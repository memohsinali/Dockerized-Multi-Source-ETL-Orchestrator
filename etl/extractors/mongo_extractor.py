from bson import ObjectId
from etl.utils.db import get_mongo_connection
from etl.utils.logger import get_logger
import os

logger = get_logger(__name__)


def convert_objectid(doc: dict) -> dict:
    """
    Convert MongoDB ObjectId to string for JSON compatibility
    """
    if "_id" in doc and isinstance(doc["_id"], ObjectId):
        doc["_id"] = str(doc["_id"])
    return doc


def extract_mongo(
    db_name: str = None,
    collection_name: str = None,
    query: dict = None
) -> list[dict]:
    """
    Extract data from MongoDB collection
    """
    try:
        client = get_mongo_connection()

        db_name = db_name or os.getenv("MONGO_DB", "etl_db")
        collection_name = collection_name or os.getenv("MONGO_COLLECTION", "users")

        db = client[db_name]
        collection = db[collection_name]

        query = query or {}

        logger.info(f"Querying MongoDB: {query}")

        documents = list(collection.find(query))

        # Convert ObjectIds
        documents = [convert_objectid(doc) for doc in documents]

        logger.info(f"Fetched {len(documents)} records from MongoDB")

        return documents

    except Exception as e:
        logger.error(f"Mongo extraction failed: {str(e)}")
        return []