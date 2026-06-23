
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
import os
from etl.utils.logger import get_logger

logger = get_logger(__name__)

load_dotenv()

file_path=os.getenv("CSV_PATH")

def extract_csv(file_path) -> list[dict]:
    """
    Reads a CSV file and returns a list of raw records (dicts).
    No transformation here — validation happens in the next step.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {file_path}")
    
    logger.info(f"Reading CSV: {file_path}")
    df = pd.read_csv(path)


     # Replace NaN with None so Pydantic handles missing fields cleanly
    df = df.where(pd.notna(df), None)

    records = df.to_dict(orient="records")
    logger.info(f"Extracted {len(records)} records from {file_path}")
    return records
