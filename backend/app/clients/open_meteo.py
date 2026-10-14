"""HTTP client for Open-Meteo (archive + geocoding). No API key needed.

Only two fixed hosts are contacted and user input is always passed as URL parameters
(never concatenated into the URL), so there is no SSRF or injection surface.
"""
import logging
import time
from datetime import date, timedelta

import httpx

from app.core.exceptions import UpstreamServiceError, ValidationFailed

logger = logging.getLogger(__name__)

ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"
GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
SUPPORTED_VARIABLES = frozenset({"temperature_2m_max", "precipitation_sum"})


class OpenMeteoClient:
    def __init__(self, timeout: float = 30.0, max_attempts: int = 3) -> None:
        self._timeout = timeout
        self._max_attempts = max_attempts

    def _get(self, url: str, params: dict) -> dict:
        last_error: Exception | None = None
        for attempt in range(self._max_attempts):
            try:
                response = httpx.get(url, params=params, timeout=self._timeout)
                if response.status_code == 429 or response.status_code >= 500:
                    last_error = UpstreamServiceError(f"upstream status {response.status_code}")
                    time.sleep(2**attempt)
                    continue
                if response.status_code >= 400:
                    raise UpstreamServiceError(f"upstream rejected the request ({response.status_code})")
                return response.json()
            except httpx.HTTPError as exc:
                last_error = exc
                logger.warning("Open-Meteo call failed (attempt %s): %s", attempt + 1, exc)
                time.sleep(2**attempt)
        raise UpstreamServiceError(f"Open-Meteo unavailable: {last_error}")

    def fetch_daily(self, lat: float, lon: float, start_year: int, end_year: int, variable: str) -> dict:
        """Daily values from ERA5 reanalysis: Tmax in °C or precipitation in mm.

        `models=era5` is explicit on purpose: the default "best_match" can switch datasets over time,
        which would create fake trends.
        """
        if variable not in SUPPORTED_VARIABLES:
            raise ValidationFailed("Unsupported variable")
        end = min(date(end_year, 12, 31), date.today() - timedelta(days=7))  # archive lags ~5 days
        data = self._get(
            ARCHIVE_URL,
            {
                "latitude": lat,
                "longitude": lon,
                "start_date": date(start_year, 1, 1).isoformat(),
                "end_date": end.isoformat(),
                "daily": variable,
                "temperature_unit": "celsius",
                "precipitation_unit": "mm",
                "models": "era5",
                "timezone": "auto",
            },
        )
        daily = data.get("daily") or {}
        times, values = daily.get("time"), daily.get(variable)
        if not times or values is None or len(times) != len(values):
            raise UpstreamServiceError("Unexpected response shape from Open-Meteo")
        return {"start_date": times[0], "values": values}

    def geocode(self, query: str, count: int = 5) -> list[dict]:
        data = self._get(GEOCODE_URL, {"name": query, "count": count, "language": "en", "format": "json"})
        results = []
        for item in data.get("results") or []:
            parts = [item.get("name"), item.get("admin1"), item.get("country")]
            results.append(
                {
                    "id": f"geo:{item['latitude']:.3f},{item['longitude']:.3f}",
                    "name": ", ".join(p for p in parts if p),
                    "state": item.get("admin1"),
                    "lat": item["latitude"],
                    "lon": item["longitude"],
                }
            )
        return results
