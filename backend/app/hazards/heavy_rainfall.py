"""Heavy rainfall: ETCCDI-style R95p.

A heavy-rainfall day = daily precipitation above the `percentile`-th percentile of WET days (>= 1 mm)
in the fixed 1991-2020 baseline. Wet days only: in dry climates most days are 0 mm and a percentile over
all days would be meaningless. Consecutive heavy days form one event.
"""
import numpy as np
import pandas as pd

from app.core.exceptions import InsufficientDataError
from app.hazards.base import DetectionParams, DetectionResult, EventColumn, Hazard, HazardSpec
from app.processing.aggregation import yearly_daily_stats
from app.processing.cleaning import clean_precip
from app.processing.events import find_runs

WET_DAY_MM = 1.0


def wet_day_threshold(series: pd.Series, base_start: int, base_end: int, pct: float = 95.0) -> float:
    base = series[(series.index.year >= base_start) & (series.index.year <= base_end)].dropna()
    wet = base[base >= WET_DAY_MM]
    if len(base) < 10 * 365 or len(wet) < 100:
        raise InsufficientDataError(
            "Not enough rainy days in the baseline period to compute a reliable threshold (very dry region?)"
        )
    return float(np.percentile(wet, pct))


def detect_heavy_rain(rain: pd.Series, threshold: float, min_days: int = 1) -> tuple[list[dict], pd.Series]:
    heavy = (rain > threshold).values
    mask = np.zeros(len(rain), dtype=bool)
    events: list[dict] = []
    for start, end in find_runs(heavy, min_days):
        mask[start:end] = True
        segment = rain.iloc[start:end]
        events.append(
            {
                "start": segment.index[0].date().isoformat(),
                "end": segment.index[-1].date().isoformat(),
                "duration": int(end - start),
                "peak": round(float(segment.max()), 1),  # wettest day, mm
                "total": round(float(segment.sum()), 1),
                "peak_excess": round(float(segment.max() - threshold), 1),
                "intensity": round(float((segment - threshold).sum()), 1),  # mm above threshold
            }
        )
    return events, pd.Series(mask, index=rain.index)


class HeavyRainfallHazard(Hazard):
    spec = HazardSpec(
        key="heavy_rainfall",
        name="Heavy rainfall",
        variable="precipitation_sum",
        noun="heavy-rainfall days",
        unit="days",
        event_word="events",
        primary_label="Heavy-rainfall days per year",
        events_label="Number of events",
        longest_label="Longest run of heavy days",
        intensity_label="Excess rainfall (mm above threshold)",
        intensity_short="Excess rainfall (mm above the threshold)",
        event_columns=(
            EventColumn("start", "Start"),
            EventColumn("end", "End"),
            EventColumn("duration", "Days"),
            EventColumn("peak", "Wettest day mm"),
            EventColumn("total", "Total mm"),
            EventColumn("intensity", "Excess mm"),
        ),
        caveats=(
            "ERA5 rainfall is a ~25 km grid average: it smooths out short, intense local cloudbursts and under-estimates point extremes.",
            "Heavy-rainfall days are relative to local wet-day rainfall in 1991-2020, not a flood-risk measure.",
            "Rainfall is far more variable than temperature, so trends are harder to detect and usually less certain.",
        ),
    )

    def normalise(self, params: DetectionParams) -> DetectionParams:
        return params.with_changes(method="none")

    def clean(self, dates, values):
        return clean_precip(dates, values)

    def detect(self, series: pd.Series, params: DetectionParams) -> DetectionResult:
        threshold = wet_day_threshold(series, params.baseline_start, params.baseline_end, params.percentile)
        base = series[(series.index.year >= params.baseline_start) & (series.index.year <= params.baseline_end)].dropna()
        wet = base[base >= WET_DAY_MM]
        share = round(100 * float((wet > threshold).mean()), 1)

        rain = series[(series.index.year >= params.start_year) & (series.index.year <= params.end_year)]
        events, mask = detect_heavy_rain(rain, threshold, params.min_duration)
        yearly = yearly_daily_stats(rain, pd.Series(threshold, index=rain.index), mask, events,
                                    params.start_year, params.end_year)
        definition = {
            "text": (f"A heavy-rainfall day has more than {threshold:.1f} mm of rain: the {params.percentile:g}th percentile "
                     f"of wet days (≥1 mm) in {params.baseline_start}-{params.baseline_end}. "
                     f"{params.min_duration}+ consecutive heavy days count as one event."),
            "sanity": f"Sanity check: {share}% of baseline wet days exceed the threshold (expected about {100 - params.percentile:.0f}%).",
        }
        return DetectionResult(events, yearly, definition)
