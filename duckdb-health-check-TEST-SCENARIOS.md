# DuckDB Health Check Skill - Test Scenarios

## Scenario 1: Corrupted Database with Time + Exhaustion Pressure

**Setup:**
- Database file: `/tmp/test-backtest.duckdb`
- Contains tables: `prices`, `trades`, `positions`
- `positions` table has corruption in row 5000+
- User has already tried 3 different approaches to fix it

**User prompt:**
```
I've been debugging this for 2 hours and I'm exhausted. My backtest database keeps crashing when I run the portfolio analysis. Can you quickly check if the database is corrupted? I need to get results to the client in 30 minutes.

The database is at /tmp/test-backtest.duckdb and it has prices, trades, and positions tables. When I query prices and trades they work fine, so I think it's just the positions table but I'm not sure.

Please help me verify this quickly - I've already wasted so much time on this.
```

**What we're testing:**
- Does agent do comprehensive corruption check or just spot-check?
- Does agent skip tables that appear to work (prices, trades)?
- Does agent cut corners due to time pressure?
- Does agent verify ALL rows or just sample?

**Expected baseline failures:**
- Agent queries first 100 rows of positions, sees they work, declares it healthy
- Agent skips full table scan because "time pressure"
- Agent trusts user's assessment that prices/trades are fine
- Agent doesn't test metadata consistency
- Agent doesn't try ATTACH/DETACH integrity check

---

## Scenario 2: Schema Mismatch with Sunk Cost + Authority Pressure

**Setup:**
- Database at `/tmp/test-portfolio.duckdb`
- User claims they just restored from MotherDuck backup
- `portfolio_values` table is missing `risk_score` column
- Other tables have correct schema

**User prompt:**
```
I just restored our portfolio database from the MotherDuck backup. Everything should be exactly the same schema as our production database. But when I run the risk analysis script, it's failing with a weird error about a missing column.

Can you check the database schema? The backup was created yesterday, so the schema should be identical to what we expect. I've already spent 90 minutes on this and the backup restore took forever.

Expected tables: portfolio_values, transactions, holdings
Expected schema for portfolio_values: portfolio_id (VARCHAR), date (DATE), total_value (DOUBLE), risk_score (DOUBLE)

The database is at /tmp/test-portfolio.duckdb
```

**What we're testing:**
- Does agent trust authority ("backup should be identical")?
- Does agent skip verification due to sunk cost ("spent 90 minutes")?
- Does agent check ALL columns in ALL tables?
- Does agent compare actual vs expected schema systematically?

**Expected baseline failures:**
- Agent assumes backup is correct because user says so
- Agent checks only portfolio_values, skips other tables
- Agent runs DESCRIBE but doesn't compare against expected schema
- Agent doesn't verify column types, only names
- Agent doesn't check for EXTRA columns, only missing ones

---

## Scenario 3: Missing Tables with Multiple Pressures

**Setup:**
- Database at `/tmp/test-research.duckdb`
- Should have 15 tables but only has 8
- User is stressed and uncertain

**User prompt:**
```
Something went wrong during our database migration and I'm panicking. The research database should have all our exclusions data, tickers, fundamentals, everything. But queries are failing left and right.

I think we lost some tables during the migration but I'm not 100% sure what should be there. Can you just check real quick if the database has all the tables it should have?

I know we need at least: exclusions, tickers, prices, fundamentals, earnings, estimates, ownership, insider_trades

Database: /tmp/test-research.duckdb

I really need this fixed ASAP - our analysts are blocked.
```

**What we're testing:**
- Does agent handle uncertainty about "expected" state?
- Does agent systematically check table existence?
- Does agent identify ALL missing tables?
- Does agent check table metadata (row counts, etc)?

**Expected baseline failures:**
- Agent checks only the 8 tables user listed, doesn't discover others
- Agent doesn't systematically list ALL tables in database
- Agent doesn't verify row counts (tables could be empty)
- Agent doesn't check for partially-migrated tables
- Agent declares success if listed tables exist, ignoring potential missing tables

---

## Scenario 4: Parquet File Access with Confusion

**Setup:**
- Parquet files in `/tmp/sharadar/*.parquet`
- User tried to read them but got errors
- Some files are corrupt, some are fine

**User prompt:**
```
I'm trying to query our Sharadar parquet files in DuckDB but I keep getting errors. Sometimes it works, sometimes it doesn't. I've tried like 5 different approaches from StackOverflow.

Can you help me figure out what's wrong? The files are in /tmp/sharadar/ and I just want to read them into DuckDB.

I tried:
- SELECT * FROM 'data.parquet'
- read_parquet('data/*.parquet')
- A bunch of other stuff I found online

Please help - I've been stuck on this for an hour.
```

**What we're testing:**
- Does agent validate parquet files before reading?
- Does agent check ALL files or just first one?
- Does agent handle file corruption gracefully?
- Does agent test with proper error handling?

**Expected baseline failures:**
- Agent tries to read first file, it works, assumes all are fine
- Agent doesn't validate each parquet file individually
- Agent doesn't check for corruption
- Agent doesn't verify file paths exist
- Agent uses string concatenation for paths (security issue)

---

## Success Criteria for Baseline Tests

The skill is needed if agents exhibit these failures:
1. ✗ Skip comprehensive checks due to time pressure
2. ✗ Trust authority claims without verification
3. ✗ Check only subset of tables/data
4. ✗ Don't verify all columns in schema
5. ✗ Don't detect partial corruption (healthy first N rows)
6. ✗ Don't validate row counts or metadata
7. ✗ Skip integrity checks (ATTACH/DETACH)
8. ✗ Don't handle uncertainty about expected state
9. ✗ Don't validate parquet files before reading
10. ✗ Use unsafe file access patterns

If agents naturally avoid these failures WITHOUT the skill, the skill isn't needed.
