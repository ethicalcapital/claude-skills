---
name: pipeline-runner
description: Use when user says "run the pipeline", "research TICKER", "run pipeline for X", or wants to kick off research processing.
---

# Pipeline Runner

Runs the research pipeline for one or more tickers.

## Single Ticker
```bash
cd /Users/srvo/dev/monocloud/research/pipeline && unset PYTHONPATH && doppler run -- uv run python -m pipeline --ticker BSRR
```

## Full Batch (by tier, with cost ceiling)
```bash
cd /Users/srvo/dev/monocloud/research/pipeline && unset PYTHONPATH && doppler run -- uv run python -m pipeline --by-tier --max-cost 20.0
```

## Resume a Batch
```bash
cd /Users/srvo/dev/monocloud/research/pipeline && unset PYTHONPATH && doppler run -- uv run python -m pipeline --by-tier --resume-from TICKER
```

## After Pipeline Completes
1. Review the batch summary printed to stdout
2. Sync markdown to DB: `cd /Users/srvo/dev/monocloud/tools/ecic && doppler run -- uv run ecic research sync`
3. Commit remaining notes: `git add research/tickers/ && git commit -m "research: pipeline batch $(date +%Y-%m-%d)"`
4. Push: `git push`

## Key Facts
- Auto-syncs to DB + git commits every 25 notes during batch runs
- Cost tracking is live via DeepInfra pricing API
- Budget tiers: full (tick>=10), comprehensive (5-9), moderate (1-4), maintenance (<=0)
- Models: DeepSeek-V3.2 (fast), Kimi-K2 (smart), GLM-5 (final)
- ~$0.01 per ticker, ~$13-16 for full universe
- `unset PYTHONPATH` is required (prevents venv conflicts)
