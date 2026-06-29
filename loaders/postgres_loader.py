import psycopg2
import os
from psycopg2.extras import execute_values
from etl.validators.schemas import CsvCustomerRecord, ApiPostRecord, MongoProductRecord
from etl.utils.logger import get_logger
from datetime import datetime

logger = get_logger(__name__)

def get_connection():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "postgres"),
        port=int(os.getenv("POSTGRES_PORT", 5432)),
        dbname=os.getenv("POSTGRES_DB", "etl_warehouse"),
        user=os.getenv("POSTGRES_USER", "etl_user"),
        password=os.getenv("POSTGRES_PASSWORD", "etl_pass"),
    )

def load_csv_customers(records: list[CsvCustomerRecord]) -> int:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            values = [
                (r.id, r.name, r.email, r.signup_date, r.country)
                for r in records
            ]
            execute_values(cur, """
                INSERT INTO csv_customers (source_id, name, email, signup_date, country)
                VALUES %s
                ON CONFLICT DO NOTHING
            """, values)
            conn.commit()
            logger.info(f"Loaded {len(records)} customer records into PostgreSQL")
            return len(records)
    finally:
        conn.close()

def load_api_posts(records: list[ApiPostRecord]) -> int:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            values = [(r.userId, r.id, r.title, r.body) for r in records]
            execute_values(cur, """
                INSERT INTO api_posts (user_id, source_id, title, body)
                VALUES %s
                ON CONFLICT DO NOTHING
            """, values)
            conn.commit()
            logger.info(f"Loaded {len(records)} API post records")
            return len(records)
    finally:
        conn.close()

def load_mongo_products(records: list[MongoProductRecord]) -> int:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            values = [
                (r._id, r.product_name, r.price, r.category, r.in_stock, r.tags)
                for r in records
            ]
            execute_values(cur, """
                INSERT INTO mongo_products
                  (mongo_id, product_name, price, category, in_stock, tags)
                VALUES %s
                ON CONFLICT (mongo_id) DO NOTHING
            """, values)
            conn.commit()
            logger.info(f"Loaded {len(records)} MongoDB product records")
            return len(records)
    finally:
        conn.close()