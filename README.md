# Claude Code Skills — Ethical Capital

Skills for [Claude Code](https://docs.anthropic.com/en/docs/claude-code) used at [Ethical Capital](https://ethicic.com) for investment research, compliance, and software development.

These are published for transparency. Clients and prospective clients can see exactly how we instruct our AI tools — what standards we hold them to, what we check for, and how we think about quality.

## Skills We Built

### Investment Research & Compliance

How we screen companies, write exclusion narratives, and check our own work.

| Skill | Purpose |
|-------|---------|
| [writing-exclusions](writing-exclusions/) | Voice and structure for exclusion narratives (public-facing on ethicic.com) |
| [exclusions-manager](exclusions-manager/) | Full exclusion lifecycle — sources, approval workflow, taxonomy |
| [evidence-crawl](evidence-crawl/) | Multi-source evidence gathering for exclusion research |
| [research-reviewer](research-reviewer/) | Research note quality review, staleness detection, MD-DB consistency |
| [compliance-analyst](compliance-analyst/) | RIA marketing compliance — SEC Marketing Rule, Utah R164, CAN-SPAM |
| [ecic-brand](ecic-brand/) | Brand voice, visual identity, and tone enforcement |

### Writing & Argumentation

How we hold our own prose to account.

| Skill | Purpose |
|-------|---------|
| [buzz-saw-editor](buzz-saw-editor/) | Ruthless argument editor — cuts filler, audits logic, flags unsupported claims |
| [fact-checker](fact-checker/) | Deep fact-checker with multi-source search, structured verdicts, and interactive edit approval |
| [anti-racist-review](anti-racist-review/) | Checks writing about marginalized communities for encoded assumptions |

### Content & Reports

| Skill | Purpose |
|-------|---------|
| [typeset-pdf](typeset-pdf/) | Branded PDF generation from markdown/Typst |
| [serper-seo](serper-seo/) | SERP research, keyword analysis, content framing |

## Development Process Skills

General-purpose engineering discipline. Not specific to investment research — useful for any team using Claude Code.

### Planning & Execution

| Skill | Purpose |
|-------|---------|
| [brainstorming](brainstorming/) | Collaborative design exploration before implementation |
| [writing-plans](writing-plans/) | Creates bite-sized TDD implementation plans from specs |
| [executing-plans](executing-plans/) | Batch execution of plans with review checkpoints |
| [subagent-driven-development](subagent-driven-development/) | Fresh subagent per task with two-stage review (spec + quality) |
| [dispatching-parallel-agents](dispatching-parallel-agents/) | Parallel investigation of independent problems |

### Quality & Discipline

| Skill | Purpose |
|-------|---------|
| [test-driven-development](test-driven-development/) | RED-GREEN-REFACTOR discipline enforcement |
| [systematic-debugging](systematic-debugging/) | Root cause investigation before attempting fixes |
| [verification-before-completion](verification-before-completion/) | Evidence before claims — no success assertions without fresh verification |
| [requesting-code-review](requesting-code-review/) | Dispatch code review subagents at key checkpoints |
| [receiving-code-review](receiving-code-review/) | Technical evaluation of feedback — verify before implementing, push back when wrong |
| [workers-best-practices](workers-best-practices/) | Cloudflare Workers production quality patterns |

### Git & Workflow

| Skill | Purpose |
|-------|---------|
| [using-git-worktrees](using-git-worktrees/) | Isolated workspaces for parallel branch work |
| [finishing-a-development-branch](finishing-a-development-branch/) | Verify tests, present merge/PR/keep/discard options, clean up |
| [using-superpowers](using-superpowers/) | Master skill — routes to the right skill before any action |

### Meta

| Skill | Purpose |
|-------|---------|
| [writing-skills](writing-skills/) | TDD applied to process documentation — test skills with subagents before deploying |

## Installation

Copy any skill directory into your `.claude/skills/` folder:

```bash
# Single skill
cp -r buzz-saw-editor/ ~/.claude/skills/buzz-saw-editor/

# All skills
cp -r */ ~/.claude/skills/
```

Skills are loaded automatically by Claude Code when their description matches your task.

## Philosophy

We believe in radical transparency. These skills encode our actual working standards — not aspirational documentation, but the instructions we give our tools every day. If a skill says "never skip verification," that is a rule we enforce on ourselves.

The investment research and compliance skills are especially relevant for due diligence. They show how we screen companies, write exclusion narratives, check facts, and review marketing materials for regulatory compliance.

## License

[MIT](LICENSE)
