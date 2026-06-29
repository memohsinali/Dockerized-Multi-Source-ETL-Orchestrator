import os
import psycopg2

from psycopg2.extras import execute_values

from etl.validators.schemas import (
    CsvCustomerRecord,
    ApiPostRecord,
    MongoUserRecord,
)

from etl.utils.logger import get_logger

logger = get_logger(__name__)


def get_connection():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "postgres"),
        port=int(os.getenv("POSTGRES_PORT", 5432)),
        dbname=os.getenv("POSTGRES_DB", "airflow"),
        user=os.getenv("POSTGRES_USER", "airflow"),
        password=os.getenv("POSTGRES_PASSWORD", "airflow"),
    )


# ============================================================
# CSV (Telco Customer Churn)
# ============================================================

def load_csv_customers(records: list[CsvCustomerRecord]) -> int:
    conn = get_connection()

    try:
        with conn.cursor() as cur:

            values = [
                (
                    r.customerID,
                    r.gender.value,
                    r.SeniorCitizen,
                    r.tenure,
                    r.PhoneService,
                    r.Contract.value,
                    r.MonthlyCharges,
                    r.TotalCharges,
                    r.Churn,
                )
                for r in records
            ]

            execute_values(
                cur,
                """
                INSERT INTO csv_customers (
                    customer_id,
                    gender,
                    senior_citizen,
                    tenure,
                    phone_service,
                    contract,
                    monthly_charges,
                    total_charges,
                    churn
                )
                VALUES %s
                ON CONFLICT (customer_id) DO NOTHING
                """,
                values,
            )

            conn.commit()

            logger.info(f"Loaded {len(records)} CSV customer records")

            return len(records)

    finally:
        conn.close()


# ============================================================
# API POSTS
# ============================================================

def load_api_posts(records: list[ApiPostRecord]) -> int:
    conn = get_connection()

    try:
        with conn.cursor() as cur:

            values = [
                (
                    r.userId,
                    r.id,
                    r.title,
                    r.body,
                )
                for r in records
            ]

            execute_values(
                cur,
                """
                INSERT INTO api_posts (
                    user_id,
                    source_id,
                    title,
                    body
                )
                VALUES %s
                ON CONFLICT (source_id) DO NOTHING
                """,
                values,
            )

            conn.commit()

            logger.info(f"Loaded {len(records)} API posts")

            return len(records)

    finally:
        conn.close()


# ============================================================
# Mongo Users
# ============================================================

def load_mongo_users(records: list[MongoUserRecord]) -> int:
    conn = get_connection()

    try:
        with conn.cursor() as cur:

            values = [
                (
                    r.id,
                    r.name,
                    r.email,
                    r.age,
                    r.country,
                    r.is_active,
                    r.tags,
                )
                for r in records
            ]

            execute_values(
                cur,
                """
                INSERT INTO mongo_users (
                    mongo_id,
                    name,
                    email,
                    age,
                    country,
                    is_active,
                    tags
                )
                VALUES %s
                ON CONFLICT (mongo_id) DO NOTHING
                """,
                values,
            )

            conn.commit()

            logger.info(f"Loaded {len(records)} Mongo users")

            return len(records)

    finally:
        conn.close()