---
name: monocloud-maintenance
description: Use when Cloudflare costs are high, workers burning usage, or user reports infrastructure cleanup needs - audits deployed workers vs codebase, identifies zombie infrastructure, and optimizes AI/KV usage in monocloud repository
---

# Monocloud Infrastructure Maintenance

## Overview

Systematic cleanup of monocloud's Cloudflare infrastructure to eliminate zombie workers, orphaned KV namespaces, and optimize AI/KV usage that drive costs.

**Core principle:** Deployed workers drift from codebase over time. Regular audits prevent zombie infrastructure from burning budget.

## When to Use

**Use this skill when:**
- User reports high Cloudflare costs
- RTN (AI inference) or KV write costs are excessive
- Workers are "burning usage" but user doesn't know which ones
- Need to audit what's actually deployed vs what's in codebase
- Suspecting zombie workers from deleted code

**Don't use for:**
- Initial monocloud setup
- Adding new workers (use standard deployment)
- Performance optimization (different skill)

## Zombie Worker Symptoms

**Common signs:**
- Cloudflare bill doesn't match expected usage
- Workers exist in API but not in `workers/` directory
- Production/staging variants (`-production`, `-smoke`) for deleted features
- KV namespaces with names not in any wrangler.toml
- Old project names in worker list (divest, matrix, haraway, triage)

## Audit Workflow

### 1. List All Deployed Workers

```bash
doppler run -- bash -c 'curl -s -X GET \
  "https://api.cloudflare.com/client/v4/accounts/${CLOUDFLARE_ACCOUNT_ID}/workers/scripts" \
  -H "Authorization: Bearer ${CLOUDFLARE_API_TOKEN}" | jq -r ".result[] | .id"'
```

**Expected workers (current monocloud):**
- Core pipeline: `forms`, `ingest`, `process`, `enrich`, `dlq-handler`
- Sites: `site-production`, `srvo-site`
- Special: `dryvest` (keep always)

### 2. Cross-Reference with Codebase

```bash
# List workers in codebase
ls workers/

# Find wrangler.toml worker names
grep -r "^name = " workers/*/wrangler.toml
```

**Red flags:**
- Worker deployed but no `workers/[name]/` directory
- Worker name has `-production` or `-smoke` suffix but base doesn't exist
- Old project names (portql, workbench, triage, matrix, haraway)

### 3. Check Deployment Dates

```bash
doppler run -- npx wrangler deployments list --name [worker-name] 2>&1 | head -10
```

**Zombie indicators:**
- Deployed recently but directory doesn't exist (deployed before deletion)
- Has service bindings to other deleted workers
- No routes configured (orphaned background worker)

### 4. Audit KV Namespaces

```bash
doppler run -- bash -c 'curl -s -X GET \
  "https://api.cloudflare.com/client/v4/accounts/${CLOUDFLARE_ACCOUNT_ID}/storage/kv/namespaces" \
  -H "Authorization: Bearer ${CLOUDFLARE_API_TOKEN}" | jq -r ".result[] | \"\(.id) - \(.title)\""'
```

**Cross-reference with wrangler.toml:**
```bash
grep -r "kv_namespaces" workers/*/wrangler.toml
```

**Orphans to delete:**
- KV namespaces not referenced in ANY wrangler.toml
- Names matching deleted workers (matrix-*, haraway-*, FEEDBACK, HOOKS if unused)
- Preview variants (`*_preview`) for deleted workers

## Safe Deletion Protocol

**CRITICAL: Always confirm with user before deleting site workers (site-production, srvo-site, etc)**

### Delete Zombie Workers

```bash
# Delete worker
doppler run -- npx wrangler delete --name [worker-name] --force

# If fails due to queue binding, delete queue first
echo "yes" | doppler run -- npx wrangler queues delete [queue-name]
doppler run -- npx wrangler delete --name [worker-name] --force
```

### Delete Orphaned KV Namespaces

```bash
doppler run -- bash -c 'curl -s -X DELETE \
  "https://api.cloudflare.com/client/v4/accounts/${CLOUDFLARE_ACCOUNT_ID}/storage/kv/namespaces/[KV_ID]" \
  -H "Authorization: Bearer ${CLOUDFLARE_API_TOKEN}" | jq -r ".success"'
```

### Verify Deletion

```bash
# List remaining workers
doppler run -- bash -c 'curl -s -X GET \
  "https://api.cloudflare.com/client/v4/accounts/${CLOUDFLARE_ACCOUNT_ID}/workers/scripts" \
  -H "Authorization: Bearer ${CLOUDFLARE_API_TOKEN}" | jq -r ".result[] | .id"'

# List remaining KV namespaces
doppler run -- bash -c 'curl -s -X GET \
  "https://api.cloudflare.com/client/v4/accounts/${CLOUDFLARE_ACCOUNT_ID}/storage/kv/namespaces" \
  -H "Authorization: Bearer ${CLOUDFLARE_API_TOKEN}" | jq -r ".result[] | .title"'
```

## AI Usage Optimization

**Primary source:** `enrich` worker uses Workers AI for email classification

### Check AI Usage Patterns

```bash
# Check enrich worker code for AI calls
grep -r "env.AI.run" workers/enrich/src/
```

**Current AI usage (workers/enrich/src):**
- `hitl-email-scorer.ts`: Email classification (EVERY email)
- `index.ts`: Transcript analysis (client matching)
- `re-analyzer.ts`: Re-scoring pending reviews (cron job)

### Cost Reduction Strategies

**1. Add Simple Heuristics First (60-70% reduction)**
```typescript
// Before calling AI, check simple rules
if (email.from.includes('noreply@') || email.from.includes('marketing@')) {
  return { classification: 'marketing', confidence: 0.9, skip_ai: true };
}
```

**2. Cache Common Classifications (KV or D1)**
- Cache sender classifications for repeat emails
- Check cache before AI call

**3. Reduce Cron Frequency**
```toml
# Change from hourly to daily
[triggers]
crons = ["0 9 * * *"]  # Daily at 9:00 AM
```

**4. Use Smaller/Cheaper Models**
- Switch from `mistral-small-3.1-24b` to `llama-3.2-1b-instruct`
- Trade-off: slightly lower accuracy

## KV Write Optimization

**Primary sources:** `forms` worker rate limiting, zombie workers

### Identify KV Write Sources

```bash
# Find all KV usage in workers
grep -r "RATE_LIMIT_KV\|KV" workers/*/src/ --include="*.ts"
```

### Rate Limiting Optimization

**Current:** 1-hour TTL = frequent writes for repeat visitors

```typescript
// Increase TTL to reduce writes
await env.RATE_LIMIT_KV.put(rateLimitKey, String(currentCount + 1), {
  expirationTtl: 86400,  // 24 hours instead of 3600 (1 hour)
});
```

**Savings:** 24x reduction in writes for repeat visitors

### Alternative: Durable Objects

Replace KV rate limiting with Durable Objects (included storage, better atomicity):
- Better for high-frequency writes
- No eventually-consistent issues
- Lower cost at scale

## Site Worker Recovery

**CRITICAL:** If you accidentally delete site workers, they MUST be restored immediately.

### Restore srvo-site

```bash
cd /Users/srvo/srvo-site
doppler run -- npx wrangler deploy
```

**Route:** `srvo.org/*`

### Restore site-production (ethicic.com)

```bash
cd /Users/srvo/ethicic.com

# First, fix wrangler.toml if it references deleted workers
# Remove tail_consumers and service bindings to deleted workers

doppler run -- npx wrangler deploy
```

**Route:** `ethicic.com` (main site)

**Service bindings to preserve:**
- `forms` - Client form submissions

**Service bindings to remove (if deleted):**
- `site-tail` - Logging worker (if deleted)
- `workbench-api-production` - Old API (if deleted)

## Common Mistakes

### ❌ Deleting Workers Without Checking Routes
**Fix:** Always check deployment info first:
```bash
doppler run -- npx wrangler deployments list --name [worker-name] | grep -E "routes|pattern"
```

### ❌ Assuming Deleted Code = Deleted Worker
**Reality:** Workers persist until explicitly deleted via API/wrangler

### ❌ Not Tracking Deleted Workers
**Fix:** Document what you delete and why (git commit message or notes)

### ❌ Ignoring Service Bindings
**Reality:** Deleting a worker that other workers depend on breaks the dependent workers

**Fix:** Check service bindings first:
```bash
grep -r "service = \"[worker-name]\"" workers/*/wrangler.toml
```

## Verification Checklist

After cleanup, verify:

- [ ] All remaining workers have corresponding `workers/[name]/` directory
- [ ] No zombie workers in Cloudflare API
- [ ] All KV namespaces referenced in at least one wrangler.toml
- [ ] Site workers (site-production, srvo-site) are still live
- [ ] Core pipeline (forms → ingest → process → enrich → dlq-handler) intact
- [ ] No orphaned queues
- [ ] Cron schedules optimized (daily instead of hourly where appropriate)

## Expected State After Cleanup

**Workers (8 total):**
1. forms - Client form submissions
2. ingest - Email routing
3. process - Queue consumer
4. enrich - AI enrichment (daily cron)
5. dlq-handler - Error recovery
6. dryvest - (special, always keep)
7. srvo-site - Personal site
8. site-production - ethicic.com

**KV Namespaces (3 max):**
1. RATE_LIMIT_KV - Forms rate limiting
2. UPTIMEFLARE_STATE - Uptime monitoring (if uptime-status deployed)
3. HOOKS - Unknown purpose (check before deleting)

**Queues:**
1. raw-ingestion-queue - Forms/ingest → process
2. enrichment-queue - Process → enrich
3. failed-ingestion-dlq - Error recovery

## Cost Impact Estimation

**Before cleanup:**
- 15-20 deployed workers
- 10+ KV namespaces
- Hourly cron jobs

**After cleanup:**
- 6-8 active workers (60-70% reduction)
- 3 KV namespaces (70% reduction)
- Daily cron jobs (95% reduction in cron invocations)

**Expected savings:** 40-60% reduction in Cloudflare bill

## Real-World Impact

**Session 2025-11-02:**
- Deleted 13 zombie workers (portql, workbench, triage, divest, site variants)
- Deleted 8 orphaned KV namespaces (matrix-*, haraway-*, FEEDBACK)
- Reduced enrich cron from hourly to daily (95% reduction)
- Restored accidentally deleted site workers (srvo-site, site-production)
- KV writes dropped from 1.3M/month (mostly from zombies) to expected normal levels
