---
name: auditing-claude-installation
description: Use when investigating Claude Code installation issues, conflicts, or needing comprehensive audit of settings, commands, CLAUDE.md files, hooks, and MCP servers - identifies duplicates, conflicts, security risks, and performance issues
---

<EXTREMELY-IMPORTANT>
This skill provides a comprehensive audit of your entire Claude Code installation to identify:
- Configuration conflicts between user and project settings
- Duplicate command definitions
- Conflicting CLAUDE.md guidance
- Invalid hook configurations
- MCP server issues and duplicates
- Security risks (overly permissive permissions)
- Performance issues (too many MCP servers, etc.)

Run this skill when:
- Troubleshooting unexpected Claude behavior
- After installing new plugins or changing configs
- Periodic health checks of your installation
- Before committing project configurations
- When experiencing performance issues
</EXTREMELY-IMPORTANT>

# Claude Installation Audit Skill

## When to Use This Skill

Use this skill when you need to:
- **Investigate** why Claude Code isn't behaving as expected
- **Audit** your entire Claude installation for conflicts and waste
- **Verify** configuration changes didn't introduce issues
- **Optimize** performance by identifying redundant configs
- **Secure** your setup by finding overly permissive rules
- **Clean up** after installing/uninstalling plugins or MCP servers

## What This Skill Audits

### 1. Configuration Files (`settings.json`)
- ✅ JSON validity and parsing
- ✅ Permission conflicts between user/project levels
- ✅ Deprecated settings
- ✅ Overly permissive security rules

### 2. Custom Commands
- ✅ Duplicate command definitions
- ✅ Redundant functionality (multiple formatters, linters, etc.)
- ✅ Proper file extensions and naming

### 3. CLAUDE.md Files
- ✅ Conflicting guidance between global/project
- ✅ Readability and accessibility
- ✅ Directive conflicts (language preferences, style, etc.)

### 4. Hooks Configuration
- ✅ Invalid command paths
- ✅ Missing matchers
- ✅ Hook validity and accessibility

### 5. MCP Servers
- ✅ Duplicate definitions
- ✅ Too many enabled servers (performance)
- ✅ User vs project conflicts

### 6. Security Issues
- ✅ Wildcard permissions (e.g., `Bash(*)`)
- ✅ Overly permissive allow rules
- ✅ Critical security misconfigurations

### 7. Performance Issues
- ✅ Excessive MCP server count
- ✅ Redundant configurations
- ✅ Optimization opportunities

## How to Use This Skill

**Basic Usage:**
```
Run a full audit of my Claude installation
```

**After Making Changes:**
```
I just installed a new MCP server - audit my setup for conflicts
```

**Troubleshooting:**
```
Claude is behaving strangely - run an audit to find issues
```

**Regular Maintenance:**
```
It's been a while - audit my Claude installation for cleanup
```

## Audit Process

When you invoke this skill, Claude will:

1. **Scan configuration files** in both user (`~/.claude/`) and project (`./.claude/`) locations
2. **Load and validate** all `settings.json` files
3. **Check custom commands** for duplicates and redundancy
4. **Read CLAUDE.md files** and check for conflicts
5. **Validate hooks** and their configurations
6. **Audit MCP servers** for duplicates and performance
7. **Security scan** for overly permissive rules
8. **Generate comprehensive report** with prioritized issues

## Understanding the Audit Report

The audit generates a structured report with:

### Issue Severity Levels
- **CRITICAL** 🔴 - Security risks or breaking configs (fix immediately)
- **HIGH** 🟠 - Conflicts that may cause errors or unexpected behavior
- **MEDIUM** 🟡 - Redundancy, optimization opportunities
- **LOW** 🟢 - Minor issues, deprecated settings
- **INFO** ⚪ - Informational findings

### Issue Categories
- **CONFIG** - Settings.json issues
- **COMMANDS** - Custom command problems
- **CLAUDE_MD** - CLAUDE.md file conflicts
- **HOOKS** - Hook configuration issues
- **MCP** - MCP server problems
- **PERFORMANCE** - Performance degradation
- **SECURITY** - Security vulnerabilities

## Example Workflow

### Scenario 1: Post-Plugin Installation
```markdown
User: I just installed the debugging-toolkit plugin. Audit my setup.

Claude: I'm using the auditing-claude-installation skill to check for conflicts...

**Audit Results:**
✅ No critical issues found
⚠️  1 medium issue: MCP server count is now 9 (recommend < 8 for performance)

**Recommendation:** Consider disabling unused MCP servers to maintain startup performance.
```

### Scenario 2: Unexplained Behavior
```markdown
User: Claude keeps ignoring my project CLAUDE.md. Run an audit.

Claude: I'm using the auditing-claude-installation skill to investigate...

**Audit Results:**
🔴 1 critical issue found:
- AUDIT-0003: Conflicting CLAUDE.md Guidance
  Location: ~/.claude/CLAUDE.md vs ./CLAUDE.md
  Issue: Global CLAUDE.md says "prefer TypeScript", project says "avoid TypeScript"
  Recommendation: Align guidance. Project-level takes precedence.

**Action:** Update your global CLAUDE.md to remove TypeScript preference or make it conditional.
```

### Scenario 3: Regular Maintenance
```markdown
User: Run a health check on my Claude installation

Claude: I'm using the auditing-claude-installation skill for a full audit...

**Audit Results:**
✅ Installation looks clean!
📊 Statistics:
- 2 config files scanned
- 12 custom commands found
- 2 CLAUDE.md files analyzed
- 6 MCP servers configured
- 0 issues detected

Your Claude Code installation is healthy.
```

## Checklist for Using This Skill

When running this skill, Claude will:

- [ ] Load all configuration files (user + project)
- [ ] Validate JSON syntax
- [ ] Check permission hierarchies
- [ ] Scan custom command directories
- [ ] Detect duplicate commands
- [ ] Read CLAUDE.md files
- [ ] Check for directive conflicts
- [ ] Validate hook configurations
- [ ] Audit MCP server setup
- [ ] Run security checks
- [ ] Run performance analysis
- [ ] Generate prioritized report
- [ ] Provide actionable recommendations

## What You Get

After running this skill, you receive:

1. **Summary Report**
   - Total issues found
   - Breakdown by severity
   - Breakdown by category
   - Overall health status

2. **Detailed Issues List**
   - Issue ID for tracking
   - Severity and category
   - Clear description
   - Exact file locations
   - Specific recommendations

3. **Statistics**
   - Config files found
   - Commands discovered
   - CLAUDE.md files analyzed
   - MCP servers configured

4. **Actionable Recommendations**
   - Prioritized next steps
   - Fix critical issues first
   - Optimization suggestions
   - Cleanup opportunities

## Files This Skill Uses

The audit scans these locations:
- `~/.claude/settings.json` (user global config)
- `./.claude/settings.json` (project config)
- `~/.claude/commands/` (user commands)
- `./.claude/commands/` (project commands)
- `~/.claude/CLAUDE.md` (global instructions)
- `./CLAUDE.md` (project instructions)

## Common Issues Found

### Configuration Conflicts
- User allows `Bash(git push:*)`, project denies it
- Duplicate MCP server definitions
- Deprecated settings still present

### Command Issues
- Same command defined in user + project
- Multiple formatters (prettier, beautify, format)
- Multiple test commands (test, spec, testing)

### CLAUDE.md Conflicts
- Global says "use CommonJS", project says "use ES modules"
- Conflicting style preferences
- Contradictory language choices

### Security Risks
- Overly broad wildcards: `Bash(*)`
- Missing permission restrictions
- Insecure hook configurations

### Performance Issues
- 10+ MCP servers enabled
- Redundant command definitions
- Unnecessary duplicate configs

## Best Practices

After running an audit:

1. **Fix critical issues immediately** - Security first
2. **Address high-priority conflicts** - Prevent errors
3. **Consolidate duplicates** - Reduce complexity
4. **Remove deprecated settings** - Stay current
5. **Optimize performance** - Disable unused features
6. **Document decisions** - Why you kept certain configs

## Skill Execution

This skill uses a Python script (`audit_script.py`) to perform deep analysis.

The script will:
1. Run without requiring user approval (read-only analysis)
2. Generate a JSON report with all findings
3. Return formatted results to Claude
4. Provide actionable next steps

## Notes

- This is a **read-only audit** - it never modifies files
- Safe to run anytime without risk
- Can be run in CI/CD for pre-commit checks
- Helpful for onboarding new team members
- Great for debugging mysterious behavior

## Integration with Other Skills

This skill pairs well with:
- **superpowers:systematic-debugging** - After finding issues, use this to fix them
- **superpowers:verification-before-completion** - Audit before marking work complete
- **maintaining-ethicic-site** - Audit before deploying configs

---

Remember: **If Claude is acting weird, run an audit first.** Often saves hours of debugging.
