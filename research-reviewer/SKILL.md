---
name: research-reviewer
description: Use when user says "review TICKER", "check note quality", "what needs review", or wants to assess research note quality.
---

# Research Note Reviewer

Review and validate research notes in `research/tickers/`.

## Review a Single Note
1. Read `research/tickers/TICKER.md`
2. Check frontmatter completeness (required: company, ticker, status, category, initiated, last_revised)
3. Check for stub indicators: "No coverage yet", text < 500 chars, missing sections
4. If `ai_conviction` exists, verify rationale makes sense
5. Flag stale notes: `last_revised` > 180 days ago

## Find Notes Needing Review
```bash
# Notes revised since last CIO review (review queue)
cd /Users/srvo/dev/monocloud && grep -l 'reviewed_at:' research/tickers/*.md | head -5
# then compare last_revised > reviewed_at

# Stale notes (>180 days)
cd /Users/srvo/dev/monocloud/research/pipeline && doppler run -- uv run python -c "
from pipeline.providers.research_store import load_universe
u = load_universe()
from datetime import datetime, timedelta
cutoff = datetime.now() - timedelta(days=180)
for t in u:
    if t.get('last_revised') and t['last_revised'] < cutoff.strftime('%Y-%m-%d'):
        print(f\"{t['ticker']:8s} score={t.get('tick_score',0):3d}  last={t['last_revised']}\")
"

# Held positions (priority review)
grep -l 'status: held' /Users/srvo/dev/monocloud/research/tickers/*.md
```

## Validate MD-DB Consistency
```bash
cd /Users/srvo/dev/monocloud/tools/ecic && doppler run -- uv run ecic research sync --dry-run
```
This shows what would change without writing. Mismatches = notes and DB out of sync.

## Quality Checklist
- [ ] Bottom Line section present and substantive
- [ ] Screening Assessment has clear pass/fail reasoning
- [ ] tick_score matches the qualitative assessment
- [ ] category is correct (Innovation/Infrastructure/Real Estate/Lending/Exclude)
- [ ] strategy matches security type (growth=stocks, income=preferreds/bonds, diversification=funds)
- [ ] Revision log has entries for recent changes
