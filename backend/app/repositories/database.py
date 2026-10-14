import logging

from app.core.config import Settings

logger = logging.getLogger(__name__)


def create_database(settings: Settings):
    """Use MongoDB when configured, otherwise use a process-local in-memory mock."""
    if settings.mongodb_uri:
        from pymongo import MongoClient

        return MongoClient(settings.mongodb_uri, serverSelectionTimeoutMS=5000)[settings.mongodb_db]

    import mongomock

    logger.warning(
        "MONGODB_URI is not configured; using an in-memory database. "
        "Data is temporary and will be lost when this process restarts."
    )
    return mongomock.MongoClient()[settings.mongodb_db]
