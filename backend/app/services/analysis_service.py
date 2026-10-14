"""Use case: analyse one hazard for one grid cell.

fetch/cache -> clean -> detect -> aggregate -> trend tests -> insights -> store in MongoDB.
"""
import hashlib
import json
import logging
import threading

import numpy as np
import pandas as pd

from app.core.config import Settings
from app.core.exceptions import ValidationFailed
from app.core.time_utils import last_complete_year
from app.hazards.base import DetectionParams
from app.hazards.registry import get_hazard
from app.processing.trends import analyze_trend
from app.repositories.climate_repository import ClimateRepository
from app.services.climate_data_service import ClimateDataService
from app.services.insights_service import build_insights

logger = logging.getLogger(__name__)

TREND_METRICS = ("primary", "events", "longest", "intensity")
MIN_TREND_YEARS = 10


def snap_to_grid(value: float) -> float:
    """Snap to the 0.25° ERA5 grid so nearby requests share one cache entry."""
    return round(round(value * 4) / 4, 2)


class AnalysisService:
    def __init__(self, data_service: ClimateDataService, repository: ClimateRepository, settings: Settings) -> None:
        self._data = data_service
        self._repository = repository
        self._settings = settings
        self._locks: dict[str, threading.Lock] = {}
        self._guard = threading.Lock()

    def _lock_for(self, key: str) -> threading.Lock:
        with self._guard:
            return self._locks.setdefault(key, threading.Lock())

    def analyze(self, hazard_key: str, lat: float, lon: float, start_year: int, end_year: int,
                percentile: float, min_duration: int, method: str) -> dict:
        cfg = self._settings
        hazard = get_hazard(hazard_key)
        notes: list[str] = []

        last_year = last_complete_year()
        if end_year > last_year:
            notes.append(f"End year reduced to {last_year}: later years are incomplete.")
            end_year = last_year
        if end_year - start_year + 1 < MIN_TREND_YEARS:
            raise ValidationFailed("Please choose a range of at least 10 years to estimate a trend.")

        params = hazard.normalise(DetectionParams(start_year, end_year, percentile, min_duration, method,
                                                  cfg.baseline_start, cfg.baseline_end))
        grid_lat, grid_lon = snap_to_grid(lat), snap_to_grid(lon)
        cell = f"{grid_lat:.2f}_{grid_lon:.2f}"
        key = self._cache_key(hazard_key, cell, params)

        cached = self._repository.get_analysis(key)
        if cached:
            return self._as_cache_hit(cached)

        with self._lock_for(key):  # stampede protection: one computation per key at a time
            cached = self._repository.get_analysis(key)
            if cached:
                return self._as_cache_hit(cached)
            payload = self._compute(hazard, params, cell, grid_lat, grid_lon, last_year, notes)
            self._repository.save_analysis(key, payload)
            return payload

    # ------------------------------------------------------------------
    def _compute(self, hazard, params: DetectionParams, cell, grid_lat, grid_lon, last_year, notes) -> dict:
        cfg, spec = self._settings, hazard.spec
        need_start = max(cfg.min_year - 1, min(params.start_year, cfg.baseline_start) - spec.lookback_years)
        need_end = min(max(params.end_year, cfg.baseline_end), last_year)

        document = self._data.get_daily(cell, spec.variable, grid_lat, grid_lon, need_start, need_end)
        dates = pd.date_range(document["start_date"], periods=len(document["values"]), freq="D")
        series, report = hazard.clean(dates, document["values"])

        result = hazard.detect(series, params)

        reliable_primary = pd.Series([r["primary"] if r["reliable"] else np.nan for r in result.yearly])
        rolling = reliable_primary.rolling(5, center=True, min_periods=3).mean()
        for row, value in zip(result.yearly, rolling):
            row["rolling"] = None if np.isnan(value) else round(float(value), 2)

        years = [row["year"] for row in result.yearly]
        trends = {m: analyze_trend(years, [r[m] if r["reliable"] else None for r in result.yearly]) for m in TREND_METRICS}

        logger.info("analysis computed: %s cell=%s years=%s-%s events=%s", spec.key, cell,
                    params.start_year, params.end_year, len(result.events))
        return {
            "hazard": spec.key,
            "hazard_meta": {
                "key": spec.key, "name": spec.name, "noun": spec.noun, "unit": spec.unit, "event_word": spec.event_word,
                "primary_label": spec.primary_label, "events_label": spec.events_label, "longest_label": spec.longest_label,
                "intensity_label": spec.intensity_label, "intensity_short": spec.intensity_short,
                "event_columns": [{"key": c.key, "label": c.label} for c in spec.event_columns],
            },
            "grid": {"lat": grid_lat, "lon": grid_lon},
            "params": {"start_year": params.start_year, "end_year": params.end_year, "percentile": params.percentile,
                       "min_duration": params.min_duration, "method": params.method,
                       "baseline": [params.baseline_start, params.baseline_end]},
            "definition": result.definition,
            "data_quality": {**report, "years_excluded": [r["year"] for r in result.yearly if not r["reliable"]], "notes": notes},
            "yearly": result.yearly,
            "events": result.events,
            "trends": trends,
            "insights": build_insights(spec, trends, result.yearly, result.events, params.start_year, params.end_year),
            "meta": {"source": "Open-Meteo ERA5 reanalysis", "cache_hit": False,
                     "computed_at": pd.Timestamp.now("UTC").isoformat()},
        }

    def _cache_key(self, hazard_key: str, cell: str, params: DetectionParams) -> str:
        raw = [hazard_key, cell, params.start_year, params.end_year, params.percentile, params.min_duration,
               params.method, params.baseline_start, params.baseline_end, "v3"]
        return hashlib.sha1(json.dumps(raw).encode()).hexdigest()

    @staticmethod
    def _as_cache_hit(payload: dict) -> dict:
        return {**payload, "meta": {**payload["meta"], "cache_hit": True}}
