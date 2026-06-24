import requests
from etl.utils.logger import get_logger

logger = get_logger(__name__)

API_URL = "https://jsonplaceholder.typicode.com/posts"

def extract_api(url: str = API_URL, params: dict = None) -> list[dict]:
    """
    Calls a REST API endpoint and returns raw JSON records.
    Handles pagination via 'page' query param if needed.
    """
    logger.info(f"Calling API: {url}")
    response = requests.get(url, params=params, timeout=30)

    response.raise_for_status()   # raises HTTPError on 4xx/5xx

    records = response.json()  #give results back in to python objects

    # Normalize: ensure we always return a list
    if isinstance(records, dict):
        records = [records]

    logger.info(f"Extracted {len(records)} records from API")
    return records