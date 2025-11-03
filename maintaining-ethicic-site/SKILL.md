---
name: maintaining-ethicic-site
description: Use when working with ethicic.com repository for deployment, config changes, or cleanup - provides architecture knowledge, pre-deployment checklists, cache management, and Doppler secret integration to prevent bloat and deployment issues
---

# Maintaining ethicic.com Repository

## Overview

The ethicic.com repository is a Quarto-based static site deployed to Cloudflare Workers. This skill provides essential knowledge for maintaining the repository: where configs live, how to deploy safely, how to manage secrets via Doppler, and how to prevent cache bloat.

**Core Principle:** Clean repository = fast operations. Expected size ~1 GB. If larger, investigate.

## When to Use

Use this skill when:
- Deploying to production
- Adding environment variables or secrets
- Working in drafts/ directory
- Repository operations are slow
- Git shows hundreds of untracked files
- Before committing after development work

## Repository Architecture

### Key Config Files

| File | Purpose | Location |
|------|---------|----------|
| `wrangler.toml` | Cloudflare Worker config (production) | Root |
| `_quarto.yml` | Main site configuration & build pipeline | Root |
| `package.json` | Node.js dependencies & npm scripts | Root |
| `.gitignore` | Excludes caches, .DS_Store, generated files | Root & drafts/ |
| `.husky/pre-commit` | Pre-commit hook (cleanup & prose check) | .husky/ |
| `.husky/pre-push` | Pre-push safety checks | .husky/ |
| `scripts/deploy-guard.sh` | Deployment safety script | scripts/ |

### Directory Structure

```
ethicic.com/
├── content/           # Website content (.qmd files)
├── factsheets/        # Generated strategy fact sheets
├── assets/
│   ├── brand/         # Brand assets & styles
│   ├── charts/        # Auto-generated charts
│   └── data/          # Performance CSVs (COMMIT these)
├── scripts/           # Build automation
├── drafts/            # Analysis work (manage carefully)
├── _site/             # Generated output (NEVER commit)
└── node_modules/      # Dependencies (NEVER commit)
```

## Pre-Deployment Checklist

**ALWAYS run before deploying:**

1. **Check for bloat**
   ```bash
   # Expected: ~1 GB
   du -sh .

   # If >1.5 GB, investigate:
   find . -name ".DS_Store" | wc -l  # Should be 0
   du -sh drafts/.venv 2>/dev/null    # Should not exist
   du -sh drafts/.quarto              # If >50 MB, clean
   ```

2. **Clean caches**
   ```bash
   # Remove .DS_Store files
   find . -name .DS_Store -exec rm {} \;

   # Clean drafts caches if large
   rm -rf drafts/.quarto drafts/.jupyter_cache drafts/_freeze
   ```

3. **Verify build succeeds**
   ```bash
   npm run build
   # Must complete without errors
   ```

4. **Check git status**
   ```bash
   git status
   # Review what will be deployed
   # NEVER commit: _site/, node_modules/, .DS_Store, *.log
   ```

5. **Run deploy guard**
   ```bash
   bash ./scripts/deploy-guard.sh
   # Checks for TODOs in rendered content
   ```

## Secret Management (Doppler)

**CRITICAL:** Use Doppler for ALL secrets, not wrangler secrets.

### Adding a New Secret

```bash
# Add to Doppler (project: rawls, env: dev)
doppler secrets set SECRET_NAME

# Verify it's available
doppler secrets get SECRET_NAME --plain

# Worker access (no code changes needed if using doppler run)
# Secrets auto-injected into env object
```

### Config Variables vs Secrets

**Public variables** → `wrangler.toml` `[vars]` section:
```toml
[vars]
SITE_URL = "https://ethicic.com"
ENVIRONMENT = "production"
```

**Secrets** → Doppler only (API keys, tokens):
- NEVER in wrangler.toml
- NEVER in .env files
- ALWAYS in Doppler

### Deployment with Secrets

```bash
# Deploy uses Doppler automatically
npm run deploy
# Internally runs: doppler run -- npx wrangler deploy
```

## Drafts Directory Management

### What to Commit from drafts/

**✅ COMMIT:**
- Your analysis scripts (.py, .R)
- Markdown docs (.md, .qmd)
- Small data files (<10 MB)
- Presentations (.html if hand-crafted, .md)

**❌ NEVER COMMIT:**
- `.quarto/` - Quarto cache (regenerable)
- `.jupyter_cache/` - Jupyter cache (regenerable)
- `_freeze/` - Frozen computations (regenerable)
- `.venv/` - Python environment (duplicate of root)
- `_output/` - Generated analysis outputs
- Generated HTML from .qmd (unless hand-crafted)

### Cleanup Workflow

```bash
# Check what's taking space
du -sh drafts/.quarto drafts/.jupyter_cache drafts/_freeze

# Clean caches (safe - regenerable)
rm -rf drafts/.quarto drafts/.jupyter_cache drafts/_freeze

# See what git would clean
git clean -Xn drafts/

# Actually clean gitignored files
git clean -Xf drafts/
```

### Expected Behavior

- `.gitignore` already excludes cache directories
- Pre-commit hook does NOT auto-clean (you control timing)
- After cleanup, `git status` should show only your work files

## Deployment Process

### Standard Deployment

```bash
# 1. Run pre-deployment checklist (see above)

# 2. Commit changes
git add <files>
git commit -m "Description"

# 3. Deploy
npm run deploy
# Runs: clean → render charts → build → lint → wrangler deploy

# 4. Verify
# Check https://ethicic.com
```

### Deploy Script Breakdown

`npm run deploy` executes:
1. `scripts/deploy-guard.sh` - Safety checks (TODOs in rendered content)
2. `scripts/clean-workspace.sh` - Cleanup before build
3. `scripts/render-observable-charts.mjs` - Generate SVG charts
4. `scripts/install-quarto.sh render` - Build site
5. `scripts/lint-vega-lite.js` - Validate charts
6. `npx wrangler deploy` - Deploy to Cloudflare

### Emergency Deploy

If you MUST skip checks (not recommended):
```bash
npx wrangler deploy
# Skips build, uses existing _site/
# Only if you're certain _site/ is current
```

## Performance Data Updates

### Monthly Update Workflow

1. **Get new data from Altruist** (manual export)

2. **Update CSVs** in `assets/data/`:
   ```
   growth-performance.csv
   income-performance.csv
   diversification-performance.csv
   ```

3. **Regenerate fact sheets**:
   ```bash
   ./scripts/render_factsheets.sh
   # Generates charts + HTML + PDF
   ```

4. **Commit and deploy**:
   ```bash
   git add assets/data/*.csv factsheets/*.{html,pdf}
   git commit -m "Update performance data for [Month Year]"
   npm run deploy
   ```

## Common Issues

### Issue: Git operations slow
**Cause:** Repository bloat
**Fix:**
```bash
du -sh .  # Check size
# Expected: ~1 GB
# If >1.5 GB, run cleanup checklist
```

### Issue: Hundreds of untracked files in drafts/
**Cause:** Cache accumulation
**Fix:**
```bash
# See what's taking space
du -sh drafts/.quarto drafts/.jupyter_cache

# Clean caches
rm -rf drafts/.quarto drafts/.jupyter_cache drafts/_freeze
```

### Issue: Deploy fails with "TODO in content"
**Cause:** TODO markers in rendered .qmd files
**Fix:**
```bash
# Find TODOs
grep -r "TODO" content/ factsheets/

# Remove or comment out before deploying
```

### Issue: Build fails during deployment
**Cause:** Missing dependencies or syntax errors
**Fix:**
```bash
# Test build locally first
npm run build

# Check errors, fix, then deploy
```

## Quick Reference

### Essential Commands

```bash
# Check repo health
du -sh . && git status --short

# Clean all caches
find . -name .DS_Store -exec rm {} \; && \
  rm -rf drafts/.quarto drafts/.jupyter_cache drafts/_freeze

# Full deploy workflow
npm run build && npm run deploy

# Add secret via Doppler
doppler secrets set SECRET_NAME

# Regenerate fact sheets
./scripts/render_factsheets.sh
```

### File Size Expectations

| Item | Expected Size | Action if Exceeded |
|------|---------------|-------------------|
| Total repo | ~1 GB | Investigate bloat |
| drafts/.quarto | <50 MB | Clean cache |
| .git/ | ~400 MB | Normal (git history) |
| node_modules/ | ~200 MB | Normal |
| .venv/ (root) | ~800 MB | Normal |
| drafts/.venv/ | 0 | Should not exist |

## Common Mistakes

### ❌ Deploying Without Safety Checks
**Wrong:** `npx wrangler deploy` directly
**Right:** `npm run deploy` (includes deploy-guard.sh)

### ❌ Using wrangler secrets Instead of Doppler
**Wrong:** `npx wrangler secret put API_KEY`
**Right:** `doppler secrets set API_KEY --project rawls --config dev`

### ❌ Committing Generated Files
**Wrong:** Committing `_site/`, `*.html` from .qmd, `.quarto/`
**Right:** Let build process regenerate these

### ❌ Ignoring Repository Bloat
**Wrong:** "It's 2.5 GB, that's normal for a big project"
**Right:** Expected ~1 GB. If larger, investigate and clean

### ❌ Skipping Pre-Deployment Checklist
**Wrong:** "I tested locally, it's fine to deploy"
**Right:** Run full checklist every time (prevents production issues)

## When NOT to Use This Skill

- For content editing (just edit .qmd files)
- For design/styling changes (use brand guidelines)
- For adding new pages (follow existing patterns)
- For non-ethicic.com repositories

This skill is specifically for ethicic.com **maintenance and deployment**, not content creation.
