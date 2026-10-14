from app.core.config import Settings
from app.repositories.database import create_database


def test_production_without_mongodb_uri_uses_in_memory_database(monkeypatch, caplog):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.delenv("MONGODB_URI", raising=False)
    monkeypatch.setenv("MONGODB_DB", "test_in_memory_db")

    with caplog.at_level("WARNING"):
        database = create_database(Settings())

    database.records.insert_one({"value": "available in this process"})

    assert database.records.find_one({"value": "available in this process"})
    assert "using an in-memory database" in caplog.text
    assert "lost when this process restarts" in caplog.text
