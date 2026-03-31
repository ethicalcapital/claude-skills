---
name: typeset-pdf
description: Use when generating PDFs, typesetting compliance documents, rendering markdown to PDF, creating client agreements, producing Form ADV brochures, or any request involving PDF export from the repo. Triggers on "generate PDF", "typeset", "render to PDF", "export PDF", "create PDF", "print-ready".
---

# Typeset PDF

Generate branded ECIC PDFs from markdown or Typst source using the `report_writer/` toolkit.

## Quick Start

```bash
cd /Users/srvo/dev/monocloud/report_writer

# Markdown → PDF (most common)
uv run python cli.py from-md INPUT.md -o OUTPUT.pdf
uv run python cli.py from-md INPUT.md --template agreement -o OUTPUT.pdf

# Typst → PDF (direct, for custom layouts)
uv run python cli.py compile INPUT.typ -o OUTPUT.pdf
```

## Template Selection

| Template | Flag | Use For |
|----------|------|---------|
| `compliance` (default) | `--template compliance` | Form ADV, Code of Ethics, annual reviews, policies, regulatory filings |
| `agreement` | `--template agreement` | Client agreements, engagement letters, any doc needing signatures |

## Markdown Frontmatter

Add YAML frontmatter to control the cover page and template:

```yaml
---
title: Investment Advisory Agreement
subtitle: Ethical Capital LLC
date: Updated March 2026
author: Sloane Ortel, CCO
last_updated: March 17, 2026
template: agreement
---
```

All fields are optional. Without frontmatter, the first `# Heading` becomes the title.

## Automatic Page Breaks

The converter forces page breaks before headings that start with:
- `ADDENDUM`
- `SCHEDULE`
- `EXHIBIT`
- `APPENDIX`
- `CLIENT SIGNATURES`

## Signature Tables

Use markdown tables instead of underscore lines for signature fields:

```markdown
| | Client | Joint Account Holder |
| --- | --- | --- |
| Signature | | |
| Date | | |
| Printed Name | | |
```

For firm signatures:

```markdown
| | |
| --- | --- |
| Signature | |
| Name | |
| Title | Chief Compliance Officer |
| Date | |
```

## Cover Page

Every document gets a branded cover page with:
- Purple band (top ~38%, golden ratio) with ETHICAL logo
- Title and subtitle below
- Date line
- Address and contact info in lower third

Skip the cover with Typst: set `show-cover: false` in the template call.

## Writing Typst Directly

For documents needing custom layout beyond what markdown provides, write Typst directly:

```typst
#import "templates/compliance-doc.typ": *

#show: compliance-doc.with(
  title: "Form ADV Part 2A",
  subtitle: "Ethical Capital LLC",
  date: "March 2026",
  last-updated: "March 17, 2026",
  show-toc: true,
)

= Advisory Business

Body text here. Use `#quote[...]` for blockquotes.
Use `#triple-line()` sparingly (cover page only).
Use `#signature-block()` or `#dual-signature()` for signatures.
```

## Available Typst Components

From `ecic.typ` (imported by all templates):
- `#triple-line()` — lavender editorial divider (cover page only)
- `#signature-block(label, name-label, title-label, date-label)` — single sig block
- `#dual-signature(left-label, right-label)` — side-by-side client + adviser

From `agreement.typ`:
- `#party-header(party-a-name, party-a-detail, party-b-name, party-b-detail)`
- `#schedule-header(label, title)` — starts new page with centered header

## Brand Tokens

Colors load at runtime from `packages/design-tokens/src/tokens.css`. If the design system changes, PDFs pick up the new values automatically. No hardcoded colors in templates.

## Iterative Refinement

After generating a PDF, **always show Sloane the output** and iterate. This is not optional.

1. **Generate** the PDF and report page count
2. **Show** key pages: cover, first content page, signature/addendum pages
3. **Ask** what to adjust — Sloane will catch issues you won't (spacing, tone, visual weight)
4. **Fix and regenerate** — most fixes are markdown content edits, not template changes
5. **Repeat** until Sloane approves

Common refinement requests:
- "That heading should be on its own page" → add the heading prefix to the page-break list in `md_convert.py`
- "Remove bold from that paragraph" → strip `**...**` in the markdown source
- "Tables need more room" → add empty rows in the markdown table
- "Text is italic/grey when it shouldn't be" → usually a bold/italic delimiter mismatch in the source markdown
- "Cover page needs X" → edit `cover-page()` in `ecic.typ`

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Bold paragraph renders as grey italic | Remove `**...**` wrapping from long paragraphs — the converter mishandles multi-line bold |
| `$` or `@` in text causes compile error | The converter escapes these automatically, but check the `.debug.typ` file if compilation fails |
| Underscore fill-in lines (`____`) look unprofessional | Use markdown tables instead (see Signature Tables above) |
| Addendum doesn't start on new page | Heading must start with ADDENDUM/SCHEDULE/EXHIBIT/APPENDIX (case-insensitive) |
| Cover page is blank | Add YAML frontmatter with at least `title:` |
