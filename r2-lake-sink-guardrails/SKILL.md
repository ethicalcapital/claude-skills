---
name: r2-lake-sink-guardrails
description: Use when touching R2 sinks (read/write/list/reconcile/archive/mirror), adding R2 clients, or changing env wiring for bucket access. Triggers on R2_ENDPOINT, R2_CATALOG_*, R2_LAKE_*, create_r2_client(), and any pipeline that reads or writes object keys.
---

# R2 Lake Sink Guardrails

## Overview

Monocloud’s default stance is **lake-first**: use `R2_LAKE_*` credentials via shared client helpers, with fallback behavior handled centrally.

This skill prevents drift back to ad-hoc env wiring and keeps R2 handling consistent across scripts, workers, and pipelines.

## When to Use

Use this skill when work includes any of:

- new R2 access code (boto3/s3 client creation)
- edits to `create_r2_client(...)` call sites
- ingestion/reconcile/export/mirror jobs touching object keys
- environment variable changes involving `R2_*`
- bugfixes in R2 request/auth/endpoint behavior

## Required Rules

1. **Use shared client first**
   - Prefer `from monocloud_storage.r2 import create_r2_client`
   - Prefer `create_r2_client()` defaults unless there is a documented, intentional non-lake target.

2. **Lake-first env resolution**
   - Treat `R2_LAKE_ENDPOINT`, `R2_LAKE_ACCESS_KEY_ID`, `R2_LAKE_SECRET_ACCESS_KEY` as canonical.
   - Do not hardcode `R2_CATALOG_*` in new code unless explicitly required by non-lake routing.

3. **No secret leakage while validating**
   - Never print secret values.
   - Validate presence with length-only checks (presence + len), not value echo.

4. **Centralize fallbacks**
   - Keep alias/fallback logic in shared helpers, not duplicated in each pipeline script.
   - If a fallback is needed, add it once in shared code and consume it everywhere.

## Preferred Pattern

```python
from monocloud_storage.r2 import create_r2_client

# Lake-first via shared defaults
s3 = create_r2_client()
```

## Anti-Patterns

```python
# ❌ Avoid pinning catalog env vars at callsite unless explicitly needed
s3 = create_r2_client(
    endpoint_env="R2_CATALOG_ENDPOINT",
    access_key_env="R2_CATALOG_ACCESS_KEY_ID",
    secret_key_env="R2_CATALOG_SECRET_ACCESS_KEY",
)
```

```python
# ❌ Avoid per-script boto3 env wiring copies
boto3.client(
    "s3",
    endpoint_url=os.environ["R2_CATALOG_ENDPOINT"],
    aws_access_key_id=os.environ["R2_CATALOG_ACCESS_KEY_ID"],
    aws_secret_access_key=os.environ["R2_CATALOG_SECRET_ACCESS_KEY"],
)
```

## PR/Review Checklist

- [ ] Uses `create_r2_client()` from shared package
- [ ] Lake-first env behavior preserved
- [ ] No new direct `os.environ["R2_CATALOG_..."]` unless justified
- [ ] No secret values printed/logged
- [ ] R2 key path intent documented (bucket/prefix/retention expectations)
- [ ] Dry-run or safe verification command captured in notes

## Notes

If a job truly must target a non-lake endpoint, add a short rationale in code comments and in the runbook/plan so future agents do not “normalize” it back by accident.
