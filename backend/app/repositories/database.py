from app.core.config import Settings


def create_database(settings: Settings):
    """Real MongoDB when MONGODB_URI is set; in-memory mongomock for local development only."""
    if settings.mongodb_uri:
        from pymongo import MongoClient

        return MongoClient(settings.mongodb_uri, serverSelectionTimeoutMS=5000)[settings.mongodb_db]
    if settings.is_production:
        raise RuntimeError("MONGODB_URI is required when APP_ENV=production")
    try:
        import mongomock
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("Set MONGODB_URI or install requirements-dev.txt for the in-memory dev database") from exc
    return mongomock.MongoClient()[settings.mongodb_db]
