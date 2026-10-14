"""Dependency providers. Tests replace them with fakes via `app.dependency_overrides`."""
from functools import lru_cache

from app.clients.open_meteo import OpenMeteoClient
from app.core.config import get_settings
from app.repositories.climate_repository import ClimateRepository
from app.repositories.database import create_database
from app.services.analysis_service import AnalysisService
from app.services.climate_data_service import ClimateDataService
from app.services.region_service import RegionService


@lru_cache
def get_repository() -> ClimateRepository:
    settings = get_settings()
    return ClimateRepository(create_database(settings), settings.cache_ttl_days)


@lru_cache
def get_open_meteo_client() -> OpenMeteoClient:
    return OpenMeteoClient(timeout=get_settings().http_timeout)


@lru_cache
def get_region_service() -> RegionService:
    return RegionService(get_repository(), get_open_meteo_client())


@lru_cache
def get_analysis_service() -> AnalysisService:
    repository = get_repository()
    data_service = ClimateDataService(get_open_meteo_client(), repository)
    return AnalysisService(data_service, repository, get_settings())
