---
name: cynical-schema-review
description: Use when reviewing database schema designs before implementation - ruthlessly identifies type mismatches, missing constraints, orphaned data risks, performance issues, edge cases, and migration failure points through systematic critical analysis
---

# Cynical Schema Review

<EXTREMELY-IMPORTANT>
This skill is for BEFORE you finalize a schema design, not after.

If you're about to write CREATE TABLE statements that will touch production data, you MUST use this skill first.

Why: Schema mistakes are expensive. Type mismatches cause migration failures. Missing constraints create orphaned data. Denormalization creates staleness. Edge cases become data corruption. Performance issues emerge at scale.

A cynic catches these BEFORE they're in production.
</EXTREMELY-IMPORTANT>

## When to Use This Skill

Use this skill when:
- Finalizing a database schema design
- Before migration scripts
- Reviewing schema proposals from other agents/developers
- User asks for "critical review", "cynical eye", "what could go wrong"
- About to touch production data with new table structures

DO NOT use this skill for:
- API design reviews
- Code reviews (use code-reviewer agent instead)
- Application architecture (unless database-focused)

## The Cynic's Mindset

A good schema review assumes:
1. **Nothing is as it seems** - Data types in documentation are wrong until verified
2. **Everything will break** - Find the edge case that orphans records
3. **Users lie** - Stated requirements miss critical workflows
4. **Data is dirty** - NULL handling, duplicates, encoding issues matter
5. **Scale reveals sins** - Joins that work on 100 rows fail on 1M rows
6. **History matters** - Point-in-time tracking or you lose audit trail
7. **Migration is half the battle** - Schema looks great but how do you populate it?

## Review Framework

### Phase 1: Data Type Verification (TIER 1 - SHOW-STOPPERS)

**Before you review the schema logic, verify the ACTUAL data types in the source system.**

NEVER trust:
- Documentation (often outdated)
- Assumptions (VARCHAR vs INTEGER breaks everything)
- External schema descriptions (they may have transformed data)

ALWAYS verify:
- Query `information_schema.columns` for actual types
- Sample actual data: `SELECT DISTINCT typeof(column) FROM table LIMIT 100`
- Check for NULL patterns, encoding issues, unexpected formats

**Checklist:**
- [ ] Every column type verified against actual source data (not docs)
- [ ] Assumed foreign key types match their parent tables EXACTLY
- [ ] String length limits based on actual max values (not guesses)
- [ ] Numeric types appropriate for scale (INTEGER vs BIGINT, DECIMAL precision)
- [ ] Date/timestamp types handle timezone requirements
- [ ] BOOLEAN vs VARCHAR('Y'/'N') vs INTEGER(0/1) patterns identified

**Common failures:**
- Assuming `permaticker INTEGER` when source has `VARCHAR` → migration fails
- Using `VARCHAR(20)` when actual data has 50-char values → truncation
- `REFERENCES company(cik)` when cik is TEXT not INTEGER → type mismatch

### Phase 2: Constraint Analysis (TIER 1 - SHOW-STOPPERS)

**Every business rule should have a database constraint, or you WILL get dirty data.**

NEVER assume:
- Application logic prevents duplicates (it doesn't)
- Users follow conventions (they won't)
- Referential integrity is "obvious" (orphans appear immediately)

ALWAYS define:
- PRIMARY KEY on every table (or explain why not)
- UNIQUE constraints on business keys (not just technical PKs)
- CHECK constraints for data invariants
- NOT NULL on required fields
- FOREIGN KEY relationships with CASCADE policies

**Checklist:**
- [ ] Every table has PRIMARY KEY (or documented exception)
- [ ] Business natural keys have UNIQUE constraints
- [ ] No duplicate prevention = duplicates WILL happen (document risk)
- [ ] All foreign keys defined (not just "implied by naming")
- [ ] CASCADE DELETE/UPDATE policies explicit (not default behavior)
- [ ] CHECK constraints for enum-like values, ranges, business rules
- [ ] NOT NULL on columns that truly can't be NULL

**Common failures:**
- Exclusions table without unique constraint on (company_id, category_code, valid_from) → duplicates
- No CASCADE policy on deletion → orphaned records
- Missing NOT NULL on "required" fields → sparse data breaks queries
- No CHECK(company_id IS NOT NULL OR security_id IS NOT NULL) → invalid rows

### Phase 3: Denormalization & Staleness (TIER 2 - IMPORTANT)

**Every denormalized field is a future bug waiting to happen.**

Denormalization patterns:
- Copying `ticker` to multiple tables (ticker changes!)
- Copying `company_name` everywhere (acquisitions rename!)
- Computed flags like `is_in_investable_universe` (market cap changes!)
- Generated columns that reference external data (Sharadar updates!)

ALWAYS ask:
- What happens when the source value changes?
- How do we detect staleness?
- What's the update strategy? (triggers? batch jobs? manual?)
- Is the performance gain worth the consistency risk?

**Checklist:**
- [ ] Every denormalized field marked with comment about staleness risk
- [ ] Update strategy documented (trigger, batch job, manual, acceptable stale)
- [ ] Alternative design without denormalization considered
- [ ] If kept: indexed for the query pattern that justified it

**Common failures:**
- `ticker VARCHAR(20)` on holdings table → stale after ticker change
- `company_name` everywhere → inconsistent after M&A
- `is_in_investable_universe BOOLEAN` → wrong after market cap drops
- No update mechanism = stale data guaranteed

### Phase 4: Temporal Data & History (TIER 2 - IMPORTANT)

**If you can't answer "what did this look like on 2024-03-15?", you're missing history.**

Temporal patterns:
- Point-in-time queries (portfolio composition on specific date)
- Audit trail (who changed what when)
- Effective dating (valid_from/valid_to)
- Change tracking (old_value → new_value)

NEVER assume:
- Current state is enough (it's not for compliance/auditing)
- You can reconstruct history from timestamps (you can't)
- Users won't need "last reviewed" tracking (they always do)

ALWAYS ask:
- Do we need point-in-time reconstruction?
- Is there an audit requirement?
- What about "last reviewed" or "last verified" dates?
- Can we track WHEN something became true, not just THAT it's true?

**Checklist:**
- [ ] Audit fields (created_at, updated_at, created_by, updated_by) on mutable tables
- [ ] History tables for critical entity changes (or valid_from/valid_to)
- [ ] "Last reviewed" pattern where humans verify data
- [ ] No DELETE operations that lose history (soft delete with valid_to instead)
- [ ] Change reason/notes for critical transitions

**Common failures:**
- Single `last_reviewed_at` timestamp → can't see review history
- No tick_history table → can't reconstruct score changes
- Deleting exclusions instead of setting valid_to → lost audit trail
- No updated_by field → can't track who made changes

### Phase 5: Index & Performance (TIER 2 - IMPORTANT)

**The query that works on 1,000 rows fails on 1,000,000 rows without indexes.**

Index patterns:
- Foreign keys (JOIN targets)
- WHERE clause columns (filtering)
- ORDER BY columns (sorting)
- Composite indexes for multi-column queries

NEVER assume:
- "We'll add indexes later" (you'll forget which queries matter)
- Database auto-indexes foreign keys (some DBs don't)
- One index per table is enough (complex queries need multiple)

ALWAYS document:
- Expected table sizes (1K? 1M? 1B rows?)
- Primary query patterns (WHAT gets queried HOW often?)
- Join strategies (which FKs are hot paths?)

**Checklist:**
- [ ] Expected row counts documented for each table
- [ ] Primary query patterns identified (top 5 queries)
- [ ] Foreign key columns indexed
- [ ] WHERE clause columns indexed (ticker, category_code, valid_to IS NULL)
- [ ] Composite indexes for common multi-column filters
- [ ] No indexes on write-heavy tables without justification

**Common failures:**
- No index on `exclusions.company_id` → slow lookups
- No index on `exclusions.valid_to` → slow "active only" queries
- No index on `strategy_holdings.security_id` → slow portfolio queries
- Over-indexing low-cardinality columns (is_excluded BOOLEAN)

### Phase 6: Migration Feasibility (TIER 1 - SHOW-STOPPERS)

**A perfect schema is useless if you can't populate it from existing data.**

Migration questions:
- Where does data come from? (CSV, existing DB, API?)
- How do we map old structure → new structure?
- What about unmapped data? (254 AFSC rows, 938 CSV-only exclusions)
- Are there data quality issues blocking migration? (NULLs, duplicates)

NEVER assume:
- "We'll figure out migration later" (schema might be unmappable)
- Clean source data (there are always NULLs, duplicates, encoding issues)
- 1:1 field mapping (transformations needed, data loss likely)

ALWAYS document:
- Source → target mapping for EVERY field
- Transformation logic (parsing, splitting, lookups)
- Data quality issues from pre-migration analysis
- Unmapped edge cases and their resolution

**Checklist:**
- [ ] Migration source(s) identified for every table
- [ ] Field-by-field mapping documented (old.column → new.column)
- [ ] Transformation logic specified (split CSV, parse codes, lookup FKs)
- [ ] Edge cases identified (AFSC rows, CSV-only data, missing IDs)
- [ ] Data quality issues documented (duplicates, NULLs, format errors)
- [ ] Migration script skeleton exists (even if pseudocode)

**Common failures:**
- Beautiful schema, no migration path → can't implement
- Forgot about 254 AFSC rows with source in wrong field → data loss
- Assumed clean 1:1 mapping → 938 CSV-only rows unmapped
- No plan for company_id population when permaticker missing → orphans

### Phase 7: Edge Cases & Invariants (TIER 3 - DESIGN CONCERNS)

**The edge case you ignore becomes the production bug.**

Edge case patterns:
- NULL handling (is NULL a valid state or data quality issue?)
- Orphaned references (what if company_id points to deleted company?)
- Circular dependencies (A references B, B references A)
- State transitions (valid → invalid → valid again?)
- Multi-source conflicts (CSV says exclude, DB says include)

ALWAYS ask:
- What happens if this foreign key points to nothing?
- Can this field be NULL? Should it be?
- What if two sources disagree?
- Is there a state that's theoretically invalid but practically possible?

**Checklist:**
- [ ] NULL semantics documented for every nullable column
- [ ] Orphaned reference handling (CASCADE? RESTRICT? SET NULL?)
- [ ] Multi-source conflict resolution strategy
- [ ] Invalid state prevention (CHECK constraints or docs)
- [ ] Delisting, M&A, ticker changes handled
- [ ] International vs US data boundaries (CIK = US only)

**Common failures:**
- Companies table allows NULLs everywhere → sparse data
- No handling for delisted companies → active/inactive confusion
- Exclusions can have both company_id AND security_id → ambiguous
- No conflict resolution when CSV and DB disagree

### Phase 8: Reference vs Duplication (TIER 2 - IMPORTANT)

**Every duplicated field is a synchronization problem.**

Reference patterns:
- Don't duplicate Sharadar data (JOIN to sharadar.tickers)
- Don't duplicate EODHD data (JOIN to eodhd tables)
- DO store business logic (exclusions, tick scores, strategies)
- DO cache for performance (but document staleness)

NEVER assume:
- "It's just one field" (that one field becomes 10, becomes unmaintainable)
- "We need it for performance" (measure first, optimize second)
- "The source won't change" (tickers change, companies merge, data updates)

ALWAYS ask:
- Is this data owned by us or by Sharadar/EODHD?
- Can we JOIN instead of COPY?
- If we MUST copy, what's the update strategy?

**Checklist:**
- [ ] External data referenced via JOIN, not copied
- [ ] Business logic (exclusions, scores) in our tables
- [ ] Justified denormalizations have update strategy
- [ ] No "because it's convenient" duplication

**Common failures:**
- Copying company_name, sector, industry from Sharadar → stale data
- Duplicating ISIN/CUSIP lookups → maintenance burden
- Not documenting WHICH system owns WHICH data

## Output Format

When using this skill, produce a tiered analysis:

**TIER 1: SHOW-STOPPERS** (blocks implementation)
- Data type mismatches
- Missing critical constraints
- Unmappable migrations
- Referential integrity violations

**TIER 2: IMPORTANT** (causes problems in production)
- Missing indexes on hot paths
- Denormalization without update strategy
- No audit trail for compliance
- Performance issues at scale

**TIER 3: DESIGN CONCERNS** (technical debt/future pain)
- Edge cases not handled
- Unclear NULL semantics
- Convenience duplications
- Missing documentation

## TodoWrite Integration

This skill has checklists. When using this skill, create TodoWrite todos for each review phase:

```json
[
  {"content": "Phase 1: Verify data types", "status": "pending", "activeForm": "Verifying data types"},
  {"content": "Phase 2: Analyze constraints", "status": "pending", "activeForm": "Analyzing constraints"},
  {"content": "Phase 3: Check denormalization", "status": "pending", "activeForm": "Checking denormalization"},
  {"content": "Phase 4: Review temporal patterns", "status": "pending", "activeForm": "Reviewing temporal patterns"},
  {"content": "Phase 5: Plan indexes", "status": "pending", "activeForm": "Planning indexes"},
  {"content": "Phase 6: Verify migration path", "status": "pending", "activeForm": "Verifying migration path"},
  {"content": "Phase 7: Document edge cases", "status": "pending", "activeForm": "Documenting edge cases"},
  {"content": "Phase 8: Check duplications", "status": "pending", "activeForm": "Checking duplications"}
]
```

## Example Critique Format

```
# Schema Review: [Schema Name]

## TIER 1: SHOW-STOPPERS (Implementation Blockers)

### Issue 1: Data Type Mismatch - permaticker
**Problem**: Schema assumes `permaticker INTEGER UNIQUE`, but source data may be VARCHAR
**Impact**: Migration will fail if permaticker contains alphanumeric values
**Evidence**: User noted "WE assigned varchar to the csvs" - type needs verification
**Fix**: Query actual data type, update schema accordingly

### Issue 2: Missing Unique Constraint
**Problem**: exclusions table has no unique constraint on business key
**Impact**: Duplicate exclusions WILL be inserted, causing data integrity issues
**Evidence**: No UNIQUE(company_id, category_code, valid_from) defined
**Fix**: Add unique constraint on natural business key

## TIER 2: IMPORTANT (Production Problems)

### Issue 3: Denormalized ticker field
**Problem**: ticker copied to strategy_holdings table
**Impact**: Stale after ticker changes (IBM → INTC after acquisition)
**Evidence**: No update trigger or batch job defined
**Fix**: Remove denormalization, JOIN to securities table

[... continue for all issues ...]

## Summary
- Tier 1: 5 show-stoppers (MUST fix before implementation)
- Tier 2: 8 important issues (fix in v1.1 or accept risk)
- Tier 3: 13 design concerns (document for future)
```

## Anti-Patterns (What NOT to do)

**Don't:**
- Review schema without querying actual data types
- Accept "we'll add indexes later" without documenting patterns
- Ignore migration complexity ("we'll figure it out")
- Assume foreign key relationships (verify them)
- Skip documentation because "the names are obvious"
- Rubber-stamp designs because user seems confident
- Approve denormalization without update strategy

**Why:** Schemas live forever. Mistakes compound. Data corruption scales. Migrations fail. Production breaks.

A cynic prevents these problems by assuming everything will fail and proving it won't.

## Final Question

After completing the review, ask yourself:

**"If I had to migrate 10 million rows of dirty production data into this schema at 3am on a Sunday, what would break?"**

If you can't answer confidently "nothing," you're not done reviewing.
