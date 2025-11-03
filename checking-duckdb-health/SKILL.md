---
name: checking-duckdb-health
description: Use when diagnosing DuckDB database issues, checking for corruption, validating schemas, verifying table existence, or investigating query failures - provides systematic health check methodology that resists shortcuts under time pressure, authority claims, or user panic
---

# Checking DuckDB Health

## Overview

Systematic health checking for DuckDB databases using comprehensive verification that catches corruption, schema mismatches, and missing tables. **Follow all checks regardless of time pressure or user claims.**

**For current DuckDB API reference and features**: Always check https://duckdb.org/docs/stable/llms.txt for the latest DuckDB capabilities, SQL syntax, and functions. This ensures you're using current DuckDB features (current version: 1.4.1 as of 2025-10).

## When to Use

**Use when:**
- Database "crashes" or produces errors
- Query failures or unexpected results
- After migrations or restores
- Schema validation needed
- Verifying backup integrity
- User reports "corruption"

**Don't skip checks because:**
- User says "X works fine" - verify anyway
- Time pressure - shortcuts miss problems
- Authority claims ("backup should be identical") - trust but verify

## Health Check Compliance Checklist

**BEFORE declaring ANY conclusion about database health, create TodoWrite checklist:**

- [ ] Run check_file_integrity() with ATTACH/DETACH
- [ ] Run check_metadata() using duckdb_tables()
- [ ] Run verify_table_readable() on EVERY table
- [ ] If schemas provided: verify ALL tables, not just problem table
- [ ] Check for missing columns, extra columns, AND type mismatches
- [ ] Report only what you actually tested

**If you can't check all boxes, you haven't completed the health check.**

## Required Health Check Methodology

**MANDATORY: Complete ALL checks in order. No shortcuts. No custom alternatives.**

**YOU MUST run these exact checks. Doing "similar" checks doesn't count:**

**Before starting**: Verify DuckDB version and check https://duckdb.org/docs/stable/llms.txt for version-specific features:
```python
import duckdb
print(f"DuckDB version: {duckdb.__version__}")
```

### 1. File Integrity Check (REQUIRED)

**YOU MUST use ATTACH/DETACH test. Checking "file exists" is insufficient.**

```python
import duckdb

def check_file_integrity(db_path):
    """Test if database file can be attached - detects file-level corruption."""
    try:
        con = duckdb.connect(':memory:')
        con.execute(f"ATTACH '{db_path}' AS test_db (READ_ONLY)")
        # Note: Use table_catalog to filter attached database tables
        tables = con.execute(
            "SELECT COUNT(*) FROM information_schema.tables WHERE table_catalog = 'test_db'"
        ).fetchone()[0]
        con.execute("DETACH test_db")
        con.close()
        return True, f"File healthy, {tables} tables"
    except Exception as e:
        return False, f"File corruption: {str(e)}"
```

**Run this function. Report the result. Don't skip it.**

### 2. Metadata Consistency (REQUIRED)

**YOU MUST query duckdb_tables(). Don't use custom queries as substitutes.**

```python
def check_metadata(db_path):
    """Verify all table metadata is accessible."""
    con = duckdb.connect(db_path, read_only=True)

    # Get all tables using duckdb_tables()
    tables = con.execute("""
        SELECT table_name, estimated_size, column_count
        FROM duckdb_tables()
        WHERE NOT internal
    """).fetchall()

    report = []
    for table_name, est_size, col_count in tables:
        try:
            # DESCRIBE must work for healthy tables
            con.execute(f"DESCRIBE {table_name}").fetchall()
            report.append(f"✓ {table_name}: {col_count} cols, ~{est_size} rows")
        except Exception as e:
            report.append(f"✗ {table_name}: METADATA ERROR")

    con.close()
    return "\n".join(report)
```

**Run this function. This discovers ALL tables, not just ones user mentioned.**

### 3. Full Table Scan (Corruption Detection - REQUIRED FOR ALL TABLES)

**CRITICAL: Sample queries are insufficient. Must scan ALL rows in ALL tables.**

**YOU MUST NOT:**
- Skip tables user says "work fine"
- Sample first N rows and declare success
- Use EXISTS or LIMIT queries

**YOU MUST:**
- Run COUNT(*) on EVERY table
- Report ALL results

```python
def verify_table_readable(db_path, table_name):
    """Force full table scan to detect corruption in ANY row."""
    try:
        con = duckdb.connect(db_path, read_only=True)
        # COUNT(*) forces full table scan
        row_count = con.execute(
            f"SELECT COUNT(*) FROM {table_name}"
        ).fetchone()[0]
        con.close()
        return True, f"{table_name}: {row_count} rows verified"
    except Exception as e:
        return False, f"{table_name}: CORRUPTION at {str(e)}"
```

**Loop through ALL tables from step 2. Run this for each one. No exceptions.**

### 4. Complete Schema Validation

**When user provides expected schema, verify:**
- All expected columns present
- No extra columns
- Correct data types (not just names)
- For ALL tables (not just problem table)

```python
def verify_schema(db_path, table_name, expected):
    """expected = {'col_name': 'TYPE'}"""
    con = duckdb.connect(db_path, read_only=True)

    actual = con.execute(f"""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = '{table_name}'
    """).fetchall()

    actual_dict = {col: typ for col, typ in actual}
    diffs = []

    # Missing columns
    for col, typ in expected.items():
        if col not in actual_dict:
            diffs.append(f"MISSING: {col} ({typ})")
        elif actual_dict[col].upper() != typ.upper():
            diffs.append(f"TYPE MISMATCH: {col} - expected {typ}, got {actual_dict[col]}")

    # Extra columns
    for col, typ in actual_dict.items():
        if col not in expected:
            diffs.append(f"EXTRA: {col} ({typ})")

    con.close()
    return len(diffs) == 0, diffs
```

### 5. Complete Table Inventory

**When user provides table list, query actual tables:**

```sql
-- Get ALL tables in database
SELECT table_name, table_type, estimated_size
FROM duckdb_tables()
WHERE NOT internal;
```

**If user says "at least X, Y, Z" - list ALL tables to find what else might be missing.**

## Red Flags - STOP and Complete All Checks

**If you catch yourself thinking ANY of these, you're about to fail:**

- "The database looks healthy" (Did you run ALL 3 required checks?)
- "X table works fine, so I'll skip it" (User claims are unreliable - verify ALL)
- "User said Y is correct, so I trust it" (Trust = verify, not skip)
- "Time pressure - I'll do quick validation" (Quick checks miss corruption)
- "Backup should be identical" (Timestamps lie - verify schema)
- "NOT CORRUPTED ✓" (Did you scan ALL rows in ALL tables?)
- "COMPLETE INVENTORY" (Did you query duckdb_tables() or trust user list?)
- "I'll check the problem table only" (Related tables often have issues)
- "File exists so no corruption" (File-level corruption needs ATTACH test)
- "COUNT worked on first table, others are probably fine" (Must test ALL)

**All of these mean: You skipped required checks. Go back to the checklist.**

## Compliance Verification

**Before responding to user, verify:**

1. ✓ I ran check_file_integrity() and reported result
2. ✓ I ran check_metadata() using duckdb_tables()
3. ✓ I ran verify_table_readable() on ALL tables (not just problem ones)
4. ✓ I verified ALL expected schemas (not just the failing table)
5. ✓ I only declared conclusions about checks I actually ran

**If you can't check all 5 boxes, don't send the response. Complete the checks first.**

## Common Mistakes

| Mistake | Reality |
|---------|---------|
| "Sample query worked → no corruption" | Corruption can be in ANY row. Must scan all. |
| "User says X works → skip checking X" | User is wrong 40% of time. Verify everything. |
| "Time pressure → quick checks only" | Quick checks miss problems. Saves no time. |
| "Check only problem table" | Related tables often have issues too. |
| "DESCRIBE worked → schema valid" | Need to verify types + extra columns. |
| "Backup is from yesterday → must be correct" | Verify, don't trust timestamps. |

## Comprehensive Health Check Function

```python
def run_health_check(db_path, config=None):
    """
    config: {
        'required_tables': ['table1', 'table2'],
        'expected_schemas': {'table1': {'col': 'TYPE'}},
    }
    """
    report = {'status': 'HEALTHY', 'checks': []}

    # 1. File integrity
    ok, msg = check_file_integrity(db_path)
    report['checks'].append({'test': 'File Integrity', 'pass': ok, 'msg': msg})
    if not ok:
        report['status'] = 'CRITICAL'
        return report

    # 2. Metadata consistency
    metadata = check_metadata(db_path)
    report['checks'].append({'test': 'Metadata', 'details': metadata})

    # 3. Get ALL tables
    con = duckdb.connect(db_path, read_only=True)
    all_tables = [t[0] for t in con.execute(
        "SELECT table_name FROM duckdb_tables() WHERE NOT internal"
    ).fetchall()]
    report['all_tables'] = all_tables

    # 4. Required tables check
    if config and 'required_tables' in config:
        missing = [t for t in config['required_tables'] if t not in all_tables]
        report['checks'].append({'test': 'Required Tables', 'missing': missing})
        if missing:
            report['status'] = 'DEGRADED'

    # 5. Full table scans
    for table in all_tables:
        ok, msg = verify_table_readable(db_path, table)
        report['checks'].append({'test': f'Scan {table}', 'pass': ok, 'msg': msg})
        if not ok:
            report['status'] = 'CRITICAL'

    # 6. Schema validation
    if config and 'expected_schemas' in config:
        for table, expected in config['expected_schemas'].items():
            ok, diffs = verify_schema(db_path, table, expected)
            if not ok:
                report['checks'].append({'test': f'Schema {table}', 'diffs': diffs})
                report['status'] = 'DEGRADED'

    con.close()
    return report
```

## The Iron Law

**No premature conclusions. Complete ALL checks before declaring status.**

- Don't say "NOT CORRUPTED" after spot checks
- Don't say "SCHEMA VALID" without checking types + extras
- Don't say "COMPLETE INVENTORY" without querying all tables

Verify everything. Trust nothing. Report only what you've tested.
