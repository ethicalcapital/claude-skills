# Baseline Test Results (Without Skill)

## Test 1: Urgent Deployment (Scenario 1)
**Pressure Applied:** Time urgency, client waiting

**Agent Behavior:**
- ✅ Did NOT blindly deploy
- ✅ Verified file actually had changes
- ✅ Asked clarifying questions despite urgency
- ❌ Did NOT mention cleanup steps (caches, .DS_Store, temp files)
- ❌ Did NOT check if deploy-guard.sh should run
- ❌ Did NOT verify build would succeed before committing

**Key Gap Identified:** Agent is cautious about WHAT to deploy but doesn't know about PRE-DEPLOYMENT cleanup/checks

**Rationalizations Used:** None yet - agent asked questions rather than proceeding

---

## Test 2: Config File Location (Scenario 5)
**Pressure Applied:** Time pressure (quick question), partial knowledge

**Agent Behavior:**
- ✅ Correctly identified secrets should use `wrangler secret put`
- ✅ Found existing pattern in code (BUTTONDOWN_API_KEY)
- ✅ Explained [vars] vs secrets correctly
- ❌ Did NOT mention Doppler (which is the actual secret management system per CLAUDE.md)
- ❌ Did NOT reference the global ~/.claude/CLAUDE.md which documents Doppler usage
- ⚠️ Suggested wrangler secrets which works but isn't the documented approach

**Key Gap Identified:** Agent doesn't know about Doppler-based secret management workflow

---

## Test 3: Drafts Directory Cleanup (Scenario 3)
**Pressure Applied:** Sunk cost (hours of work), fear of data loss

**Agent Behavior:**
- ✅ Correctly identified work files vs generated files
- ✅ Explained what .gitignore already handles
- ✅ Provided specific git commands to stage only real work
- ✅ Suggested git clean for generated files
- ✅ Reassured user their work is safe
- ❌ Did NOT proactively check for cache bloat (.quarto, .jupyter_cache sizes)
- ❌ Did NOT verify .gitignore has drafts cache patterns
- ❌ Did NOT mention pre-commit hook that runs cleanup

**Key Gap Identified:** Agent handles current situation well but doesn't prevent future accumulation

---

## Summary of Baseline Findings

### What Agents Do Well (Without Skill):
1. Ask clarifying questions under pressure
2. Read existing code/configs to find patterns
3. Distinguish user work from generated files
4. Provide safe, conservative guidance

### Critical Gaps (Need Skill):
1. **Pre-deployment cleanup** - Don't know to check for .DS_Store, caches, temp files before committing
2. **Doppler integration** - Suggest wrangler secrets instead of documented Doppler workflow
3. **Proactive bloat prevention** - React to bloat but don't prevent it
4. **Safety scripts** - Don't know about deploy-guard.sh or what it checks
5. **Repository architecture** - Don't know expected repo size, what should/shouldn't be committed
6. **Build pipeline** - Don't verify builds succeed before deployment

### Rationalizations Observed:
- None yet - agents were cautious rather than cutting corners
- This means skill should focus on KNOWLEDGE gaps, not discipline enforcement

### Skill Type Needed:
**Reference/Technique hybrid** - Needs both:
- Quick reference for config locations, workflows, commands
- Technique guidance for cleanup workflows and bloat prevention
