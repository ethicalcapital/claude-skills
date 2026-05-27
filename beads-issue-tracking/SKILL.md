---
skill: beads-issue-tracking
description: Beads-first issue tracking with bv graph/search triage. MUST READ before issue/backlog triage, issue mutations, or next-task selection.
version: 1.1.0
---

# Beads Issue Tracking

Beads is truth. Linear, GitHub, and Forgejo are mirrors. Write with `br`/`bd` unless Sloane explicitly says otherwise.

## Rules

- Track all work in Beads.
- Start local: `scripts/beads-bootstrap.sh`.
- Before starting any task, run `bd ready`.
- File discovered work with `bd create`.
- Mutate with `br`/`bd`: create, update, comment, dep, claim, close.
- Before ending any session, run `bd sync`. If unavailable locally, record that and run the repo's current export/sync path instead.
- Never edit `.beads/issues.jsonl` by hand; mutate DB, then `bd export -o .beads/issues.jsonl`.
- Never run bare `bv`; it opens a TUI. Use robot/search flags.
- For Linear commands, use BWS and never print secrets.

## bv first

Use `bv`, not raw JSONL, for issue context:

```bash
bv --search "query terms" --robot-search --format json   # semantic issue search
bv --robot-next --format json                            # best next task
bv --robot-triage --format toon                          # summary, blockers, quick wins
bv --robot-plan --format toon                            # dependency-aware tracks
bv --robot-insights --format json                        # cycles, bottlenecks, graph health
bv --robot-alerts --format json                          # stale/blocking/priority alerts
bv --robot-suggest --format json                         # duplicates, missing deps, hygiene
```

Use `--format toon` for summaries; JSON when piping to `jq`.

## Hydrate for search

`bv --search` indexes issue ID, title, labels, and description. Put durable context in descriptions:

- source files/URLs
- current-state evidence
- decisions and constraints
- acceptance checks
- mirror links
- concise imported context

Use comments for logs/chatter. If a comment changes search meaning, summarize it into the description. No secrets.

## Common commands

```bash
br ready --json
br show ETH-xxxxxx --json
br create "Title" --type task --description "..." --labels a,b
br update ETH-xxxxxx --claim
br update ETH-xxxxxx --body-file /tmp/desc.md
br comment ETH-xxxxxx --file /tmp/note.md
br dep add ETH-a ETH-b
br close ETH-xxxxxx
bd export -o .beads/issues.jsonl
```

## Mirrors

Push Beads outward only:

```bash
scripts/beads-sync-to-linear.sh --dry-run
scripts/beads-sync-to-linear.sh
```

`scripts/beads-refresh-linear.sh` is seeding/recovery only, not startup.
