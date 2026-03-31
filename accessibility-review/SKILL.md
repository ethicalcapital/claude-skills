---
name: accessibility-review
description: >
  Use when creating, modifying, or reviewing any output that humans will consume —
  web pages, PDFs, emails, forms, research notes, client documents, slide decks,
  or data visualizations. Triggers on: new component, template change, PDF generation,
  email template edit, form modification, content page creation, "is this accessible",
  "a11y check", "screen reader", "WCAG", or any client-facing deliverable.
---

# Accessibility Review

Accessibility is not a web-only concern. Every output — web pages, PDFs, emails, data
tables, printed documents — must be usable by people who navigate differently. Our
clients include people with disabilities. Our exclusion research covers companies that
harm disabled communities. We cannot credibly do that work while producing inaccessible
output ourselves.

**Standard:** WCAG 2.2 AA baseline. PDF/UA (ISO 14289) for documents.

## When to Apply

**Always** when touching:
- Web components, pages, layouts, styles
- Email templates (Supabase, Resend)
- PDF generation (Typst, ReportLab)
- Forms (intake, onboarding, any interactive)
- Data visualizations, charts, dashboards
- Research notes that render on ethicic.com
- Slide decks or client-facing documents

**Especially** when:
- Adding color, changing contrast, modifying typography
- Building interactive components (dropdowns, modals, multi-step flows)
- Generating documents for client signatures or regulatory filing
- Creating content about disability, chronic illness, or neurodivergence

## The Audit — By Output Type

### Web (Astro + Tailwind + React)

Our stack already has strong foundations. Verify they're maintained:

| Check | How | Reference |
|-------|-----|-----------|
| **Heading hierarchy** | Single `<h1>`, sequential h2→h3→h4, no skipped levels | All layouts enforce this |
| **Color contrast** | Use `--color-teal-accessible` (#0f766e, 4.6:1) for teal text. All text ≥ 4.5:1 on background | `packages/design-tokens/src/tokens.css` |
| **Link distinction** | Inline links must be underlined (not color-only). Prose links already styled | `global.css` line ~154 |
| **Focus indicators** | `focus:ring-2 focus:ring-[var(--color-purple)]` with offset | Form components in `website/src/app/forms/ui/` |
| **Skip link** | Present in `SiteLayout.tsx` — verify not removed | `website/src/app/components/layout/SiteLayout.tsx` |
| **Images** | Meaningful: descriptive `alt`. Decorative: `alt=""` or `aria-hidden="true"` | Check every `<img>` and `<svg>` |
| **Forms** | `htmlFor` + `id` on every input. `aria-invalid` + `aria-describedby` for errors. `role="alert"` on error messages | FormInput, FormSelect, FormCheckbox patterns |
| **Reduced motion** | `@media (prefers-reduced-motion: reduce)` disables animations | `global.css` |
| **Language** | `lang="en"` on `<html>` | `BaseLayout.astro` |
| **Keyboard nav** | All interactive elements reachable via Tab. No keyboard traps. Escape closes modals | Manual test |

**Run automated checks:**
```bash
cd website && npm run test:a11y        # Unit tests (vitest-axe)
npx playwright test e2e/a11y-audit     # Full route audit (axe-core)
```

### PDFs (Typst + ReportLab)

PDF accessibility is a known gap. For every PDF:

| Check | Requirement |
|-------|-------------|
| **Tagged structure** | Headings, paragraphs, lists must be tagged (not just visually styled). Typst outputs tagged PDF by default — verify with `pdfinfo` or Adobe Acrobat's accessibility checker |
| **Reading order** | Logical, matches visual order. Multi-column layouts must tag reading sequence |
| **Alt text** | Every chart, logo, or decorative element needs alt text or artifact marking |
| **Language** | Document language set in metadata |
| **Font embedding** | All fonts fully embedded (Outfit, Raleway). No font substitution |
| **Color alone** | No information conveyed by color alone — use labels, patterns, or icons |
| **Contrast** | Text on colored backgrounds ≥ 4.5:1. Purple (#581c87) on white is fine; white on purple is fine. Check any other combinations |

**ReportLab limitation:** `report_writer/md_to_pdf.py` produces untagged PDFs. If generating
compliance documents or anything a client must read, prefer Typst output. If ReportLab is
required, add `AccessibleParagraph` wrappers or flag the document as needing post-processing
in Adobe Acrobat for tagging.

### Emails (Supabase templates)

Templates at `supabase/templates/`:

| Check | Requirement |
|-------|-------------|
| **`lang` attribute** | `<html lang="en">` — currently missing, add it |
| **Semantic structure** | Use `<h1>`, `<h2>`, `<p>` — not just styled `<td>`. Already good |
| **Table layout** | Layout tables must have `role="presentation"`. Already present |
| **Link text** | "Click here" is banned. Links must describe destination. "Confirm your email" not "Click here to confirm" |
| **Button contrast** | CTA buttons must have ≥ 4.5:1 text-to-background. Purple (#581c87) + white passes |
| **Link underlines** | Add `text-decoration: underline` to links in body text (WCAG 2.2) |
| **Plain text fallback** | Transactional emails should degrade to readable plain text |
| **Image alt** | If adding logos as `<img>`, include `alt="Ethical Capital"` |

### Data Visualizations & Charts

| Check | Requirement |
|-------|-------------|
| **Color + redundant encoding** | Never convey meaning by color alone. Use labels, patterns, or icons alongside color |
| **Alt text / description** | Charts need either `alt` text (if `<img>`) or a `<figcaption>` + `aria-label` describing the key takeaway |
| **Data table fallback** | Complex charts should have an accessible data table alternative (visible or sr-only) |
| **Axis labels** | Always label axes. Units included |
| **Contrast** | Data series must be distinguishable at 3:1 contrast against adjacent colors and background |

### Research Notes & Exclusion Narratives

Content that renders on ethicic.com/exclusions/{ticker}/:

| Check | Requirement |
|-------|-------------|
| **Heading hierarchy** | Follows page template's hierarchy (exclusion detail pages start at h2) |
| **Link text** | Sources linked with descriptive text, not bare URLs |
| **Abbreviations** | First use expanded: "Norway's Government Pension Fund Global (NBIM)" not just "NBIM" |
| **Tables** | If using tables in markdown, include header row. Screen readers rely on `<th>` |
| **Reading level** | Plain prose, short sentences. Exclusion narratives are public-facing — write for a general audience, not just analysts |

### Client Documents (agreements, IPS, disclosures)

| Check | Requirement |
|-------|-------------|
| **Fillable forms** | If using PDF forms, every field must have a label. Tab order must be logical |
| **Signature blocks** | Include printed name + title text fields, not just signature image area |
| **Font size** | Body text ≥ 11pt. Footnotes ≥ 9pt. Never below 8pt for any text |
| **Line spacing** | ≥ 1.5x for body text (WCAG 1.4.12) |
| **Paragraph spacing** | ≥ 2x font size between paragraphs |

## Quick Decision Tree

```
Creating/modifying output?
  ├─ Web page/component → Run axe tests + check table above
  ├─ PDF → Check tagged structure + reading order + alt text
  ├─ Email template → Check lang attr + link text + contrast
  ├─ Data viz → Color redundancy + alt text + data table fallback
  ├─ Research note → Heading hierarchy + link text + abbreviations
  └─ Client document → Font size + spacing + fillable field labels
```

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Decorative image with no `alt` | Add `alt=""` (empty string, not missing) |
| Color-only link distinction | Add underline or icon |
| "Click here" link text | Use destination description |
| Skipped heading level (h2 → h4) | Insert h3 or restructure |
| Chart with no text alternative | Add `aria-label` with key finding or data table |
| PDF with visual-only headings | Use Typst heading syntax, not just bold text |
| Form error without `role="alert"` | Add `role="alert"` + `aria-describedby` |
| Multi-step form loses focus | Programmatically move focus to first field of new step |
| Email template missing `lang` | Add `<html lang="en">` |
| Hardcoded colors bypassing tokens | Use `var(--color-*)` tokens from design system |

## Integration with Other Skills

- **writing-exclusions**: Narratives must follow the research notes accessibility checks above
- **typeset-pdf**: PDFs must meet the document accessibility checks
- **ecic-brand**: Brand colors are pre-checked for contrast; use the accessible variants
- **compliance-analyst**: Marketing materials must be accessible as a regulatory baseline (ADA, Section 508 if serving government entities)
- **anti-racist-review**: Accessibility is an intersectional concern — disabled people of color, disabled trans people, etc. Don't treat accessibility as separate from equity review
