---
skill: beads-issue-tracking
description: Beads-first issue tracking with bv graph-aware triage and Linear sync. MUST READ before issue/backlog triage, creating/updating work items, or selecting next tasks.
version: 1.0.0
---

# Beads Issue Tracking

Beads is the authoritative issue surface for agent execution in this repo. Linear is a mirror/sync target; agents should start from Beads and use `br`/`bd` for mutations.

## Core rules

- Use `br` (or `bd`) for issue mutations. Do **not** manually edit `.beads/issues.jsonl`.
- Never run bare `bv` in an agent session; it opens an interactive TUI and can block. Use `bv --robot-*` flags.
- `.beads/issues.jsonl`, `.beads/config.yaml`, `.beads/metadata.json`, `.beads/README.md`, `.beads/hooks/`, and `.beads/linear-history/` are git-tracked project state.
- `.beads/embeddeddolt/`, locks, sockets, backups, credentials, and sync state are local runtime files and stay ignored.
- For Linear access, wrap commands in BWS (`bws run -- ...`) and never print secrets.

## Start-of-work triage

```bash
# Full graph-aware triage summary
bv --robot-triage --format json

# Minimal deterministic next pick
bv --robot-next --format json

# Parallelizable dependency-respecting execution tracks
bv --robot-plan --format json

# Check graph health/cycles before changing dependency structure
bv --robot-insights --format json
```

Prefer `bv --robot-triage` over parsing JSONL yourself. It computes PageRank, betweenness, critical path, cycles, blocker cascades, and quick wins.

## Common Beads commands

```bash
br list --json                 # list local issues
br ready --json                # ready work: open and unblocked
br show ETH-xxxxxx             # inspect one issue
br create "Title" --type task  # create local issue
br update ETH-xxxxxx ...       # update fields
br comment ETH-xxxxxx -m ...   # add context
br close ETH-xxxxxx            # close after verification
br dep add ETH-a ETH-b         # record dependency/blocking relation
```

## Linear sync

The repo is configured for team `ETH` via Beads Linear sync. Beads is the source of truth; push local Beads state to Linear with:

```bash
scripts/beads-sync-to-linear.sh --dry-run
scripts/beads-sync-to-linear.sh
```

The Linear → Beads path is for one-time seeding/recovery only, not agent startup:

```bash
scripts/beads-refresh-linear.sh --dry-run
scripts/beads-refresh-linear.sh
```

Agent startup should only bootstrap local Beads state from git-tracked `.beads/issues.jsonl`:

```bash
scripts/beads-bootstrap.sh
```

## Context-mode issue lookups

For broad backlog/status questions, search the `issues` source before scanning files or calling Linear:

```text
ctx_search(queries: ["blocked P1", "ready work", "critical path"], source: "issues")
```

Keep indexed issue snippets bounded to active/open records only.
