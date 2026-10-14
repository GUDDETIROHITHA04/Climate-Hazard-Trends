import json
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path

from app.clients.open_meteo import OpenMeteoClient
from app.core.exceptions import NotFoundError, ValidationFailed
from app.repositories.climate_repository import ClimateRepository
from app.schemas.analysis import AnalysisQuery

logger = logging.getLogger(__name__)
DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "regions.json"
PLACE_NAME_RE = re.compile(r"^[\w\s.,'\-]{2,80}$", re.UNICODE)


@dataclass(frozen=True)
class ResolvedRegion:
    label: str
    lat: float
    lon: float
    type: str
    extra: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {"label": self.label, "lat": round(self.lat, 4), "lon": round(self.lon, 4), "type": self.type, **self.extra}


class RegionService:
    """Reference data (states, cities), place search and conversion of a query into one coordinate."""

    def __init__(self, repository: ClimateRepository, client: OpenMeteoClient) -> None:
        self._repository = repository
        self._client = client
        self._catalog = json.loads(DATA_FILE.read_text(encoding="utf-8"))

    def list_regions(self, kind: str, state: str | None = None) -> list[dict]:
        """Return states or cities, optionally limited to one selected state."""
        if kind == "state":
            return self._catalog["states"]

        cities = self._catalog["cities"]
        if not state:
            return cities

        selected_state = state.strip().casefold()
        return [city for city in cities if (city.get("state") or "").casefold() == selected_state]

    def search_places(self, query: str, state: str | None = None) -> list[dict]:
        if not PLACE_NAME_RE.match(query):
            raise ValidationFailed("Search text contains invalid characters")
        state_name = " ".join(state.lower().split()) if state else ""
        key = " ".join(f"{query} {state_name}".lower().split())
        cached = self._repository.get_geocode(key)
        if cached is not None:
            return cached
        # Add the selected state and country to reduce ambiguous matches. This lets users
        # find places beyond the small built-in list without maintaining a manual city list.
        search_query = f"{query}, {state}, India" if state else query
        results = self._client.geocode(search_query)
        if state:
            selected_state = state.strip().casefold()
            results = [
                place for place in results
                if (place.get("state") or "").strip().casefold() == selected_state
                or selected_state in (place.get("name") or "").casefold()
            ]
        self._repository.save_geocode(key, results)
        return results

    def resolve(self, query: AnalysisQuery) -> ResolvedRegion:
        mode = query.region_mode
        if mode == "city":
            results = self.search_places(query.city)
            if not results:
                raise NotFoundError(f"No place found for '{query.city}'")
            top = results[0]
            return ResolvedRegion(top["name"], top["lat"], top["lon"], "city")
        if mode == "point":
            return ResolvedRegion(query.label or f"{query.lat:.2f}°, {query.lon:.2f}°", query.lat, query.lon, "point")
        # A box is represented by the ERA5 grid cell at its centre (documented assumption)
        bbox = {"south": query.south, "west": query.west, "north": query.north, "east": query.east}
        return ResolvedRegion(query.label or "Custom box", (query.south + query.north) / 2,
                              (query.west + query.east) / 2, "box", {"bbox": bbox})
