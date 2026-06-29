from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

from etl.extractors.csv_extractor import extract_csv
from etl.extractors.api_extractor import extract_api
from etl.extractors.mongo_extractor import extract_mongo
from etl.validators.schemas import CsvCustomerRecord, ApiPostRecord, MongoUserRecord
from etl.validators.validator import validate_records
from etl.loaders.postgres_loader import (
    load_csv_customers,
    load_api_posts,
    load_mongo_users
)

# ─── Default arguments for all tasks ───────────────────────────────────────────
default_args = {
    "owner": "data-engineering",
    "depends_on_past": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "email_on_failure": True,
    "email": ["amohsin2003@gmail.com"],
}

# ─── Task functions (Airflow calls these via PythonOperator) ────────────────────
def task_extract_csv(**context):
    records = extract_csv("./data/Telco-Customer-Churn.csv")
    context["ti"].xcom_push(key="csv_records", value=records)

def task_extract_api(**context):
    records = extract_api()
    context["ti"].xcom_push(key="api_records", value=records)

def task_extract_mongo(**context):
    records = extract_mongo("users")
    context["ti"].xcom_push(key="mongo_records", value=records)

def task_validate_and_load(**context):
    ti = context["ti"]

    # Pull data from previous tasks via XCom
    csv_raw    = ti.xcom_pull(key="csv_records",   task_ids="extract_csv")
    api_raw    = ti.xcom_pull(key="api_records",   task_ids="extract_api")
    mongo_raw  = ti.xcom_pull(key="mongo_records", task_ids="extract_mongo")

    # Validate each source
    csv_valid,   csv_invalid   = validate_records(csv_raw,   CsvCustomerRecord, "CSV")
    api_valid,   api_invalid   = validate_records(api_raw,   ApiPostRecord,     "API")
    mongo_valid, mongo_invalid = validate_records(mongo_raw, MongoUserRecord, "MongoDB")

    # Load valid records
    load_csv_customers(csv_valid)
    load_api_posts(api_valid)
    load_mongo_users(mongo_valid)

    # Surface summary
    print(f"CSV:   {len(csv_valid)} valid, {len(csv_invalid)} invalid")
    print(f"API:   {len(api_valid)} valid, {len(api_invalid)} invalid")
    print(f"Mongo: {len(mongo_valid)} valid, {len(mongo_invalid)} invalid")

# ─── DAG definition ─────────────────────────────────────────────────────────────
with DAG(
    dag_id="multi_source_etl_pipeline",
    default_args=default_args,
    description="ETL from CSV + REST API + MongoDB → PostgreSQL",
    schedule_interval="0 6 * * *",   # Runs daily at 6 AM UTC
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["etl", "production"],
) as dag:

    extract_csv_task = PythonOperator(
        task_id="extract_csv",
        python_callable=task_extract_csv,
    )

    extract_api_task = PythonOperator(
        task_id="extract_api",
        python_callable=task_extract_api,
    )

    extract_mongo_task = PythonOperator(
        task_id="extract_mongo",
        python_callable=task_extract_mongo,
    )

    validate_and_load_task = PythonOperator(
        task_id="validate_and_load",
        python_callable=task_validate_and_load,
    )

    # All 3 extractions run in PARALLEL, then validate+load waits for all 3
    [extract_csv_task, extract_api_task, extract_mongo_task] >> validate_and_load_task