import logging

from app.clients.open_meteo import OpenMeteoClient
from app.repositories.climate_repository import ClimateRepository

logger = logging.getLogger(__name__)


class ClimateDataService:
    """Returns raw daily observations for a grid cell, from MongoDB when possible, otherwise from Open-Meteo."""

    def __init__(self, client: OpenMeteoClient, repository: ClimateRepository) -> None:
        self._client = client
        self._repository = repository

    def get_daily(self, cell: str, variable: str, lat: float, lon: float, start_year: int, end_year: int) -> dict:
        key = f"{cell}:{variable}"
        cached = self._repository.get_observations(key)
        if cached and cached["start_year"] <= start_year and cached["end_year"] >= end_year:
            logger.info("observations cache hit: %s", key)
            return cached
        if cached:  # widen the cached range instead of throwing it away
            start_year, end_year = min(start_year, cached["start_year"]), max(end_year, cached["end_year"])
        logger.info("observations cache miss: %s (%s-%s), calling Open-Meteo", key, start_year, end_year)
        fetched = self._client.fetch_daily(lat, lon, start_year, end_year, variable)
        document = {"start_year": start_year, "end_year": end_year, **fetched}
        self._repository.save_observations(key, document)
        return document
