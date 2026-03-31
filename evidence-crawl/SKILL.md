---
name: evidence-crawl
description: Use when writing exclusion reason_detail narratives and you need to gather source material — reads from R2 evidence archive and Qdrant semantic search first, falls back to crawl4ai or Keiro Drift only when local sources are insufficient. Also use when asked to "crawl this URL", "fetch that page", or "store evidence". If context is still insufficient after local search, writes a review_note flagging what's missing rather than speculating.
---

# Evidence Consolidation & Crawl

The primary job is **consolidating evidence that already exists locally** into reason_detail narratives. Most exclusion records already have crawled evidence in R2 and/or indexed chunks in Qdrant. Start there.

## Workflow

```
1. Read existing evidence from R2 (by ticker + evidence_url)
2. Search Qdrant exclusion_evidence collection (semantic, by ticker)
3. Check the DB record's existing reason_detail, evidence_url, evidence_citation
4. If sufficient → write the reason_detail narrative (use writing-exclusions skill)
5. If insufficient → flag via review_note, do NOT speculate
6. Only crawl new URLs or kick off Keiro Drift when explicitly asked
```

## Step 1: Read Local Evidence

### From R2 (previously crawled pages)

```python
from monocloud_storage.evidence import EvidenceStore, r2_key_for

store = EvidenceStore()

# Read by ticker + URL
markdown = store.read_from_r2("ORCL", "https://bdsmovement.net/...")

# Compute R2 key without I/O
key = r2_key_for("ORCL", "https://bdsmovement.net/...")
# → "exclusion_evidence/ORCL/bdsmovement_net_0a342ac9cf9255b8.md"
```

### From Qdrant (semantic search over all crawled evidence)

```python
from qdrant_client import QdrantClient
from monocloud_search import get_embedding

client = QdrantClient(url=os.environ.get("QDRANT_URL", "http://localhost:6333"))
vec = get_embedding("Oracle occupied territories settlement")
results = client.search(
    collection_name="exclusion_evidence",
    query_vector=vec,
    query_filter={"must": [{"key": "ticker", "match": {"value": "ORCL"}}]},
    limit=5,
)
for r in results:
    print(r.payload["url"], r.payload["chunk_text"][:200])
```

### From the DB record itself

The `evidence_url`, `evidence_citation`, `reason_detail`, and `notes` fields on `exclusions.active_exclusions` often contain enough context to write a narrative without crawling anything.

## Step 2: Flag Gaps (Don't Speculate)

If local evidence is insufficient to write a confident reason_detail, update the record's `review_note` to flag what's missing:

```sql
UPDATE exclusions.active_exclusions SET
  review_note = 'Insufficient evidence for narrative: need primary source confirming [specific claim]. R2 has [X] but missing [Y].',
  review_status = 'needs_cio_review'
WHERE id = '<uuid>';
```

Do NOT:
- Invent facts to fill gaps
- Write vague narratives to cover for missing evidence
- Kick off web research without being asked

## Step 3: Crawl New URLs (Only When Asked)

### WebFetch first (static pages)

Use the WebFetch tool directly. If empty/garbled, fall back to crawl4ai.

### crawl4ai (JS-rendered pages)

```python
import httpx, os

resp = httpx.post(
    f"{os.environ['RAILWAY_CRAWL4AI_URL']}/crawl",
    headers={
        "Authorization": f"Bearer {os.environ['RAILWAY_CRAWL4AI_API_TOKEN']}",
        "Content-Type": "application/json",
    },
    json={
        "urls": ["https://example.com"],
        "browser_config": {"headless": True},
        "crawler_config": {
            "cache_mode": "bypass",
            "word_count_threshold": 20,
            "excluded_tags": ["nav", "footer", "aside", "header", "script", "style", "form"],
        },
    },
    timeout=60,
)
markdown = resp.json()["results"][0]["markdown"]["fit_markdown"]
```

### Store to R2

```python
store = EvidenceStore()
result = store.crawl_and_store("ORCL", "https://bdsmovement.net/...", "occupied_territories")
```

R2 key: `exclusion_evidence/{ticker}/{domain_slug}_{url_hash}.md`

### Keiro Drift (deep research, only when explicitly requested)

```python
from monocloud_research.keiro_drift import DriftClient

drift = DriftClient()
result = drift.research("Oracle Corp occupied territories")

for source in result.sources:
    store.store_content(
        symbol="ORCL", url=source.url,
        sub_category_code="occupied_territories",
        content=source.content,
    )
```

## Batch Ingestion

```bash
doppler run -- uv run python scripts/crawl_evidence_to_r2_qdrant.py [--dry-run] [--limit N] [--skip-qdrant]
```

## Proxy (Blocked Sites)

Pass Mullvad SOCKS5 per-request when rawls IP is blocked:

```python
"crawler_config": {
    "proxy_config": {"server": "socks5://ACCT:mullvad@us-nyc-001.socks5.mullvad.net:1080"},
}
```

## Required Env Vars

| Var | What |
|-----|------|
| `RAILWAY_CRAWL4AI_URL` | `https://crawl.ec1c.com` |
| `RAILWAY_CRAWL4AI_API_TOKEN` | Bearer auth |
| `CF_ACCESS_CLIENT_ID` / `CF_ACCESS_CLIENT_SECRET` | Service token for `*.ec1c.com` |
| `R2_ENDPOINT_URL` / `R2_ACCESS_KEY_ID` / `R2_SECRET_ACCESS_KEY` | R2 evidence storage |
| `KEIRO_API_KEY` | Keiro Drift (only when doing new research) |
| `DEEPINFRA_API_KEY` | Embedding for Qdrant |

All in Doppler (project: `rawls`, env: `dev`). Run with `doppler run --`.
