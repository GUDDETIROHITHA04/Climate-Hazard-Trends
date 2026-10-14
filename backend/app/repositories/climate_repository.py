"""MongoDB persistence (the NoSQL store).

Collections
-----------
daily_observations : cached raw daily series, one document per ERA5 grid cell and variable
analyses           : computed hazard results, one document per (hazard, cell, parameters)
geocode_cache      : cached place searches
"""
import logging
from datetime import datetime, timedelta, timezone

logger = logging.getLogger(__name__)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)  # Mongo returns naive UTC datetimes


class ClimateRepository:
    def __init__(self, database, cache_ttl_days: int = 30) -> None:
        self._db = database
        self._ttl = timedelta(days=cache_ttl_days)
        try:  # let MongoDB expire stale analyses by itself
            self._db.analyses.create_index("computed_at", expireAfterSeconds=int(self._ttl.total_seconds()))
        except Exception as exc:  # index creation is an optimisation, never a reason to fail
            logger.warning("Could not create TTL index: %s", exc)

    # ---- raw observations -------------------------------------------------
    def get_observations(self, key: str) -> dict | None:
        return self._db.daily_observations.find_one({"_id": key})

    def save_observations(self, key: str, document: dict) -> None:
        self._db.daily_observations.replace_one({"_id": key}, {**document, "_id": key, "saved_at": _utc_now()}, upsert=True)

    # ---- analyses ---------------------------------------------------------
    def get_analysis(self, key: str) -> dict | None:
        doc = self._db.analyses.find_one({"_id": key})
        if not doc or _utc_now() - doc["computed_at"] > self._ttl:
            return None
        return doc["payload"]

    def save_analysis(self, key: str, payload: dict) -> None:
        self._db.analyses.replace_one({"_id": key}, {"_id": key, "payload": payload, "computed_at": _utc_now()}, upsert=True)

    # ---- geocoding --------------------------------------------------------
    def get_geocode(self, query: str) -> list | None:
        doc = self._db.geocode_cache.find_one({"_id": query})
        return doc["results"] if doc else None

    def save_geocode(self, query: str, results: list) -> None:
        self._db.geocode_cache.replace_one({"_id": query}, {"_id": query, "results": results, "saved_at": _utc_now()}, upsert=True)
