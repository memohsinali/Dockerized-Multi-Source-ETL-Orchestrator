-- Customers (from CSV)
CREATE TABLE IF NOT EXISTS csv_customers (
    id          SERIAL PRIMARY KEY,
    source_id   INT NOT NULL,
    name        VARCHAR(255) NOT NULL,
    email       VARCHAR(255) NOT NULL,
    signup_date DATE NOT NULL,
    country     CHAR(2) NOT NULL,
    loaded_at   TIMESTAMP DEFAULT NOW()
);

-- Posts (from REST API)
CREATE TABLE IF NOT EXISTS api_posts (
    id          SERIAL PRIMARY KEY,
    user_id     INT NOT NULL,
    source_id   INT NOT NULL,
    title       TEXT NOT NULL,
    body        TEXT NOT NULL,
    loaded_at   TIMESTAMP DEFAULT NOW()
);

-- Products (from MongoDB)
CREATE TABLE IF NOT EXISTS mongo_products (
    id           SERIAL PRIMARY KEY,
    mongo_id     VARCHAR(50) NOT NULL,
    product_name VARCHAR(255) NOT NULL,
    price        NUMERIC(10,2) NOT NULL,
    category     VARCHAR(100) NOT NULL,
    in_stock     BOOLEAN NOT NULL,
    tags         TEXT[],
    loaded_at    TIMESTAMP DEFAULT NOW()
);

-- ETL Run Log: tracks every pipeline execution
CREATE TABLE IF NOT EXISTS etl_run_log (
    id            SERIAL PRIMARY KEY,
    run_id        VARCHAR(100) UNIQUE NOT NULL,
    source        VARCHAR(50) NOT NULL,
    records_valid INT NOT NULL DEFAULT 0,
    records_invalid INT NOT NULL DEFAULT 0,
    status        VARCHAR(20) NOT NULL,   -- 'success' | 'partial' | 'failed'
    started_at    TIMESTAMP NOT NULL,
    finished_at   TIMESTAMP DEFAULT NOW()
);