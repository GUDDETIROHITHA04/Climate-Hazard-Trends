import os

# Must be set before the app is imported (settings are read once).
os.environ.setdefault("RATE_LIMIT", "1000/minute")
os.environ.setdefault("APP_ENV", "development")

import mongomock  # noqa: E402
import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.api.dependencies import get_analysis_service, get_region_service  # noqa: E402
from app.core.config import get_settings  # noqa: E402
from app.main import create_app  # noqa: E402
from app.repositories.climate_repository import ClimateRepository  # noqa: E402
from app.services.analysis_service import AnalysisService  # noqa: E402
from app.services.climate_data_service import ClimateDataService  # noqa: E402
from app.services.region_service import RegionService  # noqa: E402
from tests.factories.synthetic import make_rainfall_series, make_temperature_series  # noqa: E402


def pytest_collection_modifyitems(items):
    """Mark tests by folder so `pytest -m unit` / `-m integration` work without decorating every test."""
    for item in items:
        path = str(item.fspath).replace("\\", "/")
        if "/tests/unit/" in path:
            item.add_marker(pytest.mark.unit)
        elif "/tests/integration/" in path:
            item.add_marker(pytest.mark.integration)


class FakeOpenMeteoClient:
    """Stands in for the real HTTP client: deterministic data, and it records every call."""

    def __init__(self):
        self.fetch_calls: list[tuple] = []
        self.geocode_calls: list[str] = []

    def fetch_daily(self, lat, lon, start_year, end_year, variable):
        self.fetch_calls.append((lat, lon, start_year, end_year, variable))
        if variable == "temperature_2m_max":
            series = make_temperature_series(start_year, end_year, warming_per_year=0.05)
        else:
            series = make_rainfall_series(start_year, end_year, intensity_trend=-0.015)
        series.iloc[100:103] = None  # real data has gaps
        return {"start_date": series.index[0].date().isoformat(), "values": [None if v != v else float(v) for v in series.values]}

    def geocode(self, query, count=5):
        self.geocode_calls.append(query)
        return [{"id": "geo:17.400,78.500", "name": "Testville, Nowhere", "state": "Nowhere", "lat": 17.4, "lon": 78.5}]


@pytest.fixture
def fake_client() -> FakeOpenMeteoClient:
    return FakeOpenMeteoClient()


@pytest.fixture
def repository() -> ClimateRepository:
    return ClimateRepository(mongomock.MongoClient()["test_db"])


@pytest.fixture
def analysis_service(fake_client, repository) -> AnalysisService:
    return AnalysisService(ClimateDataService(fake_client, repository), repository, get_settings())


@pytest.fixture
def region_service(fake_client, repository) -> RegionService:
    return RegionService(repository, fake_client)


@pytest.fixture
def api(analysis_service, region_service) -> TestClient:
    app = create_app()
    app.dependency_overrides[get_analysis_service] = lambda: analysis_service
    app.dependency_overrides[get_region_service] = lambda: region_service
    with TestClient(app) as client:
        yield client
