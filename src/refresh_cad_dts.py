import os

from dotenv import load_dotenv

from load_cad_snowflake import PROJECT_ROOT, connect


def refresh_dynamic_tables() -> None:
    database = os.environ["SNOWFLAKE_DATABASE"]
    tables = [
        f"{database}.SILVER.CAD",
        f"{database}.GOLD.CAD_FLYBYS",
        f"{database}.GOLD.CAD_KPI",
        f"{database}.GOLD.CAD_BY_DAY",
    ]
    with connect(os.environ["SNOWFLAKE_WAREHOUSE"]) as conn:
        with conn.cursor() as cur:
            for name in tables:
                sql = f"ALTER DYNAMIC TABLE {name} REFRESH"
                print(sql)
                cur.execute(sql)
    print("Fertig")


if __name__ == "__main__":
    load_dotenv(PROJECT_ROOT / ".env")
    refresh_dynamic_tables()
