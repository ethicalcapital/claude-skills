---
name: data-app-ui-review
description: Comprehensive UI/UX review for data apps, dashboards, and analytics tools. Evaluates clarity, visual hierarchy, accessibility, interactivity, and data visualization best practices.
version: 1.0.0
---

# Data App UI Review Skill

This skill enables Claude to provide expert-level UI critique for data applications, dashboards, analytics platforms, and data visualization systems.

## Activation Triggers

Use this skill when you need to:
- Critique a data dashboard or analytics UI
- Review data visualization effectiveness
- Evaluate accessibility of a data app
- Get structured feedback on an interactive analytics interface
- Assess visual hierarchy and information architecture of a BI tool

## Core Review Framework

### 1. Visual Hierarchy & Layout (Score: 0-2)

**Evaluation Points:**
- Most important information visually prominent (position, size, color, weight)?
- Adequate white space preventing cognitive overload?
- Consistent grid alignment and spacing?
- Natural scanning patterns supported (F-pattern for dashboards)?
- Text hierarchy clear (font sizes, weights, colors)?

**What to Look For:**
- Dashboard title immediately tells users the purpose
- Key metrics featured prominently in upper left/center
- Supporting details lower priority
- Minimum 12pt font for readability
- Clear visual emphasis on actionable insights

---

### 2. Data Visualization Quality (Score: 0-2)

**Evaluation Points:**
- Chart type matches data type appropriately?
- Proportions and scales accurate (bars start at zero)?
- Color usage meaningful and accessible?
- Data labels clear and complete?
- Title conveys insight, not just data?
- No excessive decoration (chart junk removed)?

**Critical Checks:**
- ✓ Bar charts for comparison
- ✓ Line charts for trends over time
- ✓ Scatter plots for relationships
- ✗ Pie charts with >3 segments
- ✗ Dual-axis charts without justification
- ✗ 3D effects or gratuitous animation

**Accessibility:** Colorblind-friendly palette? Sufficient contrast (WCAG AA)?

---

### 3. Clarity & Information Design (Score: 0-2)

**Evaluation Points:**
- Chart titles convey insight ("Revenue Up 23% YoY" not "Revenue")?
- Context provided (current period, baseline, target)?
- Units clearly indicated?
- Annotations explaining anomalies or trends?
- Legends positioned logically?
- Text contrast sufficient (4.5:1 minimum)?

**Scoring:**
- 2 = All information crystal clear at a glance
- 1 = Understandable but requires cognitive effort
- 0 = Confusing or misleading

---

### 4. Interactivity & User Control (Score: 0-2)

**Evaluation Points:**
- Relevant filters available (by time, dimension, metric)?
- Drill-down capabilities for exploration?
- Interactive elements obviously interactive (hover states, buttons)?
- Loading states visible during data fetch?
- Errors clearly communicated?
- Reset or undo functionality available?
- Interactions feel responsive (<500ms)?

**User Control Assessment:**
- Can users answer their own questions?
- Is the interaction model intuitive?
- Are advanced users supported?

---

### 5. Responsiveness & Accessibility (Score: 0-2)

**Evaluation Points:**
- Graceful degradation on mobile screens?
- Touch targets adequate (44x44px minimum)?
- Keyboard navigation fully supported?
- Screen reader compatible?
- Color not sole differentiator?
- Content density appropriate?
- Page load time acceptable (<3 seconds)?

**WCAG Compliance Check:**
- Color contrast: 4.5:1 for text (AA standard)
- Alt text for images/charts
- Keyboard accessible (all functions)
- Distinguishable (not color-only)

---

### 6. Usefulness & Task Alignment (Score: 0-2)

**Evaluation Points:**
- Data relevant to intended audience?
- Supports primary user workflows?
- Jargon minimized?
- Actionable (enables decision-making)?
- Essential information present (no critical gaps)?
- Avoid redundant displays?

---

## Structured Feedback Template

When reviewing, provide feedback in this format:

### Strengths (2-3 highlights)
- What works well and why

### Critical Issues (Priority 1)
- **Issue Name**
  - Current state: What's happening
  - Impact: Why it matters
  - Fix: Specific, actionable recommendation

### Improvements (Priority 2)
- **Category**: Issue
  - Recommendation: How to address

### Accessibility Notes
- Specific concerns or wins

### Overall Score
- Visual Hierarchy: [0-2]
- Data Visualization: [0-2]
- Clarity: [0-2]
- Interactivity: [0-2]
- Accessibility: [0-2]
- Usefulness: [0-2]
- **Total: [0-12]**

---

## Key Principles

1. **Clarity Over Decoration** - Every pixel serves a purpose
2. **Proportional Accuracy** - Visual = Data relationship
3. **Provide Context** - Benchmarks, targets, history matter
4. **User-Centric** - Design for your user, not design trends
5. **Accessible First** - Works for everyone, including those with disabilities
6. **Performance Counts** - Beautiful + slow = useless
7. **Consistency Rules** - Same interactions everywhere

---

## Data App Red Flags ⚠️

- Pie charts with >3 segments
- Unlabeled axes or missing context
- Animations without purpose
- >5 colors in single visualization
- No error states designed
- Text overlapping or hard to read
- Inconsistent date/number formatting
- No export/action capability
- Dashboard drowning in metrics
- Unclear data source or recency

---

## How to Request a Review

**Good request:**
> "Review this [dashboard/analytics page]. Target users are portfolio managers tracking daily returns. They need to spot anomalies quickly. Are my KPI cards prominent enough? Is the price chart clear?"

**What to provide:**
- Screenshot or description of the UI
- Intended users and use cases
- Primary tasks they perform
- Specific areas you want feedback on
