-- ==========================================================
-- CSV : Telco Customer Churn
-- ==========================================================

CREATE TABLE IF NOT EXISTS csv_customers (
    customer_id      VARCHAR(50) PRIMARY KEY,
    gender           VARCHAR(10) NOT NULL,
    senior_citizen   INTEGER NOT NULL,
    tenure           INTEGER NOT NULL,
    phone_service    VARCHAR(10) NOT NULL,
    contract         VARCHAR(30) NOT NULL,
    monthly_charges  NUMERIC(10,2) NOT NULL,
    total_charges    NUMERIC(10,2),
    churn            VARCHAR(5) NOT NULL,
    loaded_at        TIMESTAMP DEFAULT NOW()
);


-- ==========================================================
-- REST API Posts
-- ==========================================================

CREATE TABLE IF NOT EXISTS api_posts (
    source_id     INTEGER PRIMARY KEY,
    user_id       INTEGER NOT NULL,
    title         TEXT NOT NULL,
    body          TEXT NOT NULL,
    loaded_at     TIMESTAMP DEFAULT NOW()
);


-- ==========================================================
-- Mongo Users
-- ==========================================================

CREATE TABLE IF NOT EXISTS mongo_users (
    mongo_id      VARCHAR(100) PRIMARY KEY,
    name          VARCHAR(255) NOT NULL,
    email         VARCHAR(255) NOT NULL,
    age           INTEGER NOT NULL,
    country       CHAR(2) NOT NULL,
    is_active     BOOLEAN NOT NULL,
    tags          TEXT[],
    loaded_at     TIMESTAMP DEFAULT NOW()
);


-- ==========================================================
-- ETL Run Log
-- ==========================================================

CREATE TABLE IF NOT EXISTS etl_run_log (
    id                 SERIAL PRIMARY KEY,
    run_id             VARCHAR(100) UNIQUE NOT NULL,
    source             VARCHAR(50) NOT NULL,
    records_valid      INTEGER NOT NULL DEFAULT 0,
    records_invalid    INTEGER NOT NULL DEFAULT 0,
    status             VARCHAR(20) NOT NULL,
    started_at         TIMESTAMP NOT NULL,
    finished_at        TIMESTAMP DEFAULT NOW()
);