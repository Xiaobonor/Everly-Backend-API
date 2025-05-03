"""MongoDB connection module."""

import logging
from typing import Optional

import mongoengine
from mongoengine.connection import ConnectionFailure

from app.core.config import settings

logger = logging.getLogger(__name__)


async def connect_to_mongo() -> None:
    """
    Connect to MongoDB using settings from the config.
    
    This function establishes a connection to MongoDB using the URL
    and database name specified in the application settings.
    """
    try:
        logger.info("Connecting to MongoDB...")
        mongoengine.connect(
            db=settings.MONGODB_DATABASE,
            host=settings.MONGODB_URL,
            alias="default"
        )
        logger.info("Connected to MongoDB successfully.")
    except ConnectionFailure as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise


async def disconnect_from_mongo() -> None:
    """
    Disconnect from MongoDB.
    
    This function closes the connection to MongoDB.
    """
    try:
        logger.info("Disconnecting from MongoDB...")
        mongoengine.disconnect(alias="default")
        logger.info("Disconnected from MongoDB successfully.")
    except Exception as e:
        logger.error(f"Error while disconnecting from MongoDB: {e}")
        raise


async def get_database():
    """
    Get the MongoDB database instance.
    
    This function returns the MongoDB database instance.
    It is designed to be used as a FastAPI dependency.
    """
    try:
        # Return the database instance
        return mongoengine.get_db()
    except Exception as e:
        logger.error(f"Error getting MongoDB database: {e}")
        raise 