---
name: investment-analysis
description: Structured logical analysis for investment decisions - validates theses, detects biases, tests assumptions, and creates auditable decision workflows. Use for investment thesis validation, divestment analysis, impact assessment, or any complex analytical decision requiring transparent reasoning.
---

<EXTREMELY-IMPORTANT>
This skill transforms complex investment analysis from free-form reasoning into structured, auditable workflows that expose assumptions, detect cognitive biases, test robustness, and create defensible decision trails.

**MANDATORY WORKFLOW**: Every analysis must produce structured output with explicit:
- Problem statement and decision framework
- All assumptions (explicit and hidden)
- Evidence with source assessment
- Bias detection and mitigation
- Sensitivity analysis
- Confidence calibration
- Audit trail
</EXTREMELY-IMPORTANT>

# Investment Analysis Skill

## When to Use This Skill

Use this skill for ANY complex analytical decision, including:

- **Investment Thesis Validation**: Breaking down investment hypotheses into testable components
- **Divestment Analysis**: Structuring arguments for divesting from holdings
- **Impact Assessment**: Evaluating actual (not projected) impact of investment decisions
- **Ethical Screening Logic**: Applying screening policy consistently across holdings
- **Risk Attribution & Causal Analysis**: Understanding what actually drives performance
- **Scenario Analysis**: Exploring how assumptions drive conclusions
- **Multi-Criteria Decisions**: Handling trade-offs between competing objectives

## Core Principles

1. **Structured Over Free-Form**: Use frameworks, not stream-of-consciousness
2. **Explicit Over Implicit**: State all assumptions, don't hide them
3. **Rigorous Over Convenient**: Test sensitivity, don't assume robustness
4. **Transparent Over Opaque**: Create audit trails, not black boxes
5. **Humble Over Confident**: Quantify uncertainty, don't pretend certainty

## MANDATORY Analysis Workflow

Every analysis MUST follow this structure:

```yaml
ANALYSIS:
  problem_statement: "What decision are we making? Why now?"

  decision_framework: "Which framework applies?"
    # Options: Investment Thesis, Divestment, Impact Assessment, MCDA, Causal Inference

  scope_definition:
    what_is_included: [...]
    what_is_excluded: [...]
    key_entities_affected: [...]
    time_horizon: "..."

  assumptions:
    explicit_assumptions:
      - assumption: "..."
        type: "observable|predictive|model|implicit"
        criticality: "high|medium|low"
        confidence: "high|medium|low"
        validation_method: "How can we test this?"

    hidden_assumptions: [...]
      # Claude MUST uncover unstated assumptions

  evidence:
    - claim: "..."
      sources: [...]
      reliability: "high|medium|low"
      contradictory_evidence: [...]

  reasoning_steps:
    - step: "..."
      logic: "..."
      conclusion: "..."

  bias_check:
    cognitive_biases_detected: [...]
    logical_fallacies_found: [...]
    conflicts_with_prior_beliefs: [...]
    mitigation_actions: [...]

  counterarguments:
    strongest_opposing_argument: "..."
    response_to_opposition: "..."
    residual_concerns: [...]

  sensitivity_analysis:
    critical_variables:
      - variable: "..."
        base_case: "..."
        test_range: [min, max]
        breakeven_point: "At what value does conclusion flip?"
        robustness: "high|medium|low"

    scenario_results: [...]

  conclusions:
    - conclusion: "..."
      confidence: "high|medium|low"
      confidence_rationale: "Why this confidence level?"
      key_uncertainty: "What don't we know?"

  recommendation: "What should we do?"

  uncertainty_acknowledgment:
    - "What would change your mind?"
    - "What would make you more confident?"
    - "What's the biggest unknown?"

  audit_trail:
    analyst: "..."
    date: "YYYY-MM-DD"
    reviewer: "..."
    data_sources: [...]
    key_subjective_judgments: [...]
```

## Step-by-Step Execution

When you invoke this skill, you MUST:

### 1. Problem Definition Phase

**TodoWrite Checklist**:
- [ ] State the decision being made
- [ ] Identify decision framework to use
- [ ] Define scope (included, excluded, affected parties)
- [ ] Establish time horizon

**Questions to Answer**:
- What exactly are we deciding?
- Why are we making this decision now?
- Who is affected by this decision?
- What are the boundaries of this analysis?

### 2. Assumption Mapping Phase

**TodoWrite Checklist**:
- [ ] List all explicit assumptions
- [ ] Uncover hidden assumptions
- [ ] Categorize each assumption (observable, predictive, model, implicit)
- [ ] Rate criticality of each assumption
- [ ] Identify validation methods

**Critical Task**: For EACH assumption, ask:
- "How do we know this is true?"
- "What evidence supports this?"
- "What would prove this wrong?"
- "How critical is this to our conclusion?"

### 3. Evidence Gathering Phase

**TodoWrite Checklist**:
- [ ] Document all evidence for key claims
- [ ] Assess reliability of each source
- [ ] Identify contradictory evidence
- [ ] Note data gaps

**Red Flags**:
- All evidence supports one view (confirmation bias)
- Recent events dominate (availability heuristic)
- Evidence from only friendly sources (in-group bias)

### 4. Reasoning Construction Phase

**TodoWrite Checklist**:
- [ ] Lay out reasoning steps explicitly
- [ ] Connect evidence to conclusions
- [ ] Identify logical leaps
- [ ] Check for fallacies

**Standard**: Someone reading this should be able to:
- Follow the logic from evidence to conclusion
- Identify where judgment was applied
- Reconstruct the reasoning independently

### 5. Bias Detection Phase

**MANDATORY**: Run through bias checklist (see reference/cognitive-biases.md)

**TodoWrite Checklist**:
- [ ] Check for confirmation bias
- [ ] Check for availability heuristic
- [ ] Check for anchoring bias
- [ ] Check for sunk cost fallacy
- [ ] Check for status quo bias
- [ ] Check for in-group bias
- [ ] Check for logical fallacies

For each bias detected, document mitigation action.

### 6. Counterargument Phase

**TodoWrite Checklist**:
- [ ] Generate strongest opposing argument
- [ ] Address opposition directly
- [ ] Identify residual concerns
- [ ] Note what would change your mind

**Critical**: This is NOT a strawman exercise. Build the STRONGEST version of the opposing view.

### 7. Sensitivity Analysis Phase

**TodoWrite Checklist**:
- [ ] Identify critical variables
- [ ] Test each across reasonable range
- [ ] Find breakeven points
- [ ] Assess robustness

**Questions**:
- At what point does the recommendation flip?
- Which assumptions matter most?
- How much cushion do we have?

### 8. Conclusion & Recommendation Phase

**TodoWrite Checklist**:
- [ ] State conclusions with confidence levels
- [ ] Provide rationale for confidence
- [ ] Identify key uncertainties
- [ ] Make clear recommendation
- [ ] Document what would change your mind

### 9. Audit Trail Phase

**TodoWrite Checklist**:
- [ ] Document analyst and date
- [ ] List all data sources
- [ ] Note key subjective judgments
- [ ] Identify who decided what
- [ ] Ensure future auditability

## Templates Available

Use these templates for specific analysis types:

- `templates/thesis-validation.md` - Investment thesis validation
- `templates/assumption-testing.md` - Assumption stress testing
- More templates can be added as needed

## Reference Materials

- `reference/cognitive-biases.md` - Comprehensive bias detection guide
- `reference/logical-fallacies.md` - Common fallacies to avoid

## Examples

- `examples/example-thesis.md` - Worked example of thesis validation

## Critical Success Factors

✅ **Explicitness Over Elegance**: Detailed reasoning beats concise conclusions
✅ **Assumption Obsession**: Question everything assumed rather than proven
✅ **Bias Awareness**: Actively look for ways analysis could be wrong
✅ **Stakeholder Clarity**: Make subjective judgments explicit
✅ **Robustness Testing**: Verify conclusions hold across assumption ranges
✅ **Audit Trail**: Future you can understand present you's reasoning

## What This Skill Does NOT Do

❌ Make decisions for you (you decide, this structures your reasoning)
❌ Remove uncertainty (it quantifies and acknowledges it)
❌ Replace judgment (it elevates judgment with rigor)
❌ Guarantee right answers (it reduces preventable errors)

## Integration Points

- **Data Sources**: Self-hosted Nhost PostgreSQL on rawls (credentials via Doppler: project rawls, env dev)
- **Screening Policy**: Reference https://ethicic.com/content/process/screening-policy
- **Ethical Framework**: Align with firm's values and impact objectives
- **Credential Management**: Always use `doppler run --` for database access
- **GraphQL API**: Self-hosted Hasura endpoint available for queries

## Output Format

All analyses should produce:
1. **Structured YAML/JSON output** (machine-readable audit trail)
2. **Executive summary** (human-readable conclusion)
3. **Supporting documentation** (detailed reasoning)
4. **Sensitivity tables** (robustness evidence)

This ensures decisions are:
- Transparent (anyone can follow the logic)
- Auditable (future review is possible)
- Rigorous (biases are detected and mitigated)
- Defensible (assumptions are tested)

---

**Remember**: This skill doesn't replace your judgment. It makes your judgment better by ensuring it rests on solid analytical foundations rather than intuition or confirmation bias.
