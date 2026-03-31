---
name: workers-best-practices
description: Use when reviewing, writing, or debugging Cloudflare Workers code for production quality issues like streaming, floating promises, global state, secrets, and observability.
---

# Cloudflare Workers Best Practices

## Quick Reference Tables

| Category | Anti-Pattern | Best Practice | Pattern |
|----------|--------------|---------------|---------|
| **Streaming** | Buffer full responses | Stream early | `new ReadableStream()` |
| **Promises** | Fire-and-forget without void | Always void or await | `Promise<void>` or `await` |
| **State** | Module-level mutable state | Stateless per request | `Env` bindings only |
| **Secrets** | Hardcode in code | Environment variables | `env.SECRET` |
| **Observability** | No logging | Structured logging | `createLogger()` |
| **Error Handling** | Uncaught rejections | Always return Response | Top-level try/catch |

---

## Streaming Responses

**Rule**: Never buffer large responses — stream early for better UX.

```typescript
// ❌ BAD: Could exceed 5MB limit
const largeData = await fetchLargeData() // Promise<ArrayBuffer>
return Response.json(largeData) // Buffer entire response

// ✅ GOOD: Stream immediately
async function handleLargeStream(env: Env): Promise<Response> {
  return new Response(new ReadableStream({
    async start(controller) {
      for await (const chunk of streamFromR2(env.R2_BUCKET, 'key')) {
        controller.enqueue(chunk)
      }
      controller.close()
    }
  }), { headers: { 'Content-Type': 'application/octet-stream' } })
}
```

**When to stream**:
- Large file downloads (>1MB)
- Long-running processes with periodic updates
- SSE (Server-Sent Events)

---

## Floating Promises

**Rule**: Always void or await floating promises — never fire-and-forget.

```typescript
// ❌ BAD: Promise rejection crashes Worker
fetch('https://api.example.com')
await handleRequest()

// ✅ GOOD: Void if you don't need result
fetch('https://api.example.com').then(() => void 0)
await handleRequest()

// ✅ OPTIONAL: Wait if you need result
const result = await fetch('https://api.example.com')
await handleRequest()
```

**Pattern**: Use `.then(() => void 0)` after console warnings, free fresh promises, or log errors.

---

## Global State Pitfalls

**Rule**: Workers are ephemeral — module-level state persists across requests during warm-up but not between invocations.

```typescript
// ❌ BAD: Relies on worker-warm state
const cache = new Map() // State lost after cold start
export default {
  async fetch(request: Request, env: Env) {
    return Response.json({ cached: !cache.has(request.url) })
  }
}

// ✅ GOOD: Bindings only
export interface Env {
  CACHE_KV: KVNamespace // Persistent via KV
}

export default {
  async fetch(request: Request, env: Env) {
    const cached = await env.CACHE_KV.get(request.url)
    return Response.json({ cached: cached !== null })
  }
}
```

**Never store**: Module-level state, request-scoped computed data, or config outside `Env`.

---

## Secrets Management

**Rule**: Never hardcode secrets — use environment variables and `wrangler secret`.

```typescript
// ❌ BAD: Hardcoded credentials
const apiKey = 'sk_live_12345'
const supabaseUrl = 'https://xyz.supabase.co'

// ✅ GOOD: Environment bindings
export interface Env {
  SUPABASE_URL: string
  SUPABASE_SERVICE_ROLE_KEY: string
  OPENAI_API_KEY: string
}

export default {
  async fetch(request: Request, env: Env) {
    const analysis = await openai(env.OPENAI_API_KEY, request)
    return Response.json(analysis)
  }
}
```

**Note**: Always wrap in `doppler run --` for local development:

```bash
# Workers
doppler run -- npx wrangler deploy

# CLI hook
/bin/bash -c "cd /Users/srvo/dev/monocloud/workers/phone && doppler run -- npx wrangler deploy"
```

---

## Bindings

**Rule**: Access all external services via `env` bindings — never construct URLs manually.

| Binding Type | Access in Workers |
|--------------|-------------------|
| **D1** | `env.DB.prepare(sql).bind(...).first()` |
| **R2** | `env.R2_BUCKET.get(key)` |
| **KV** | `env.KV_NAMESPACE.get(key)` |
| **Durable Objects** | `env.MY_DO.idFromName(name).getMyStub()` |
| **Service Binding** | `env.SERVICE_NAME.fetch(url)` |

```typescript
export interface Env {
  DB: D1Database
  R2_BUCKET: R2Bucket
  MY_KV: KVNamespace
  MY_DO: DurableObjectNamespace
  MY_SERVICE: ServiceBinder
}

export default {
  async fetch(request: Request, env: Env) {
    const user = await env.DB.prepare(
      'SELECT * FROM users WHERE id = ?'
    ).bind(userId).first()

    const file = await env.R2_BUCKET.get('document.pdf')
    const cached = await env.MY_KV.get('token')

    const stub = env.MY_DO.idFromName(userId).getMyStub()
    await stub.fetch('/action', { method: 'POST' })

    // ❌ BAD: Direct R2 SDK
    const s3 = new S3Client({ endpoint: '...' })

    // ✅ GOOD: Use bindings
    const doStub = env.MY_DO.idFromName('key')
    await doStub.fetch('/path')
  }
}
```

---

## Observability

**Rule**: Always instrument workers with structured logging and PostHog events — never silent failures.

```typescript
// Import helpers
import { initObservability, createLogger } from '@monocloud/shared'

// Initialize at module level
const logger = createLogger('worker-name', 'service-tag')

export default {
  async fetch(request: Request, env: Env, ctx: ExecutionContext) {
    initObservability(env, {
      serviceName: 'my-service',
      environment: env.ENVIRONMENT,
      workerName: 'worker-name',
    })

    try {
      const result = await handleRequest(request, env)
      logger.info('Request completed', {
        status: result.status,
        path: new URL(request.url).pathname,
      })
      return result
    } catch (err) {
      logger.error('Request failed', {
        error: err instanceof Error ? err.message : String(err),
        path: new URL(request.url).pathname,
      })
      return Response.json(
        { error: 'Internal server error' },
        { status: 500 }
      )
    }
  }
}
```

**Log levels**:
- `logger.info()` — Success paths, route matches
- `logger.warn()` — Retries, sticky/cache hit (non-critical)
- `logger.error()` — Failures, uncaught exceptions

---

## Error Handling

**Rule**: Always return a Response — catch at top level.

```typescript
// ❌ BAD: Unhandled rejections crash Worker
export default {
  async fetch(request: Request) {
    const data = await fetch('https://api.example.com') // May throw
    return Response.json(data)
  }
}

// ✅ GOOD: Top-level error handling
export default {
  async fetch(request: Request) {
    try {
      const result = await handleRequest(request)
      return result
    } catch (err) {
      logger.error('Unhandled error', { error: err.message })
      return Response.json(
        { error: 'Internal server error' },
        { status: 500 }
      )
    }
  }
}
```

**Structured error response**:

```typescript
// helpers/response.ts exported from shared package
export function jsonOk<T>(data: T, extraHeaders: Record<string, string> = {}): Response {
  return Response.json(data, { status: 200, headers: extraHeaders })
}

export function jsonError(message: string, status: number = 500, extraHeaders: Record<string, string> = {}): Response {
  return Response.json({ error: message }, { status, headers: extraHeaders })
}
```

**Pattern**:

```typescript
async function handleSomePath(request: Request, env: Env): Promise<Response> {
  try {
    const data = await doWork(request)
    return jsonOk(data)
  } catch (err) {
    logger.error('Path handler failed', { error: err.message })
    return jsonError(err.message, 500)
  }
}
```

---

## CORS

**Rule**: Use `@monocloud/shared` helpers — don't manually construct CORS headers.

```typescript
import { initObservability, createLogger, handleCorsPreflight } from '@monocloud/shared'
import type { Env } from './lib/env'

const logger = createLogger('data-api', 'data-api-worker')

export default {
  async fetch(request: Request, env: Env, rng: ExecutionContext) {
    initObservability(env, {
      serviceName: 'data-api',
      environment: env.ENVIRONMENT,
      workerName: 'data-api',
    })

    // Must check preflight before routing
    const preflight = handleCorsPreflight(request)
    if (preflight) return preflight

    // ... route handling ...
  }
}
```

**Manual CORS pattern (if helpers unavailable)**:

```typescript
function buildCorsHeaders(origin: string | null = null): Record<string, string> {
  const headers: Record<string, string> = {
    'Access-Control-Allow-Origin': origin || '*',
    'Access-Control-Allow-Methods': 'GET, POST, PATCH, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Request-ID',
    'Access-Control-Max-Age': '86400',
  }

  if (origin && origin !== '*') {
    headers['Access-Control-Allow-Origin'] = origin
  }

  return headers
}

// OPTIONS preflight
if (request.method === 'OPTIONS') {
  return new Response(null, {
    headers: buildCorsHeaders(request.headers.get('origin')),
  })
}
```

---

## Request Size Limits

**Rule**: 128MB limit — plan for chunking.

```typescript
// Workers standard limit (not configurable)
const MAX_REQUEST_SIZE = 128 * 1024 * 1024 // 128MB

async function handleUpload(request: Request, env: Env): Promise<Response> {
  const contentLength = request.headers.get('Content-Length')
  const size = Number(contentLength)

  if (size > MAX_REQUEST_SIZE) {
    return Response.json(
      { error: 'Payload too large' },
      { status: 413 }
    )
  }

  // Stream file to R2 (avoid loading into memory)
  const chunks: Uint8Array[] = []
  let totalSize = 0

  const reader = request.body?.getReader()
  if (!reader) {
    return Response.json({ error: 'No body' }, { status: 400 })
  }

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    if (value.byteLength + totalSize > MAX_REQUEST_SIZE) {
      return Response.json({ error: 'Payload too large' }, { status: 413 })
    }

    chunks.push(value)
    totalSize += value.byteLength
  }

  // Write to R2
  if (chunks.length === 1) {
    await env.R2_BUCKET.put('key', chunks[0])
  } else {
    await env.R2_BUCKET.put('key', new Uint8Array(flattenChunks(chunks)))
  }

  return Response.json({ success: true })
}

function flattenChunks(chunks: Uint8Array[]): Uint8Array {
  const total = chunks.reduce((acc, chunk) => acc + chunk.byteLength, 0)
  const result = new Uint8Array(total)
  let offset = 0
  for (const chunk of chunks) {
    result.set(chunk, offset)
    offset += chunk.byteLength
  }
  return result
}
```

---

## CPU Time Limits

**Rule**: 10ms free, 30s paid. Offload heavy work.

| Task Type | Recommended Approach |
|-----------|----------------------|
| **Short processing (<10ms)** | Inline (e.g., auth check, validation) |
| **Medium processing (10ms-1s)** | Inline or queue |
| **Long processing (>1s)** | Queue (Arq) + Durable Objects |
| **Database queries** | Async via docket queue |
| **External API calls** | Queue or timeout after 5s |

```typescript
// ❌ BAD: Blocking work in request handler
export default {
  async fetch(request: Request) {
    await heavyProcessing() // May exceed 30s limit
    return Response.json({ done: true })
  }
}

// ✅ GOOD: Offload heavy work
import { handleQueue } from './queue'

export default {
  async fetch(request: Request, env: Env) {
    await handleQueue(env).processRequest(request) // Background worker handles it
    return Response.json({ processing: true })
  }
}

// ✅ WORKAROUND: Timed out external call
export default {
  async fetch(request: Request) {
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), 5000) // 5s

    try {
      const response = await fetch('https://api.example.com/slow', {
        signal: controller.signal,
      })
      clearTimeout(timeoutId)
      return Response.json(await response.json())
    } catch (err) {
      if (timeoutId) clearTimeout(timeoutId)
      logger.error('Request timed out')
      return Response.json(
        { error: 'Request timed out' },
        { status: 504 }
      )
    }
  }
}
```

**Queue pattern** (Arq):

```typescript
// workers/my-worker/src/queue.ts
import { handleQueue } from '@monocloud/workers/queue'

export const handleQueue = handleQueue({
  env: (env) => env,
  queue:
    env.TEMPORAL_QUEUE || env.ARQ_QUEUE || env.QUEUE, // Map worker bindings
})

export default {
  async fetch(request: Request, env: Env, _ctx: ExecutionContext) {
    await handleQueue(env).processRequest(request)
    return Response.json({ status: 'accepted' })
  }
}
```

---

## Common Patterns

### Structured Response Helper

```typescript
// workers/data-api/src/lib/response.ts
export function jsonOk<T>(data: T, extraHeaders: Record<string, string> = {}): Response {
  return Response.json(data, { status: 200, headers: extraHeaders })
}

export function jsonError(message: string, status: number = 500, extraHeaders: Record<string, string> = {}): Response {
  return Response.json({ error: message }, { status, headers: extraHeaders })
}

export function htmlResponse(title: string, body: string, status: number): Response {
  return new Response(
    `<!DOCTYPE html><html><head><title>${title}</title></head>
    <body><h1>${title}</h1><p>${body}</p></body></html>`,
    { status, headers: { 'Content-Type': 'text/html; charset=utf-8' } }
  )
}
```

### Router Pattern

```typescript
// workers/data-api/src/index.ts
export default {
  async fetch(request: Request, env: Env) {
    const url = new URL(request.url)
    const path = url.pathname.replace(/^\//, '').split('/').filter(Boolean)

    // Health check
    if (path.length === 0 || path[0] === 'health') {
      return Response.json({ status: 'ok' })
    }

    // Route dispatch
    if (path[0] === 'funds') {
      return handleFunds(request, env, path[1])
    }

    if (path[0] === 'clients') {
      return handleClients(request, env, path[1])
    }

    return Response.json({ error: 'not found' }, { status: 404 })
  }
}
```

### Initialization Helper

```typescript
// workers/data-api/src/index.ts
import { initObservability, createLogger, handleCorsPreflight } from '@monocloud/shared'

const logger = createLogger('data-api', 'data-api-worker')

export default {
  async fetch(request: Request, env: Env, _ctx: ExecutionContext) {
    initObservability(env, {
      serviceName: 'data-api',
      environment: env.ENVIRONMENT,
      workerName: 'data-api',
    })

    // CORS preflight
    const preflight = handleCorsPreflight(request)
    if (preflight) return preflight

    // Route handler
    const result = await handleRequest(request, env)
    logger.info('Request completed', { status: result.status })
    return result
  }
}
```

---

## Checklist Before Deploy

- [ ] No hardcoded secrets (use `env.VAR`)
- [ ] All services accessed via `env` bindings
- [ ] Stream large responses (avoid buffering)
- [ ] Floating promises voided or awaited
- [ ] Observability initialized (`initObservability`)
- [ ] Logger used for errors/warnings
- [ ] Top-level try/catch returns Response
- [ ] CORS preflight handled (`handleCorsPreflight`)
- [ ] Request size < 128MB (chunk if needed)
- [ ] Heavy work offloaded to queue/DO (CPU < 30s)
- [ ] Tests pass: `npm test` or `uv run pytest`
- [ ] Deploy: `doppler run -- npx wrangler deploy`