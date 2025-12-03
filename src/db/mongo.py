from __future__ import annotations

import os
import logging
from enum import Enum

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

logger = logging.getLogger(__name__)


class DeploymentMode(str, Enum):
    STANDALONE = "standalone"
    REPLICASET = "replicaset"
    SHARDED = "sharded"


# read env variables
MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongo-standalone:27017")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "blog_db")
DEPLOYMENT_MODE = DeploymentMode(os.getenv("DEPLOYMENT_MODE", "standalone"))

_client: AsyncIOMotorClient | None = None
_db: AsyncIOMotorDatabase | None = None


def get_client() -> AsyncIOMotorClient:
    if _client is None:
        raise RuntimeError("Mongo client NOT initialized")
    return _client


def get_db() -> AsyncIOMotorDatabase:
    if _db is None:
        raise RuntimeError("Mongo db NOT initialized")
    return _db


async def init_mongo(app=None) -> None:
    """
    Read MONGO_URI / MONGO_DB_NAME / DEPLOYMENT_MODE from environment variables
    Create client connection
    Confirming db connection by ping
    uses app.state
    """
    global _client, _db

    if _client is not None:
        logger.info("Mongo client initialized")
        return

    logger.info(f"Initializing MongoDB client. URI={MONGO_URI}, DB={MONGO_DB_NAME}, "
                f"DEPLOYMENT_MODE={DEPLOYMENT_MODE}")

    _client = AsyncIOMotorClient(
        MONGO_URI,
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=5000,
        socketTimeoutMS=10000
    )
    _db = _client[MONGO_DB_NAME]

    # health check
    try:
        await _client.admin.command("ping")
        logger.info("Successfully connected to MongoDB")
    except Exception as e:
        logger.exception("Failed to connect to MongoDB: %s", e)
        raise

    # log the mode
    if DEPLOYMENT_MODE == DeploymentMode.STANDALONE:
        logger.info("MongoDB running in STANDALONE mode")
    elif DEPLOYMENT_MODE == DeploymentMode.SHARDED:
        logger.info("MongoDB running in SHARDED mode via mongos")

    # use app.state
    if app is not None:
        app.state.mongo_client = _client
        app.state.mongo_db = _db


async def close_mongo(app=None) -> None:
    """
    CLose connection to MongoDB upon application exit
    """
    global _client, _db

    if _client is not None:
        logger.info("Closing MongoDB client")
        _client.close()

    _client = None
    _db = None

    if app is not None:
        if hasattr(app.state, "mongo_client"):
            del app.state.mongo_client
        if hasattr(app.state, "mongo_db"):
            del app.state.mongo_db
