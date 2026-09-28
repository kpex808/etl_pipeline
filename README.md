# CAD ELT (Snowflake)

NASA/JPL **Close Approach Data** lists predicted times when near-Earth asteroids (and some comets) pass Earth: object name, time, miss distance (AU / km), relative speed.

The public [CAD API](https://ssd-api.jpl.nasa.gov/doc/cad.html) returns that as JSON (`GET`). This project loads it into Snowflake: raw JSON in **Bronze**, flatten/marts as **Dynamic Tables** (Silver/Gold), Streamlit on **Gold**.

It is an ephemeris table (calculated future/past flybys), not a live radar feed. A weekly run is enough.

## Flow

1. GitHub Actions (Mondays 06:00 UTC, or manual): `extract_cad_elt.py` → `load_cad_snowflake.py` → `refresh_cad_dts.py`
2. Bronze `ELT_DEV.BRONZE.CAD_RAW`: one row (`extracted_at` + `payload` VARIANT)
3. Dynamic Tables rebuild Silver/Gold
4. Streamlit reads Gold only (`src/app.py`)

SQL notes: `sql/cad_live.sql`, `sql/cad_dynamic_tables.sql`. `sql/cad_archive.sql` is the learning path (do not run as a whole in Snowflake).

## Why two warehouses?

- **Load / Dynamic Tables:** `SNOWFLAKE_WAREHOUSE` (e.g. Learning-WH). INSERT and DT refresh need compute.
- **Dashboard:** `SNOWFLAKE_DASHBOARD_WAREHOUSE`. Streamlit only `SELECT`s Gold. Separate XSMALL with a short auto-suspend so an app rerun does not wake the load warehouse.

Two warehouses do not mean double cost. Credits accrue only while a warehouse is **running**.

## Why Dynamic Tables with TARGET_LAG 3 days if the Action already runs on Mondays?

The Action owns **extract + load**. Transform stays in Snowflake, not `CREATE OR REPLACE TABLE` in Python.

- **`TARGET_LAG = '3 days'`** (Silver): Snowflake can still catch up if the Action fails or someone loads Bronze only.
- **`TARGET_LAG = DOWNSTREAM`** (Gold): Gold follows Silver, not a second timer.
- **`ALTER DYNAMIC TABLE … REFRESH`** in the Action: on Monday, Gold should match the new Bronze **immediately**, without waiting up to three days.

Lag is a safety net. Refresh in the Action keeps the dashboard current after the cron.

## Local

Python 3.12+, venv, `pip install -r requirements.txt`. Copy `.env.example` to `.env`. Dashboard: `python -m streamlit run src/app.py`. Credentials stay in `.env` / GitHub Actions secrets, not in git.
