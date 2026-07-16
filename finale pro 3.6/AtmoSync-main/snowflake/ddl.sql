-- Snowflake DDL for AtmoSync.
-- Mirrors the SQLite schema 1:1 so the dbt models in dbt_atmosync/ run
-- unchanged (or with trivial dialect tweaks) once you point dbt at Snowflake.

CREATE DATABASE IF NOT EXISTS ATMOSYNC;
CREATE SCHEMA IF NOT EXISTS ATMOSYNC.RAW;

USE SCHEMA ATMOSYNC.RAW;

CREATE TABLE IF NOT EXISTS sensor_data (
    id              INTEGER AUTOINCREMENT PRIMARY KEY,
    container_id    VARCHAR,
    temperature     FLOAT,
    humidity        FLOAT,
    vibration       FLOAT,
    battery         INTEGER,
    latitude        FLOAT,
    longitude       FLOAT,
    door_status     VARCHAR,
    spoilage_risk   VARCHAR,
    timestamp       TIMESTAMP_NTZ
);

CREATE TABLE IF NOT EXISTS markets (
    market_id       VARCHAR PRIMARY KEY,
    market_name     VARCHAR,
    latitude        FLOAT,
    longitude       FLOAT
);

CREATE TABLE IF NOT EXISTS commodity_prices (
    id              INTEGER AUTOINCREMENT PRIMARY KEY,
    commodity       VARCHAR,
    market_id       VARCHAR,
    price_per_kg    FLOAT,
    updated_at      TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);
