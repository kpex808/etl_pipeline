import os

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from load_cad_snowflake import PROJECT_ROOT, connect

load_dotenv(PROJECT_ROOT / ".env")

st.title("CAD Dashboard")

db = os.environ["SNOWFLAKE_DATABASE"]


def read_sql(conn, sql):
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    cols = [col[0].lower() for col in cur.description]
    return pd.DataFrame(rows, columns=cols)


with connect(warehouse=os.environ["SNOWFLAKE_DASHBOARD_WAREHOUSE"]) as conn:
    kpi = read_sql(conn, f"SELECT * FROM {db}.GOLD.CAD_KPI")
    flybys = read_sql(
        conn,
        f"SELECT * FROM {db}.GOLD.CAD_FLYBYS ORDER BY dist_au ASC LIMIT 100",
    )
    by_day = read_sql(
        conn,
        f"SELECT approach_day, n_approaches FROM {db}.GOLD.CAD_BY_DAY ORDER BY approach_day",
    )

row = kpi.iloc[0]
left, mid, right = st.columns(3)
left.metric("Approaches", int(row["n_approaches"]))
mid.metric("Closest (km)", int(row["min_dist_km"]))
right.metric("Max speed (km/s)", round(float(row["max_speed_kms"]), 1))

st.subheader("Upcoming flybys")
st.dataframe(flybys)

st.subheader("Approaches per day")
st.bar_chart(by_day, x="approach_day", y="n_approaches")
