---
skill: beads-issue-tracking
description: Beads-first work tracking with bv search/triage. MUST READ before starting work, issue/backlog triage, issue mutations, or next-task selection.
version: 1.4.0
---

# Beads Issue Tracking

Beads is truth. Linear, GitHub, and Forgejo are mirrors. Write with `br`/`bd` unless Sloane explicitly says otherwise.

## Non-negotiables

- Track all work in Beads.
- Start local: `scripts/beads-bootstrap.sh`.
- Before starting any task, run `bd ready`.
- File any discovered work >2 minutes with `bd create`.
- Cover blockers and related follow-ups; link them with deps.
- Before ending: persist state to git with `bd export -o .beads/issues.jsonl`, commit, and `git push`.
- Dolt remotes/backups are optional only when configured.
- Never edit `.beads/issues.jsonl` by hand; mutate DB, then export.
- Never run bare `bv`; it opens a TUI. Use robot/search flags.

## Non-interactive commands only

Never run `bd create` without flags; it can hang waiting for input.

```bash
bd create "Title" --type task --priority 2 --description "Context" --json
echo 'Description with `code` or "quotes"' \
  | bd create "Title" --type task --priority 2 --description=- --json
bd show ETH-xxxx --json
bd ready --json
bd update ETH-xxxx --claim
bd close ETH-xxxx --reason "What actually shipped"
```

Types: `bug|feature|task|epic|chore|decision`. Priority: `0` highest, `4` lowest. Always use `--json` for programmatic access.

## Think → Create → Act

- Unknown bug: investigate briefly, then file discovered work with `--deps discovered-from:<parent-id>`.
- Known feature: create the issue first with acceptance criteria, then work from `bd show <id>`.
- Large goal: create an epic and immediately decompose into child tasks.
- Atomic task: one implementation step, clear done check.
- Dependencies: use `blocks` for hard blockers, `parent-child` for hierarchy, `discovered-from` for investigation fallout, and `related` for soft links; `bd ready` depends on blockers.

## Field discipline

- Title/description: stable problem statement; change rarely.
- Design/acceptance criteria: evolve as the approach clarifies.
- Notes/comments: session handoff (`COMPLETED`, `NEXT`, blockers).
- Status: claim immediately (`bd update <id> --claim`); close with `--reason`.

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

`bv --search` indexes issue ID, title, labels, and description. Put durable context in descriptions: source paths, evidence, decisions, constraints, acceptance checks, mirror links. Use comments for chatter/logs. If a comment changes search meaning, summarize it into the description. No secrets.

## State persistence

Default for now: save Beads state in git.

```bash
bd export -o .beads/issues.jsonl
git add .beads/issues.jsonl
git commit -m "beads: update issue state"
git push
```

Optional only when configured:

```bash
bd dolt push      # Dolt remote
bd dolt pull      # recover from remote/stale state
bd backup sync    # portable backup
bd backup restore # restore portable backup
bd doctor         # diagnose only; do not run --fix without explicit approval
```

Repo mirrors are outward only:

```bash
scripts/beads-sync-to-linear.sh --dry-run
scripts/beads-sync-to-linear.sh
```

`scripts/beads-refresh-linear.sh` is seeding/recovery only, not startup.
