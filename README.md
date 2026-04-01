# Claude Code Dotfiles — Ethical Capital

Configuration, skills, and plugin stack for [Claude Code](https://docs.anthropic.com/en/docs/claude-code) as used at [Ethical Capital](https://ethicic.com) for investment research, compliance, and software development.

Published for transparency. Clients and prospective clients can see exactly how we instruct our AI tools — what standards we hold them to, what we check for, and how we think about quality.

## Plugin Stack

We run 16 plugins. The principle: LSPs for code navigation, workflow plugins for discipline, domain plugins only when they earn their token budget.

### Always On

| Plugin | Source | What It Does |
|--------|--------|-------------|
| `superpowers` | claude-plugins-official | 14 workflow skills (brainstorming, TDD, code review, debugging, etc.) |
| `episodic-memory` | superpowers-marketplace | Cross-session memory via semantic search |
| `elements-of-style` | superpowers-marketplace | Strunk's rules applied to all prose |
| `brand-voice` | knowledge-work-plugins | Brand guideline enforcement + generation |
| `productivity` | knowledge-work-plugins | Task management, memory management |
| `frontend-design` | claude-plugins-official | Anti-generic design direction |
| `claude-md-management` | claude-plugins-official | CLAUDE.md auditing and improvement |
| `dead-code` | jko-claude-plugins | Dead code detection and removal |
| `rust` | jko-claude-plugins | Rust critique, hardening, type strengthening |

### Language Servers (LSP)

| Plugin | Language | Notes |
|--------|----------|-------|
| `typescript-lsp` | TypeScript | Symbol nav, type checking |
| `pyright-lsp` | Python | Type checking, symbol nav |
| `rust-analyzer-lsp` | Rust | Full Rust IDE support |

### Domain-Specific

| Plugin | Source | What It Does |
|--------|--------|-------------|
| `database-design` | claude-code-workflows | PostgreSQL schema design best practices |
| `database-migrations` | claude-code-workflows | Zero-downtime migration strategies |
| `python-development` | claude-code-workflows | Async patterns, testing, packaging, uv |
| `debugging-toolkit` | claude-code-workflows | Structured debugging methodology |

### Disabled (Available When Needed)

| Plugin | Why Disabled |
|--------|-------------|
| `marketing-skills` | ~25 skills, rarely needed — re-enable for campaigns |
| `posthog` | ~20 skills — re-enable for analytics work |
| `serena` | Replaced by per-language LSPs (TS/Python/Rust) |
| `postgres-best-practices` | Duplicate of project-level Supabase MCP |
| `data-engineering` | Not currently needed |
| `code-review` | Superpowers handles this |
| `textual-tui` | Not currently needed |

## MCP Servers

### Global (`~/.claude/.mcp.json`)

| Server | What |
|--------|------|
| `research-mcp` | Railway-hosted web research (fetch, crawl, PDF, screenshot, search) |
| `devin` | DeepWiki documentation + Devin session management |

### Project-Level (`.mcp.json`)

| Server | What |
|--------|------|
| `supabase` | Database management, migrations, SQL execution |
| `linear-server` | Issue tracking, project management |

### Cloud Integrations (Account-Level)

Gmail, Magic Patterns, Mesh (contacts), Chrome automation.

### What We Removed (and Why)

| Server | Replaced By |
|--------|-------------|
| `filesystem` | Claude Code built-in Read/Write/Edit/Glob/Grep |
| `cloudflare-observability` | `workers-observability` skill + wrangler CLI |
| `cloudflare-bindings` | `workers-observability` skill + wrangler CLI |
| `serena` (global MCP) | `serena` plugin (then replaced by per-language LSPs) |
| `vectorbtpro` | Configured but never enabled — removed dead config |

## Skills

### Investment Research & Compliance

How we screen companies, write exclusion narratives, and check our own work.

| Skill | Purpose |
|-------|---------|
| [writing-exclusions](writing-exclusions/) | Voice and structure for exclusion narratives (public-facing on ethicic.com) |
| [exclusions-manager](exclusions-manager/) | Full exclusion lifecycle — sources, approval workflow, taxonomy |
| [evidence-crawl](evidence-crawl/) | Multi-source evidence gathering for exclusion research |
| [research-reviewer](research-reviewer/) | Research note quality review, staleness detection, MD-DB consistency |
| [research-notes](research-notes/) | Research note management for ~7,600 investment research notes |
| [pipeline-runner](pipeline-runner/) | Orchestrates the overnight research pipeline |
| [compliance-analyst](compliance-analyst/) | RIA marketing compliance — SEC Marketing Rule, Utah R164, CAN-SPAM |
| [investment-analysis](investment-analysis/) | Structured logical analysis — thesis validation, bias detection, decision audit trails |

### Writing & Argumentation

How we hold our own prose to account. These two are complementary: buzz-saw audits logic and evidence, elements-of-style (plugin) refines prose clarity.

| Skill | Purpose |
|-------|---------|
| [buzz-saw-editor](buzz-saw-editor/) | Ruthless argument editor — cuts filler, audits logic chains, flags unsupported claims |
| [fact-checker](fact-checker/) | Multi-source fact-checking with structured verdicts and interactive edit approval |
| [anti-racist-review](anti-racist-review/) | Checks writing about marginalized communities for encoded assumptions |
| [veil-of-ignorance](veil-of-ignorance/) | Forces analysis through Rawlsian lens — who bears consequences the analyst doesn't? |

### Brand & Content

| Skill | Purpose |
|-------|---------|
| [ecic-brand](ecic-brand/) | Brand voice, visual identity, and tone enforcement |
| [serper-seo](serper-seo/) | SERP research, keyword analysis, content framing |
| [signup-flow-cro](signup-flow-cro/) | Signup and registration flow conversion optimization |

### Infrastructure & Observability

| Skill | Purpose |
|-------|---------|
| [deploy-worker](deploy-worker/) | Cloudflare Worker deployment with pre-deploy checks and rollback |
| [workers-observability](workers-observability/) | Worker health, binding inspection, metrics, debugging (replaces CF MCPs) |
| [workers-best-practices](workers-best-practices/) | CF Workers production patterns — streaming, error handling, secrets |

### Code Quality & Review

| Skill | Purpose |
|-------|---------|
| [cynical-schema-review](cynical-schema-review/) | Ruthless database schema review — type mismatches, missing constraints, edge cases |
| [data-app-ui-review](data-app-ui-review/) | UI/UX review for data apps, dashboards, analytics tools |
| [accessibility-review](accessibility-review/) | WCAG 2.2 AA + PDF/UA across all output types |
| [auditing-claude-installation](auditing-claude-installation/) | Audit Claude Code setup for conflicts, duplicates, security risks |
| [typeset-pdf](typeset-pdf/) | Branded PDF generation from markdown/Typst |

### Thinking Tools

| Skill | Purpose |
|-------|---------|
| [thought-partner](thought-partner/) | Structured reasoning for tricky, uncertain, or strategic problems |

## Configuration Principles

### Token Budget Management

Every skill description, MCP tool name, and plugin instruction block consumes tokens in every prompt. We audit aggressively:

- **Skills**: ~95 total (was 130). Removed duplicates from plugins re-exporting the same skills.
- **MCP tools**: ~105 deferred tools (was 152). Removed redundant servers, fixed Serena context flag.
- **Plugin MCP servers**: 18 (was 27). Disabled servers that duplicate project-level MCPs.
- **LSP servers**: 3 (TypeScript, Python, Rust). Replaced Serena's single-language MCP with per-language LSPs.

### Credential Management

All secrets flow through [Doppler](https://doppler.com) (project: `rawls`, env: `dev`). MCP configs never contain hardcoded credentials — they wrap commands in `doppler run --`.

### Permission Philosophy

Pattern-based allow rules (`Bash(git:*)`, `Bash(doppler run:*)`) rather than per-command approvals. Session-specific one-off permissions are cleaned periodically to prevent `settings.local.json` bloat.

## Installation

Copy any skill directory into your `.claude/skills/` folder:

```bash
# Single skill
cp -r buzz-saw-editor/ ~/.claude/skills/buzz-saw-editor/

# All skills
for d in */; do [ -f "$d/SKILL.md" ] && cp -r "$d" ~/.claude/skills/; done
```

Skills are loaded automatically by Claude Code when their trigger description matches your task.

## Philosophy

We believe in radical transparency. These skills encode our actual working standards — not aspirational documentation, but the instructions we give our tools every day. If a skill says "never skip verification," that is a rule we enforce on ourselves.

The investment research and compliance skills are especially relevant for due diligence. They show how we screen companies, write exclusion narratives, check facts, and review marketing materials for regulatory compliance.

## License

[CC BY-NC 4.0](LICENSE) — use freely, but not for resale.
