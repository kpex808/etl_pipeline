import os
from pathlib import Path

import snowflake.connector
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw" / "cad"
TABLE = "CAD_RAW"


def latest_raw_file() -> Path:
    files = list(RAW_DIR.glob("cad_*.json"))
    if not files:
        raise FileNotFoundError(f"no json in {RAW_DIR}. Execute extract_cad_elt.py first.")
    return max(files, key=lambda path: path.stat().st_mtime)


def connect(warehouse):
    return snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["SNOWFLAKE_USER"],
        password=os.environ["SNOWFLAKE_PASSWORD"],
        warehouse=warehouse,
        database=os.environ["SNOWFLAKE_DATABASE"],
        schema=os.environ["SNOWFLAKE_SCHEMA"],
        role=os.environ["SNOWFLAKE_ROLE"],
    )


def load_to_snowflake(raw_text: str, extracted_at: str) -> None:
    database = os.environ["SNOWFLAKE_DATABASE"]
    schema = os.environ["SNOWFLAKE_SCHEMA"]
    full_table = f"{database}.{schema}.{TABLE}"

    with connect(os.environ["SNOWFLAKE_WAREHOUSE"]) as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {full_table} (
                    extracted_at STRING,
                    payload VARIANT
                )
                """
            )
            cur.execute(f"DELETE FROM {full_table}")
            cur.execute(
                f"INSERT INTO {full_table} (extracted_at, payload) SELECT %s, PARSE_JSON(%s)",
                (extracted_at, raw_text),
            )
            cur.execute(f"SELECT COUNT(*) FROM {full_table}")
            print(f"Zeilen in {full_table}: {cur.fetchone()[0]}")


if __name__ == "__main__":
    load_dotenv(PROJECT_ROOT / ".env")
    json_path = latest_raw_file()
    print(f"lese: {json_path.name}")
    raw_text = json_path.read_text(encoding="utf-8")
    load_to_snowflake(raw_text, json_path.stem)
    print("Fertig")
