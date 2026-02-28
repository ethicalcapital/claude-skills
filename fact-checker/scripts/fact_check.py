#!/usr/bin/env python3
"""
fact_check.py — Deep fact-checker + edit proposer

Phase 1: Extract and classify every claim in the input text.
Phase 2: Search for evidence (SearXNG self-hosted + EXA neural, in parallel).
Phase 3: Assess each FACT claim → CONFIRMED/REFUTED/MISLEADING/NUANCED/UNVERIFIED.
Phase 4: Propose concrete edits (hyperlinks, footnotes, rewording) for anything
         that needs fixing. Output JSON for Claude to drive the approval loop.

Usage:
    # Markdown report to stdout
    cat doc.txt | doppler run -- uv run python fact_check.py

    # JSON for Claude's approval loop (pass source file so edits can reference line spans)
    doppler run -- uv run python fact_check.py --file doc.md --json

    # Save report
    doppler run -- uv run python fact_check.py --file doc.md --output report.md --verbose

Env vars (via Doppler):
    RAILWAY_SEARXNG_URL  — self-hosted SearXNG on Railway (required for search)
    EXA_API_KEY          — EXA neural search (optional, improves recall)
    ANTHROPIC_API_KEY    — Claude API (required)

Dependencies: httpx, anthropic
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from dataclasses import asdict, dataclass, field
from typing import Literal

import anthropic
import httpx

# ── Types ──────────────────────────────────────────────────────────────────

ClaimKind = Literal["FACT", "OPINION", "HEURISTIC"]
Verdict = Literal["CONFIRMED", "REFUTED", "MISLEADING", "NUANCED", "UNVERIFIED"]
Confidence = Literal["HIGH", "MEDIUM", "LOW"]
EditType = Literal["add_link", "add_footnote", "reword", "soften", "flag", "none"]


@dataclass
class Claim:
    id: int
    text: str
    kind: ClaimKind
    search_query: str | None = None


@dataclass
class Source:
    title: str
    url: str
    excerpt: str
    published_date: str | None = None
    provider: str = "searxng"


@dataclass
class ProposedEdit:
    claim_id: int
    edit_type: EditType
    original_text: str           # exact span from source document
    proposed_text: str           # replacement (may include markdown links/footnotes)
    footnote_text: str = ""      # full footnote if edit_type == "add_footnote"
    best_source_url: str = ""
    best_source_title: str = ""
    reasoning: str = ""


@dataclass
class ClaimResult:
    claim: Claim
    verdict: Verdict | None = None
    confidence: Confidence | None = None
    sources: list[Source] = field(default_factory=list)
    analysis: str = ""
    caveats: str = ""
    proposed_edit: ProposedEdit | None = None


# ── Search ──────────────────────────────────────────────────────────────────


async def searxng_search(query: str, num: int = 6) -> list[Source]:
    base_url = os.environ.get("RAILWAY_SEARXNG_URL", "").rstrip("/")
    if not base_url:
        return []
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.get(
                f"{base_url}/search",
                params={"q": query, "format": "json", "language": "en", "pageno": 1},
            )
            resp.raise_for_status()
            data = resp.json()
            return [
                Source(
                    title=r.get("title", ""),
                    url=r.get("url", ""),
                    excerpt=(r.get("content") or "")[:600],
                    published_date=r.get("publishedDate"),
                    provider="searxng",
                )
                for r in data.get("results", [])[:num]
            ]
    except Exception as e:
        print(f"  [SearXNG] {e}", file=sys.stderr)
        return []


async def exa_search(query: str, num: int = 4) -> list[Source]:
    api_key = os.environ.get("EXA_API_KEY", "")
    if not api_key:
        return []
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.post(
                "https://api.exa.ai/search",
                headers={"x-api-key": api_key, "Content-Type": "application/json"},
                json={
                    "query": query,
                    "numResults": num,
                    "contents": {"text": {"maxCharacters": 1000}},
                    "type": "neural",
                    "useAutoprompt": True,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            return [
                Source(
                    title=r.get("title", ""),
                    url=r.get("url", ""),
                    excerpt=(r.get("text") or "")[:600],
                    published_date=r.get("publishedDate"),
                    provider="exa",
                )
                for r in data.get("results", [])
            ]
    except Exception as e:
        print(f"  [EXA] {e}", file=sys.stderr)
        return []


async def search_claim(claim: Claim) -> list[Source]:
    """Parallel SearXNG + EXA for a single claim. Deduplicated by URL."""
    if not claim.search_query:
        return []
    searxng, exa = await asyncio.gather(
        searxng_search(claim.search_query),
        exa_search(claim.search_query),
    )
    seen: set[str] = set()
    merged: list[Source] = []
    for sources in (searxng, exa):
        for s in sources:
            if s.url not in seen:
                seen.add(s.url)
                merged.append(s)
    return merged


# ── LLM prompts ────────────────────────────────────────────────────────────

EXTRACTION_SYSTEM = """\
You are a precise analytical assistant. Extract every distinct claim from the
provided text and classify each one.

Claim types:
- FACT: Specific, verifiable assertion — a number, name, date, event,
  attribution, statistic, or causal claim that could in principle be confirmed
  or refuted by evidence.
- OPINION: A subjective judgment, preference, prediction, value statement, or
  interpretation that does not require third-party citation.
- HEURISTIC: A generalization or rule of thumb using language like "usually,"
  "often," "tends to," "generally," "most," "typically." Directionally
  defensible but not definitively verifiable.

Rules:
- Extract verbatim phrases from the source text where possible.
- One claim per list item — do not bundle multiple assertions.
- For FACT claims, write a precise, Googleable search query.
- Return ONLY valid JSON, no prose.
"""

EXTRACTION_SCHEMA = """\
{
  "claims": [
    {
      "id": 1,
      "text": "The exact claim, as close to verbatim as possible",
      "kind": "FACT | OPINION | HEURISTIC",
      "search_query": "search query string — or null for OPINION"
    }
  ]
}
"""

VERDICT_SYSTEM = """\
You are a rigorous fact-checker assessing a single claim against search results.

Verdict options:
- CONFIRMED: Multiple reliable sources directly support the claim.
- REFUTED: Sources contradict the claim.
- MISLEADING: Technically true but framing is selective or deceptive.
- NUANCED: Partially true with important caveats or context.
- UNVERIFIED: No reliable evidence found in either direction.

Confidence:
- HIGH: Strong, consistent evidence from multiple authoritative sources.
- MEDIUM: Some evidence, minor gaps or inconsistencies.
- LOW: Thin evidence, conflicting sources, or the claim is hard to verify.

Also propose an edit to the source text:
- CONFIRMED + good sources → add_link (hyperlink the claim text to best source)
  or add_footnote (add a citation footnote)
- REFUTED → reword (correct the claim) using best source
- MISLEADING or NUANCED → reword (add caveat) or soften (hedge the language)
- UNVERIFIED → soften (hedge) or flag ([citation needed] style)
- No change needed → none

Return ONLY valid JSON:
{
  "verdict": "CONFIRMED | REFUTED | MISLEADING | NUANCED | UNVERIFIED",
  "confidence": "HIGH | MEDIUM | LOW",
  "analysis": "1-3 sentences citing specific sources. Be direct.",
  "caveats": "Important nuances. Empty string if none.",
  "edit_type": "add_link | add_footnote | reword | soften | flag | none",
  "original_text": "verbatim span from source text to be replaced",
  "proposed_text": "replacement text (use [text](url) markdown for links, [^N] for footnotes)",
  "footnote_text": "full footnote/reference text if edit_type is add_footnote, else empty",
  "best_source_url": "URL of the most authoritative source found",
  "best_source_title": "Title of that source",
  "edit_reasoning": "one sentence: why this edit improves accuracy"
}
"""


def _strip_fence(raw: str) -> str:
    if "```" in raw:
        parts = raw.split("```")
        inner = parts[1]
        if inner.startswith("json"):
            inner = inner[4:]
        return inner.strip()
    return raw.strip()


# ── LLM calls ──────────────────────────────────────────────────────────────


def extract_claims(client: anthropic.Anthropic, text: str) -> list[Claim]:
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=EXTRACTION_SYSTEM,
        messages=[
            {
                "role": "user",
                "content": (
                    f"Extract all claims from this text.\n\n"
                    f"Return JSON matching this schema:\n{EXTRACTION_SCHEMA}\n\n"
                    f"Text:\n{text}"
                ),
            }
        ],
    )
    data = json.loads(_strip_fence(response.content[0].text))
    return [
        Claim(
            id=c["id"],
            text=c["text"],
            kind=c["kind"],
            search_query=c.get("search_query"),
        )
        for c in data["claims"]
    ]


def assess_claim(
    client: anthropic.Anthropic, claim: Claim, sources: list[Source]
) -> ClaimResult:
    source_block = "\n\n".join(
        f"[{i+1}] {s.provider.upper()} — {s.title}\nURL: {s.url}\nDate: {s.published_date or 'unknown'}\n{s.excerpt}"
        for i, s in enumerate(sources[:8])
    ) or "No search results found."

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1500,
        system=VERDICT_SYSTEM,
        messages=[
            {
                "role": "user",
                "content": f"CLAIM:\n{claim.text}\n\nSEARCH RESULTS:\n{source_block}",
            }
        ],
    )
    data = json.loads(_strip_fence(response.content[0].text))

    edit: ProposedEdit | None = None
    if data.get("edit_type", "none") != "none" and data.get("original_text"):
        edit = ProposedEdit(
            claim_id=claim.id,
            edit_type=data["edit_type"],
            original_text=data.get("original_text", claim.text),
            proposed_text=data.get("proposed_text", claim.text),
            footnote_text=data.get("footnote_text", ""),
            best_source_url=data.get("best_source_url", ""),
            best_source_title=data.get("best_source_title", ""),
            reasoning=data.get("edit_reasoning", ""),
        )

    return ClaimResult(
        claim=claim,
        verdict=data["verdict"],
        confidence=data["confidence"],
        sources=sources,
        analysis=data["analysis"],
        caveats=data.get("caveats", ""),
        proposed_edit=edit,
    )


# ── Formatters ──────────────────────────────────────────────────────────────

VERDICT_EMOJI = {
    "CONFIRMED": "✅",
    "REFUTED": "❌",
    "MISLEADING": "⚠️",
    "NUANCED": "🔶",
    "UNVERIFIED": "❓",
}

EDIT_LABEL = {
    "add_link": "Add hyperlink",
    "add_footnote": "Add footnote",
    "reword": "Reword",
    "soften": "Soften",
    "flag": "Flag",
    "none": "No change",
}


def format_markdown_report(results: list[ClaimResult]) -> str:
    lines = ["# Fact Check Report", ""]
    facts = [r for r in results if r.claim.kind == "FACT"]
    opinions = [r for r in results if r.claim.kind == "OPINION"]
    heuristics = [r for r in results if r.claim.kind == "HEURISTIC"]
    edits_needed = [r for r in facts if r.proposed_edit and r.proposed_edit.edit_type != "none"]

    if facts:
        counts = {v: sum(1 for r in facts if r.verdict == v) for v in VERDICT_EMOJI}
        parts = " · ".join(
            f"{VERDICT_EMOJI[v]} {counts[v]} {v.lower()}"
            for v in ["CONFIRMED", "REFUTED", "MISLEADING", "NUANCED", "UNVERIFIED"]
            if counts[v]
        )
        lines += [
            "## Summary",
            f"**{len(facts)} factual claims** — {parts}",
            f"**{len(edits_needed)} edits proposed** (links, footnotes, rewording)",
            f"**{len(opinions)} opinions** · **{len(heuristics)} heuristics**",
            "",
        ]

    if facts:
        lines += ["---", "", "## Factual Claims", ""]
        for r in facts:
            emoji = VERDICT_EMOJI.get(r.verdict or "UNVERIFIED", "❓")
            conf_tag = f" `{r.confidence}`" if r.confidence else ""
            lines += [
                f"### {emoji} [{r.verdict}{conf_tag}] Claim {r.claim.id}",
                f"> {r.claim.text}",
                "",
            ]
            if r.analysis:
                lines += [r.analysis, ""]
            if r.caveats:
                lines += [f"**Caveats:** {r.caveats}", ""]
            if r.proposed_edit and r.proposed_edit.edit_type != "none":
                e = r.proposed_edit
                lines += [
                    f"**Proposed edit ({EDIT_LABEL[e.edit_type]}):**",
                    f"- Before: `{e.original_text}`",
                    f"- After:  `{e.proposed_text}`",
                ]
                if e.footnote_text:
                    lines += [f"- Footnote: {e.footnote_text}"]
                if e.best_source_url:
                    lines += [f"- Source: [{e.best_source_title or e.best_source_url}]({e.best_source_url})"]
                lines += [""]
            if r.sources:
                lines += ["**Search results:**"]
                for s in r.sources[:4]:
                    date_str = f" ({s.published_date[:10]})" if s.published_date else ""
                    lines += [f"- [{s.title or s.url}]({s.url}){date_str} _{s.provider}_"]
                lines += [""]

    if opinions:
        lines += ["---", "", "## Opinions", "", "_Subjective — no citation required._", ""]
        for r in opinions:
            lines += [f"- 💭 **[{r.claim.id}]** {r.claim.text}"]
        lines += [""]

    if heuristics:
        lines += ["---", "", "## Heuristics", "", "_Arguable generalizations — defensible but not definitively citable._", ""]
        for r in heuristics:
            lines += [f"- 〜 **[{r.claim.id}]** {r.claim.text}"]
        lines += [""]

    return "\n".join(lines)


def format_json_output(
    results: list[ClaimResult],
    source_text: str,
    source_file: str | None,
) -> str:
    """Structured JSON for Claude's interactive approval loop."""
    def result_to_dict(r: ClaimResult) -> dict:
        d: dict = {
            "claim_id": r.claim.id,
            "claim_text": r.claim.text,
            "kind": r.claim.kind,
            "verdict": r.verdict,
            "confidence": r.confidence,
            "analysis": r.analysis,
            "caveats": r.caveats,
            "sources": [
                {
                    "title": s.title,
                    "url": s.url,
                    "excerpt": s.excerpt[:200],
                    "provider": s.provider,
                }
                for s in r.sources[:4]
            ],
            "proposed_edit": None,
        }
        if r.proposed_edit and r.proposed_edit.edit_type != "none":
            e = r.proposed_edit
            d["proposed_edit"] = {
                "edit_type": e.edit_type,
                "original_text": e.original_text,
                "proposed_text": e.proposed_text,
                "footnote_text": e.footnote_text,
                "best_source_url": e.best_source_url,
                "best_source_title": e.best_source_title,
                "reasoning": e.reasoning,
            }
        return d

    output = {
        "source_file": source_file,
        "total_claims": len(results),
        "edits_proposed": sum(
            1 for r in results
            if r.proposed_edit and r.proposed_edit.edit_type != "none"
        ),
        "results": [result_to_dict(r) for r in results],
    }
    return json.dumps(output, indent=2)


# ── Main ────────────────────────────────────────────────────────────────────


async def run(
    text: str,
    source_file: str | None = None,
    verbose: bool = False,
) -> tuple[list[ClaimResult], str]:
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    print("Phase 1: Extracting and classifying claims...", file=sys.stderr)
    claims = extract_claims(client, text)
    facts = [c for c in claims if c.kind == "FACT"]
    opinions = [c for c in claims if c.kind == "OPINION"]
    heuristics = [c for c in claims if c.kind == "HEURISTIC"]

    print(
        f"Found {len(claims)} claims: {len(facts)} facts, "
        f"{len(opinions)} opinions, {len(heuristics)} heuristics",
        file=sys.stderr,
    )
    if verbose:
        for c in claims:
            print(f"  [{c.kind}] {c.id}: {c.text[:80]}", file=sys.stderr)

    # Phase 2: parallel search — all fact claims fire simultaneously
    print(f"Phase 2: Parallel search for {len(facts)} factual claims...", file=sys.stderr)
    if facts:
        search_results = await asyncio.gather(*[search_claim(c) for c in facts])
        if verbose:
            for c, srcs in zip(facts, search_results):
                print(f"  Claim {c.id}: {len(srcs)} sources", file=sys.stderr)
    else:
        search_results = []

    # Phase 3 + 4: assess + propose edit (sequential to respect rate limits)
    print("Phase 3: Assessing claims and proposing edits...", file=sys.stderr)
    results: list[ClaimResult] = []
    for claim, sources in zip(facts, search_results):
        if verbose:
            print(f"  [{claim.id}] {claim.text[:60]}...", file=sys.stderr)
        result = assess_claim(client, claim, sources)
        results.append(result)

    # Non-fact claims — no verdict, no edit
    for c in opinions:
        results.append(ClaimResult(claim=c))
    for c in heuristics:
        results.append(ClaimResult(claim=c))

    results.sort(key=lambda r: r.claim.id)
    return results, text


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fact-checker + edit proposer: SearXNG + EXA + Claude",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("text", nargs="?", help="Text to fact-check")
    parser.add_argument("--file", "-f", help="Read text from file")
    parser.add_argument("--output", "-o", help="Write report/JSON to file")
    parser.add_argument(
        "--json", action="store_true",
        help="Output structured JSON for Claude's approval loop (default: markdown)"
    )
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    source_file: str | None = None
    if args.file:
        source_file = args.file
        text = open(args.file).read()
    elif args.text:
        text = args.text
    elif not sys.stdin.isatty():
        text = sys.stdin.read()
    else:
        parser.print_help()
        sys.exit(1)

    results, original = asyncio.run(run(text.strip(), source_file=source_file, verbose=args.verbose))

    if args.json:
        output = format_json_output(results, original, source_file)
    else:
        output = format_markdown_report(results)

    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"Saved to {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
