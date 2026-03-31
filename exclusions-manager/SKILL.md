---
name: exclusions-manager
description: Use when auditing exclusion data quality, sourcing evidence for exclusion reasons, reviewing classification accuracy, identifying stale or unsourced exclusions, or suggesting changes to the exclusions schema.
---

# Exclusions Manager

Manage the quality, sourcing, and classification accuracy of `exclusions.active_exclusions`.
Supabase MCP is assumed available for all queries.

## Core Mental Model

Three separable tasks — run them together or independently:

1. **Source audit** — find rows with no `evidence_urls`, weak `reason_detail`, or inactive source orgs
2. **Classification review** — verify `sub_category_code` matches the actual conduct described
3. **Currency check** — find rows where the underlying conduct may have changed (company restructured, settled, divested)

## Active Record Definition

An **active exclusion** is a row where:
```sql
valid_to IS NULL AND disposition = 'excluded'
```
Both conditions are required. All queries filtering for "current" exclusions must include both predicates. Rows with `disposition` values other than `'excluded'` (e.g., `'observation'`, `'pipeline'`) are not active exclusions even if `valid_to IS NULL`.

## Immutability Rule

Never UPDATE `sub_category_code` or `source_id`. Corrections to classification require closing the old row (`valid_to = NOW()`) and inserting a corrected new row.

`reason_detail` and `evidence_urls` CAN be updated in-place as evidence improves — these are refinements, not reclassifications.

Other fields safe to UPDATE in-place: `evidence_citation`, `notes`, `review_status`.

## Schema Constraints

### company_id NOT NULL
Enforced by trigger `trg_require_company_id`. Every row must reference a valid `research.companies` record. Bare ticker-only rows are rejected.

### sub_category_code FK → exclusions.taxonomy
All `sub_category_code` values must exist in `exclusions.taxonomy` (58 codes as of 2026-03). Non-canonical codes are rejected by FK constraint. Query `exclusions.taxonomy` for the full list before inserting.

### trg_evidence_gate
Blocks `is_approved = true` without `evidence_urls`. You cannot approve a row that has no evidence.

### is_approved gate
`is_approved = true` means the exclusion is **public-facing on ethicic.com**. The trigger `trg_sync_is_approved` automatically sets this based on:
- `review_status = 'confirmed'` AND `valid_to IS NULL`

The `trg_evidence_gate` prevents approval without evidence. To get a row approved: set `evidence_urls`, then set `review_status = 'confirmed'`.

### Multi-source records
Multiple records per company per category from different sources is **intentional**. Each record represents an independent evidence line with an independent lifecycle (its own `valid_from`/`valid_to`, source, evidence). Never consolidate them into a single row.

## review_status Values

| Value | Meaning |
|-------|---------|
| `cio_approved` | CIO explicitly approved this exclusion |
| `confirmed` | Verified with evidence — triggers `is_approved = true` via `trg_sync_is_approved` |
| `needs_cio_review` | Automated process flagged for human review |
| `needs_source` | Exclusion reason exists but no authoritative source yet |
| `cio_reviewed` | CIO has reviewed but not confirmed (e.g., needs more evidence) |
| `retired_data_quality` | Closed due to data quality issues (bad ticker mapping, duplicate, etc.) |
| `reclassified` | Old row closed because classification was corrected — new row inserted |
| `rejected` | CIO reviewed and rejected — not a valid exclusion |
| `lifted_no_evidence` | Closed — no current evidence supports the exclusion |

---

## Step 1: Orient — What's the Current State?

```sql
-- Overall health snapshot
SELECT
    COUNT(*) FILTER (WHERE valid_to IS NULL AND disposition = 'excluded') AS active_rows,
    COUNT(*) FILTER (WHERE valid_to IS NULL AND disposition = 'excluded' AND evidence_urls IS NULL) AS missing_evidence,
    COUNT(*) FILTER (WHERE valid_to IS NULL AND disposition = 'excluded' AND review_status = 'needs_cio_review') AS needs_cio_review,
    COUNT(*) FILTER (WHERE valid_to IS NULL AND disposition = 'excluded' AND review_status = 'lifted_no_evidence') AS lifted_no_evidence,
    COUNT(DISTINCT company_id) FILTER (WHERE valid_to IS NULL AND disposition = 'excluded') AS distinct_companies
FROM exclusions.active_exclusions;
```

```sql
-- Source breakdown (which sources are covering what)
SELECT
    r.source_name,
    r.source_type,
    r.deprecated,
    COUNT(*) AS rows,
    COUNT(DISTINCT ae.company_id) AS companies,
    MIN(ae.valid_from) AS earliest,
    MAX(ae.valid_from) AS latest,
    COUNT(*) FILTER (WHERE ae.evidence_urls IS NULL) AS missing_evidence
FROM exclusions.active_exclusions ae
JOIN exclusions.reasons r ON ae.source_id = r.id
WHERE ae.valid_to IS NULL AND ae.disposition = 'excluded'
GROUP BY r.source_name, r.source_type, r.deprecated
ORDER BY rows DESC;
```

---

## Step 2: Find Rows Needing Attention

### No evidence URLs (biggest gap)

```sql
SELECT
    ae.symbol,
    ae.sub_category_code,
    ae.reason_detail,
    ae.valid_from,
    s.source_name,
    ae.review_status
FROM exclusions.active_exclusions ae
JOIN exclusions.sources s ON ae.source_id = s.source_id
WHERE ae.valid_to IS NULL
  AND ae.disposition = 'excluded'
  AND ae.evidence_urls IS NULL
  AND ae.review_status IS DISTINCT FROM 'lifted_no_evidence'
ORDER BY s.source_name, ae.sub_category_code, ae.symbol
LIMIT 50;
```

### Flagged for CIO review (no automated evidence found)

```sql
SELECT ae.symbol, ae.sub_category_code, ae.reason_detail, ae.valid_from, s.source_name
FROM exclusions.active_exclusions ae
JOIN exclusions.sources s ON ae.source_id = s.source_id
WHERE ae.valid_to IS NULL
  AND ae.disposition = 'excluded'
  AND ae.review_status = 'needs_cio_review'
ORDER BY ae.valid_from DESC;
```

### Old bulk-import rows (pre-2022, external source, no detail)

```sql
SELECT ae.symbol, ae.sub_category_code, ae.reason_detail, ae.valid_from, s.source_name
FROM exclusions.active_exclusions ae
JOIN exclusions.sources s ON ae.source_id = s.source_id
WHERE ae.valid_to IS NULL
  AND ae.disposition = 'excluded'
  AND ae.valid_from < '2022-01-01'
  AND ae.source_id != 11   -- not ECIC internal
  AND (ae.reason_detail IS NULL OR length(ae.reason_detail) < 30)
ORDER BY s.source_name, ae.symbol
LIMIT 50;
```

### Deprecated source rows still active

```sql
SELECT ae.symbol, ae.sub_category_code, ae.valid_from, s.source_name, s.source_id
FROM exclusions.active_exclusions ae
JOIN exclusions.sources s ON ae.source_id = s.source_id
WHERE ae.valid_to IS NULL
  AND ae.disposition = 'excluded'
  AND s.is_active = FALSE;
```

---

## Step 3: Classification Accuracy

Check that `sub_category_code` is the best-fit code for the conduct described.

```sql
-- Full taxonomy reference (58 codes)
SELECT sub_category_code, sub_category_name, policy_category, parent_category, theme, description
FROM exclusions.taxonomy
ORDER BY parent_category, policy_category, sub_category_name;
```

Red flags for misclassification:
- `multiple_violations` on a row that has a specific conduct description — should use the specific code
- `corporate_misconduct` (parent) without a specific child code when the conduct is clearly weapons, labor, etc.
- `fossil_fuel_ancillary` when the company is a direct producer — should be `oil_gas` or `coal`
- A row in `surveillance_capitalism` situation without `situation_id = 2`

When you find a misclassification:
```sql
-- 1. Close the old row
UPDATE exclusions.active_exclusions
SET valid_to = CURRENT_DATE,
    review_status = 'reclassified',
    notes = CONCAT(COALESCE(notes, ''), ' [Reclassified: was ', sub_category_code, ']')
WHERE id = <row_id>;

-- 2. Insert corrected row (preserve original valid_from)
INSERT INTO exclusions.active_exclusions
    (company_id, symbol, sub_category_code, reason_detail, valid_from, source_id, situation_id, notes, evidence_urls, evidence_citation)
SELECT
    company_id, symbol,
    '<correct_code>',   -- corrected code
    reason_detail, valid_from, source_id, situation_id,
    'Reclassified from <old_code>. ' || COALESCE(notes, ''),
    evidence_urls, evidence_citation
FROM exclusions.active_exclusions
WHERE id = <row_id>;
```

---

## Step 4: Find Authoritative Sources

### Source Registry (from `exclusions.sources`)

These are the institutional sources already registered in the database. Query by `source_id` when adding or attributing rows.

**Primary sources with active exclusion data:**

| source_id | Source | Confidence | Themes Covered | URL |
|-----------|--------|-----------|----------------|-----|
| 11 | ECIC (internal) | 100 | all themes | — |
| 8 | Cruelty Free Investors | 90 | animal_rights, environment, fossil_fuels | — |
| 17 | NBIM | 100 | animal_rights, corporate_misconduct, environment, fossil_fuels, geopolitical_conflict, weapons_military | https://www.nbim.no/en/responsible-investment/ethical-exclusions/exclusion-of-companies/ |
| 1 | AFSC Investigate | 80 | geopolitical_conflict, weapons_military, labor_rights, corporate_misconduct | https://investigate.afsc.org/ |
| 7 | Climate Transition Pathway (TPI) | 80 | fossil_fuels, environment, labor_rights | — |
| 5 | Banking on Climate Chaos | 80 | fossil_fuels, corporate_misconduct | https://www.bankingonclimatechaos.org/ |
| 19 | SIPRI | 100 | weapons_military | https://www.sipri.org/databases/armsindustry |

**Active sources with no current data (priority for sourcing gaps):**

| source_id | Source | Confidence | Best For | URL |
|-----------|--------|-----------|----------|-----|
| 34 | KnowTheChain | 85 | labor_rights, supply chain (tech/apparel/food) | https://www.business-humanrights.org/en/from-us/knowthechain/ |
| 35 | Worth Rises | 85 | criminal_justice (prison industry) | https://data.worthrises.org |
| 37 | National Opioids Settlement | 90 | harmful_products (opioids) | https://nationalopioidsettlement.com/ |
| 38 | NewsGuard | 85 | harmful_products (misinformation) | https://www.newsguardtech.com/ |
| 44 | Forest 500 | 90 | environment (deforestation) | https://forest500.org |
| 45 | Trase | 90 | environment (supply chain deforestation) | https://trase.earth |
| 46 | OpenSecrets (Dark Money) | 92 | corporate_misconduct (political spending) | https://www.opensecrets.org |
| 27 | UFLPA Entity List (DHS) | 50 | labor_rights (forced labor, Uyghur) | https://www.dhs.gov/uflpa-entity-list |
| 4 | As You Sow | 80 | environment, fossil_fuels, corporate_misconduct | https://www.asyousow.org/ |
| 42 | First Peoples Worldwide | 80 | indigenous_rights | https://firstpeoplesworldwide.org/ |
| 36 | Break Free From Plastic | 80 | environment (plastics) | https://www.breakfreefromplastic.org/ |
| 41 | Environmental Working Group | 80 | environment, harmful_products (pesticides) | https://www.ewg.org/ |
| 40 | Food & Water Watch | 80 | environment, harmful_products (food safety) | https://www.foodandwaterwatch.org/ |
| 6 | Business & Human Rights Resource Centre | 80 | indigenous_rights, labor_rights, geopolitical_conflict | https://www.business-humanrights.org/ |
| 31 | WhoProfits Research Center | 5 | geopolitical_conflict (I/P supply chain) | https://whoprofits.org/ |
| 29 | ICIJ Offshore Leaks Database | 5 | corporate_misconduct (tax, corruption) | https://offshoreleaks.icij.org/ |

**Inactive/deprecated sources (do not assign new rows):**

| source_id | Source | Status |
|-----------|--------|--------|
| 18 | Observation | Inactive — disposition tag, not an org |
| 24 | Yahoo! Finance | Inactive — 9 legacy rows, re-source or lift |
| 28 | NBIM - Government Pension Fund Global | Merged into source_id=17 |
| 21 | Stockholm International Peace Research Institute | Merged into source_id=19 |
| 30 | SIPRI Arms Industry Database | Merged into source_id=19 |

**For evidence not covered by the above, also search:**

| Source | Best For | URL |
|--------|----------|-----|
| ViolationTracker (Good Jobs First) | Corporate fines, OSHA, NLRB, DOJ, EPA | https://violationtracker.goodjobsfirst.org/ |
| SEC EDGAR Litigation | Financial misconduct, fraud settlements | https://efts.sec.gov/LATEST/search-index |
| NLRB Case Search | Labor violations, union-busting | https://www.nlrb.gov/case/ |
| DOJ Press Releases | Criminal fines, settlements | https://www.justice.gov/news |
| EPA ECHO | Environmental violations | https://echo.epa.gov/facilities/facility-search |

Use `research-tools` skill (or `WebFetch`/`WebSearch`) to look up specific companies. Target: a URL that directly documents the conduct, plus a formal citation if available.

### Updating evidence fields (safe in-place update)

```sql
UPDATE exclusions.active_exclusions
SET
    evidence_urls = ARRAY['https://violationtracker.goodjobsfirst.org/...'],
    evidence_citation = 'Good Jobs First ViolationTracker, accessed 2026-03-10',
    notes = CONCAT(COALESCE(notes, ''), ' [Evidence added 2026-03-10]')
WHERE id = <row_id>;
```

To append to existing evidence_urls:
```sql
UPDATE exclusions.active_exclusions
SET
    evidence_urls = array_cat(COALESCE(evidence_urls, ARRAY[]::text[]), ARRAY['https://new-source-url']),
    notes = CONCAT(COALESCE(notes, ''), ' [Additional evidence added 2026-03-19]')
WHERE id = <row_id>;
```

---

## Step 5: Currency Check

External lists (CFI, NBIM, AFSC, TPI) were imported at a point in time. Companies may have:
- Divested the flagged business unit
- Changed ownership (spinoff, merger, delisting)
- Settled the underlying violation and made operational changes

```sql
-- Companies with only external-source rows AND no ECIC internal row
-- (candidates for staleness review — ECIC never independently confirmed)
SELECT ae.symbol, STRING_AGG(s.source_name, ', ') AS sources, MIN(ae.valid_from) AS oldest_row
FROM exclusions.active_exclusions ae
JOIN exclusions.sources s ON ae.source_id = s.source_id
WHERE ae.valid_to IS NULL
  AND ae.disposition = 'excluded'
GROUP BY ae.symbol
HAVING COUNT(*) FILTER (WHERE ae.source_id = 11) = 0  -- no ECIC row
ORDER BY oldest_row
LIMIT 50;
```

```sql
-- Lifecycle check: rows for companies Sharadar shows as delisted
-- (may still be valid — track via company_id, not ticker)
SELECT ae.symbol, ae.sub_category_code, ae.lifecycle_status, ae.valid_from, r.source_name
FROM exclusions.active_exclusions ae
JOIN exclusions.reasons r ON ae.source_id = r.id
WHERE ae.valid_to IS NULL
  AND ae.disposition = 'excluded'
  AND ae.lifecycle_status = 'delisted'
ORDER BY ae.symbol;
```

To lift an exclusion with insufficient evidence:
```sql
UPDATE exclusions.active_exclusions
SET valid_to = CURRENT_DATE,
    review_status = 'lifted_no_evidence',
    notes = CONCAT(COALESCE(notes, ''), ' [Lifted: no current evidence found, CIO review ', CURRENT_DATE, ']')
WHERE id = <row_id>;
```

---

## Step 6: Suggest New Exclusions

When research surfaces companies not yet in the list:

```sql
-- Check if a ticker is already excluded
SELECT ae.symbol, ae.sub_category_code, ae.reason_detail, ae.valid_from
FROM exclusions.active_exclusions ae
WHERE ae.symbol = 'TICKER'
  AND ae.valid_to IS NULL
  AND ae.disposition = 'excluded';

-- Find company_id (required for new rows — trg_require_company_id enforces this)
SELECT id AS company_id, name, ticker
FROM research.companies
WHERE ticker = 'TICKER';

-- Add new exclusion
INSERT INTO exclusions.active_exclusions
    (company_id, symbol, sub_category_code, reason_detail, valid_from,
     source_id, evidence_urls, evidence_citation, notes)
VALUES
    (<company_id>, 'TICKER', '<sub_category_code>',
     'Specific conduct description referencing the source',
     CURRENT_DATE,
     11,  -- source_id=11 for ECIC internal decisions
     ARRAY['https://primary-source-url'],
     'Source Name, Publication Date or Case Number',
     'Added after [research session date] review');
```

---

## Coverage Gaps to Address

Known thin areas (as of 2026-03-10):

| Theme/Code | Gap | Suggested Action |
|------------|-----|-----------------|
| `indigenous_rights` | 0 rows — code exists, no data | Research Standing Rock, Line 3, DAPL companies |
| `child_labor` | 0 rows | KnowTheChain tech/apparel supply chain rankings |
| `fur_exotic_skins` | 0 rows | Cruelty Free International fur list |
| Yahoo Finance source (id=24) | 9 legacy rows, low confidence | Re-source each to a primary source or lift |
| CFI list (id=8) | 2019–2022 snapshot, not refreshed | Check CFI current list for additions/removals |
| NBIM list (id=17) | Last import 2023 | Check NBIM current exclusion list for updates |

---

## Quick Reference

| Task | SQL/Action |
|------|-----------|
| Active row count | `WHERE valid_to IS NULL AND disposition = 'excluded'` |
| Missing evidence | `AND evidence_urls IS NULL` |
| Needs CIO attention | `AND review_status = 'needs_cio_review'` |
| Close a row | `SET valid_to = CURRENT_DATE` |
| Lift with no evidence | `SET review_status = 'lifted_no_evidence'` |
| Add evidence (in-place) | Update `evidence_urls`, `evidence_citation`, `notes` only |
| Update narrative (in-place) | Update `reason_detail` with improved text |
| Add new exclusion | INSERT with `source_id=11`, `company_id` required, `evidence_urls` as text array |
| Reclassify | Close old row (review_status='reclassified') → INSERT corrected row |
| Approve for website | Set `review_status = 'confirmed'` (triggers `is_approved = true` via `trg_sync_is_approved`) — requires `evidence_urls` |
