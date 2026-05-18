---
name: verification-before-completion
description: Use when about to claim work is complete, fixed, or passing, before committing or creating PRs - requires running verification commands and confirming output before making any success claims; evidence before assertions always
---

# Verification Before Completion

## Overview

Claiming work is complete without verification is dishonesty, not efficiency.

**Core principle:** Evidence before claims, always.

**Violating the letter of this rule is violating the spirit of this rule.**

## The Iron Law

```
NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE
```

If you haven't run the verification command in this message, you cannot claim it passes.

## The Gate Function

```
BEFORE claiming any status or expressing satisfaction:

1. IDENTIFY: What command proves this claim?
2. RUN: Execute the FULL command (fresh, complete)
3. READ: Full output, check exit code, count failures
4. VERIFY: Does output confirm the claim?
   - If NO: State actual status with evidence
   - If YES: State claim WITH evidence
5. ONLY THEN: Make the claim

Skip any step = lying, not verifying
```

## Common Failures

| Claim | Requires | Not Sufficient |
|-------|----------|----------------|
| Tests pass | Test command output: 0 failures | Previous run, "should pass" |
| Linter clean | Linter output: 0 errors | Partial check, extrapolation |
| Build succeeds | Build command: exit 0 | Linter passing, logs look good |
| Bug fixed | Test original symptom: passes | Code changed, assumed fixed |
| Regression test works | Red-green cycle verified | Test passes once |
| Agent completed | VCS diff shows changes | Agent reports "success" |
| Requirements met | Line-by-line checklist | Tests passing |

## Red Flags - STOP

- Using "should", "probably", "seems to"
- Expressing satisfaction before verification ("Great!", "Perfect!", "Done!", etc.)
- About to commit/push/PR without verification
- Trusting agent success reports
- Relying on partial verification
- Thinking "just this once"
- Tired and wanting work over
- **ANY wording implying success without having run verification**

## Rationalization Prevention

| Excuse | Reality |
|--------|---------|
| "Should work now" | RUN the verification |
| "I'm confident" | Confidence ≠ evidence |
| "Just this once" | No exceptions |
| "Linter passed" | Linter ≠ compiler |
| "Agent said success" | Verify independently |
| "I'm tired" | Exhaustion ≠ excuse |
| "Partial check is enough" | Partial proves nothing |
| "Different words so rule doesn't apply" | Spirit over letter |

## Key Patterns

**Tests:**
```
✅ [Run test command] [See: 34/34 pass] "All tests pass"
❌ "Should pass now" / "Looks correct"
```

**Regression tests (TDD Red-Green):**
```
✅ Write → Run (pass) → Revert fix → Run (MUST FAIL) → Restore → Run (pass)
❌ "I've written a regression test" (without red-green verification)
```

**Build:**
```
✅ [Run build] [See: exit 0] "Build passes"
❌ "Linter passed" (linter doesn't check compilation)
```

**Requirements:**
```
✅ Re-read plan → Create checklist → Verify each → Report gaps or completion
❌ "Tests pass, phase complete"
```

**Agent delegation:**
```
✅ Agent reports success → Check VCS diff → Verify changes → Report actual state
❌ Trust agent report
```

## State Fact-Checking Gate

Before any completion claim, verify that state-as-described IS current state.

The most insidious failure mode is claiming work is done because you *remember* doing it — but the actual state of the world hasn't caught up, or you context-switched before the final step.

### The Gate

```
BEFORE claiming any state (merged, deployed, fixed, passing):

1. TODO RECONCILIATION
   For every todo marked `completed`:
   - ✅ Merge: `git log --oneline` confirms the commit is on target branch
   - ✅ Fix: test output shows 0 failures (fresh run, not last run)
   - ✅ Deploy: health endpoint or deployment status confirms live
   - ✅ PR closed: GitHub confirms PR is merged, branch deleted
   - ⛔ "I remember doing it" — verify is not remembering

2. STATUS FACT-CHECK  
   For every claim in your response:
   - "Tests pass" → you ran them THIS message, not last message
   - "PR merged" → git log shows the commit, PR shows Merged status
   - "Deployed" → request the endpoint, check the version
   - "Ticket done" → Linear/issue tracker confirms status
   - ⛔ "Should be" / "Probably" / "I think" — not evidence

3. CLAIM AUDIT
   Read your claim. Ask: what would prove it's false?
   - If you can't produce counter-evidence in 5 seconds → RACE CONDITION
   - Your description of state diverged from reality
   - STOP. Re-verify before speaking.

4. PERIODIC STATE RECONCILIATION
   Every N turns (N=5 for fast work, N=10 for deep work):
   - Re-read your active todos
   - Is each status still accurate?
   - Did anything land/merge/deploy that you forgot to track?
   - Update todos to match reality, not memory
```

### Common State Divergence Patterns

| Pattern | What Happens | Fix |
|---------|-------------|-----|
| **Merge amnesia** | Merged PR, context-switched, forgot to update todos | Todo update paired with merge action |
| **Optimistic completion** | Marked done because "it should work" not because it was verified | Gate function above |
| **Stale state** | CI passed 3 turns ago, assumed still passing today | Fresh verification |
| **Ticket drift** | Ticket shows In Progress but you're about to claim Done | Check ticket status before claiming |
| **Cross-session gap** | Resumed session, system says 4/5 done but actual state is different | Periodic reconciliation on resume |

## Why This Matters

From 24 failure memories:
- your human partner said "I don't believe you" - trust broken
- Undefined functions shipped - would crash
- Missing requirements shipped - incomplete features
- Time wasted on false completion → redirect → rework
- Violates: "Honesty is a core value. If you lie, you'll be replaced."

## When To Apply

**ALWAYS before:**
- ANY variation of success/completion claims
- ANY expression of satisfaction
- ANY positive statement about work state
- Committing, PR creation, task completion
- Moving to next task
- Delegating to agents

**Rule applies to:**
- Exact phrases
- Paraphrases and synonyms
- Implications of success
- ANY communication suggesting completion/correctness

## The Bottom Line

**No shortcuts for verification.**

Run the command. Read the output. THEN claim the result.

This is non-negotiable.
