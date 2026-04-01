---
name: deploy-worker
description: Use when user says "deploy forms", "deploy admin-api", "deploy WORKER", "ship it", or wants to push a Cloudflare worker to production.
---

# Deploy Cloudflare Worker

## Deploy a Specific Worker
```bash
cd /Users/srvo/dev/monocloud/workers/WORKER_NAME && doppler run -- npx wrangler deploy
```

## Active Workers
- `altruist` — Custodian OAuth + account sync
- `data-api` — Public API for website (ethicic.com)
- `phone` — Vonage voicemail + call routing
- `webhooks` — Inbound webhook router (GitHub, Zoho, Resend)
- `website` — Astro SSR site (ethicic.com)

## Pre-Deploy Checklist
1. Run tests: `cd workers/WORKER_NAME && npm test`
2. Check for TypeScript errors: `npx tsc --noEmit`
3. Review wrangler.toml for correct bindings
4. Deploy: `doppler run -- npx wrangler deploy`
5. Check logs: `doppler run -- npx wrangler tail`

## Tail Logs After Deploy
```bash
cd /Users/srvo/dev/monocloud/workers/WORKER_NAME && doppler run -- npx wrangler tail
```

## Rollback
```bash
# List recent deployments
cd /Users/srvo/dev/monocloud/workers/WORKER_NAME && doppler run -- npx wrangler deployments list
# Rollback to previous
cd /Users/srvo/dev/monocloud/workers/WORKER_NAME && doppler run -- npx wrangler rollback
```

## Website Deploy (Special Case)
Website uses environment-specific deploys:
```bash
# Staging (auto-deploys on push to main via CI)
cd /Users/srvo/dev/monocloud/website && doppler run -- npx wrangler deploy

# Production (manual)
cd /Users/srvo/dev/monocloud/website && doppler run -- bash -c 'npx astro build && npx wrangler deploy --env production'
```

## For observability, binding inspection, metrics, and debugging
Use the `workers-observability` skill.
