from pymongo import MongoClient
from etl.utils.logger import get_logger
import os

logger = get_logger(__name__)


def get_mongo_connection() -> MongoClient:
    """
    Create and return MongoDB connection
    """
    try:
        mongo_uri = os.getenv("MONGO_URI")

        if not mongo_uri:
            raise ValueError("MONGO_URI not found in environment variables")

        client = MongoClient(mongo_uri)

        # Test connection
        client.admin.command("ping")

        logger.info("MongoDB connection established")

        return client

    except Exception as e:
        logger.error(f"MongoDB connection failed: {str(e)}")
        raise