---
name: workers-observability
description: Use when checking worker health, inspecting bindings (KV/R2/D1), viewing worker metrics, debugging production errors, or auditing Cloudflare infrastructure costs. Replaces the cloudflare-observability and cloudflare-bindings MCPs.
---

# Cloudflare Workers Observability & Binding Management

Replaces the remote `cloudflare-observability` and `cloudflare-bindings` MCP servers with direct CLI + API access.

## Prerequisites

All commands require Doppler for credentials:
```bash
doppler run -- <command>
```

Key secrets: `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_KEY_MASTER` (can create tokens), `CF_ACCOUNT_ID` (if set).

Account ID can be read from any worker's `wrangler.toml` or via:
```bash
doppler run -- npx wrangler whoami
```

## Quick Health Check

### List all deployed workers
```bash
doppler run -- npx wrangler deployments list --config workers/WORKER_NAME/wrangler.toml
```

### Tail live logs (structured JSON)
```bash
doppler run -- npx wrangler tail WORKER_NAME --format json | head -50
```

### Tail with error filter
```bash
doppler run -- npx wrangler tail WORKER_NAME --format json --status error | head -20
```

### Check worker status via API
```bash
doppler run -- bash -c 'curl -s -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  "https://api.cloudflare.com/client/v4/accounts/$CF_ACCOUNT_ID/workers/scripts" | jq ".result[] | {id, modified_on}"'
```

## Binding Inspection

### KV Namespaces — list all
```bash
doppler run -- bash -c 'curl -s -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  "https://api.cloudflare.com/client/v4/accounts/$CF_ACCOUNT_ID/storage/kv/namespaces" | jq ".result[] | {id, title}"'
```

### KV — list keys in a namespace
```bash
doppler run -- bash -c 'curl -s -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  "https://api.cloudflare.com/client/v4/accounts/$CF_ACCOUNT_ID/storage/kv/namespaces/NAMESPACE_ID/keys?limit=100" | jq ".result"'
```

### KV — read a specific key
```bash
doppler run -- bash -c 'curl -s -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  "https://api.cloudflare.com/client/v4/accounts/$CF_ACCOUNT_ID/storage/kv/namespaces/NAMESPACE_ID/values/KEY_NAME"'
```

### R2 Buckets — list all
```bash
doppler run -- bash -c 'curl -s -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  "https://api.cloudflare.com/client/v4/accounts/$CF_ACCOUNT_ID/r2/buckets" | jq ".result.buckets[] | {name, creation_date}"'
```

### R2 — list objects in a bucket (prefix filter)
```bash
doppler run -- npx wrangler r2 object list BUCKET_NAME --prefix "some/prefix/"
```

### Secrets — list (names only, never values)
```bash
doppler run -- npx wrangler secret list --config workers/WORKER_NAME/wrangler.toml
```

## Metrics & Analytics

### Worker analytics (last 24h)
```bash
doppler run -- bash -c 'curl -s -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"{ viewer { accounts(filter: {accountTag: \\\"$CF_ACCOUNT_ID\\\"}) { workersInvocationsAdaptive(limit: 10, filter: {datetime_geq: \\\"$(date -u -v-1d +%Y-%m-%dT%H:%M:%SZ)\\\", datetime_leq: \\\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\\\"}, orderBy: [sum_requests_DESC]) { sum { requests errors subrequests } dimensions { scriptName status } } } } }\"}" \
  "https://api.cloudflare.com/client/v4/graphql" | jq ".data.viewer.accounts[0].workersInvocationsAdaptive"'
```

### CPU time analytics
```bash
doppler run -- bash -c 'curl -s -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"{ viewer { accounts(filter: {accountTag: \\\"$CF_ACCOUNT_ID\\\"}) { workersInvocationsAdaptive(limit: 10, filter: {datetime_geq: \\\"$(date -u -v-1d +%Y-%m-%dT%H:%M:%SZ)\\\"}) { quantiles { cpuTimeP50 cpuTimeP99 } dimensions { scriptName } } } } }\"}" \
  "https://api.cloudflare.com/client/v4/graphql" | jq ".data.viewer.accounts[0].workersInvocationsAdaptive"'
```

## Deployed Workers

Current production workers in `workers/`:
- `altruist` — Custodian OAuth + account sync
- `data-api` — Public API for website (ethicic.com)
- `phone` — Vonage voicemail + call routing
- `webhooks` — Inbound webhook router (GitHub, Zoho, Resend)
- `website` — Astro SSR site (ethicic.com)

## Known Bindings

| Worker | Binding | Type | Purpose |
|--------|---------|------|---------|
| data-api | RATE_LIMIT_KV | KV | Rate limiting |
| data-api | LAKE_BUCKET | R2 | Form uploads, client PDFs |
| altruist | ALTRUIST_TOKENS | KV | OAuth token cache |

## Debugging Playbook

1. **"Worker is returning 500s"**
   - Tail logs with error filter (see above)
   - Check CPU time — if near 30s, it's hitting the limit
   - Check recent deployments for bad deploy

2. **"KV reads are slow/missing"**
   - List keys to verify the key exists
   - Check if the namespace ID in wrangler.toml matches production
   - Verify the binding name matches code (`env.RATE_LIMIT_KV`)

3. **"R2 uploads failing"**
   - Check bucket exists and permissions
   - Verify CORS config on the bucket
   - Check object size limits (Workers free: 25MB, paid: 500MB per request)

4. **"Costs spiking"**
   - Run worker analytics query to find hot workers
   - Check KV write volume (rate limiter can be write-heavy)
   - Look for retry loops in tail output
