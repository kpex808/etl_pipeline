-- Bronze Table + Dynamic Tables

CREATE DATABASE IF NOT EXISTS ELT_DEV;
CREATE SCHEMA IF NOT EXISTS ELT_DEV.BRONZE;
CREATE SCHEMA IF NOT EXISTS ELT_DEV.SILVER;
CREATE SCHEMA IF NOT EXISTS ELT_DEV.GOLD;

CREATE TABLE IF NOT EXISTS ELT_DEV.BRONZE.CAD_RAW (
    extracted_at STRING,
    payload VARIANT
);

CREATE DYNAMIC TABLE IF NOT EXISTS ELT_DEV.SILVER.CAD
    TARGET_LAG = '3 days'
    WAREHOUSE = SNOWFLAKE_LEARNING_WH
AS
SELECT
    f.value[0]::STRING AS designation,
    f.value[3]::STRING AS approach_at,
    f.value[4]::FLOAT AS dist_au,
    f.value[7]::FLOAT AS v_rel_kms
FROM ELT_DEV.BRONZE.CAD_RAW,
LATERAL FLATTEN(input => payload:data) f;

--How close in km?
CREATE DYNAMIC TABLE IF NOT EXISTS ELT_DEV.GOLD.CAD_FLYBYS
    TARGET_LAG = DOWNSTREAM
    WAREHOUSE = SNOWFLAKE_LEARNING_WH
AS
SELECT
    designation,
    approach_at,
    dist_au,
    ROUND(dist_au * 149597870.7, 0) AS dist_km,
    v_rel_kms,
    CASE
        WHEN dist_au < 0.01 THEN 'very close'
        WHEN dist_au < 0.03 THEN 'close'
        ELSE 'moderate'
    END AS closeness
FROM ELT_DEV.SILVER.CAD;

--How many approaches? closest distance, max. speed
CREATE DYNAMIC TABLE IF NOT EXISTS ELT_DEV.GOLD.CAD_KPI
    TARGET_LAG = DOWNSTREAM
    WAREHOUSE = SNOWFLAKE_LEARNING_WH
AS
SELECT
    COUNT(*) AS n_approaches,
    MIN(dist_au) AS min_dist_au,
    ROUND(MIN(dist_au) * 149597870.7, 0) AS min_dist_km,
    MAX(v_rel_kms) AS max_speed_kms
FROM ELT_DEV.SILVER.CAD;

--Approaches per day
CREATE DYNAMIC TABLE IF NOT EXISTS ELT_DEV.GOLD.CAD_BY_DAY
    TARGET_LAG = DOWNSTREAM
    WAREHOUSE = SNOWFLAKE_LEARNING_WH
AS
SELECT
    TO_DATE(TO_TIMESTAMP_NTZ(approach_at, 'YYYY-MON-DD HH24:MI')) AS approach_day,
    COUNT(*) AS n_approaches,
    MIN(dist_au) AS min_dist_au
FROM ELT_DEV.SILVER.CAD
GROUP BY 1;
