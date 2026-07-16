# Migrating AtmoSync from SQLite to Snowflake

You're currently running the full pipeline (Kafka → SQLite → dbt → Superset)
against `atmosync.db`. This is the checklist to swap the warehouse layer
to Snowflake without touching your Kafka or dbt model logic.

## 1. Get a Snowflake trial
https://signup.snowflake.com — free 30-day trial, no card required for the
free tier. Note your account identifier, username, password, and the
default warehouse name (e.g. `COMPUTE_WH`).

## 2. Create the schema
Run `snowflake/ddl.sql` in a Snowflake worksheet (or via `snowsql`). It
mirrors the SQLite schema 1:1.

## 3. Load existing data (optional, for historical rows)
Export from SQLite and load via Snowflake's web UI "Load Data" wizard, or:

```bash
sqlite3 atmosync.db -header -csv "select * from sensor_data;" > sensor_data.csv
sqlite3 atmosync.db -header -csv "select * from markets;" > markets.csv
sqlite3 atmosync.db -header -csv "select * from commodity_prices;" > commodity_prices.csv
```
Then upload each CSV via Snowflake's Load Data wizard (Data → Databases →
ATMOSYNC → RAW → table → Load Data), matching it to the table you created.

## 4. Point the Kafka consumer at Snowflake instead of SQLite
`streaming/consumer.py` currently writes via `sqlite3.connect`. Swap that
block for the `snowflake-connector-python` client (already in
requirements.txt):

```python
import snowflake.connector

conn = snowflake.connector.connect(
    account="<your_account>",
    user="<your_user>",
    password="<your_password>",
    warehouse="COMPUTE_WH",
    database="ATMOSYNC",
    schema="RAW",
)
cursor = conn.cursor()
# same INSERT statement, just swap ? placeholders for %s
```

Recommend pulling credentials from environment variables / a `.env` file
(not committed) rather than hardcoding them — `python-dotenv` is already in
requirements.txt for this.

## 5. Point dbt at Snowflake
Replace `dbt_atmosync/profiles.yml` with:

```yaml
atmosync:
  target: dev
  outputs:
    dev:
      type: snowflake
      account: "<your_account>"
      user: "<your_user>"
      password: "<your_password>"
      role: "ACCOUNTADMIN"
      database: "ATMOSYNC"
      warehouse: "COMPUTE_WH"
      schema: "ANALYTICS"
      threads: 4
```

You'll also need `dbt-snowflake` instead of `dbt-sqlite`:
```bash
pip install dbt-snowflake
```

Model SQL needs near-zero changes — the marts already avoid SQLite-only
syntax. One thing to check: `spoilage_arbitrage.sql` previously used a
manual row_number()-based "latest reading" pattern instead of `QUALIFY`
because SQLite doesn't support it. On Snowflake you could simplify back to
`QUALIFY row_number() over (...) = 1` if you want, but the current version
works fine as-is on both.

## 6. Point Superset at Snowflake
Settings → Database Connections → + Database → Snowflake, and use the
`snowflake-sqlalchemy` connector (Superset's official image ships with it).
URI format:
```
snowflake://<user>:<password>@<account>/ATMOSYNC/ANALYTICS?warehouse=COMPUTE_WH&role=ACCOUNTADMIN
```
Re-point your existing dashboard's datasets to the new database connection
— charts stay the same.
