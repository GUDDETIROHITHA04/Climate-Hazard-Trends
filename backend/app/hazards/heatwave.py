"""Heatwave definition and detection.

Definition (relative, percentile based - ETCCDI / WMO style):
  A heatwave is >= `min_duration` consecutive days on which Tmax is above the `percentile`-th
  percentile of Tmax for that calendar day, computed over a fixed 1991-2020 baseline with a
  15-day window centred on the day.

Why per-calendar-day thresholds? One annual percentile only flags the hottest season.
Why a fixed baseline? Percentiles taken from the analysed period would hide part of the trend.
The "annual" method (one threshold for the whole year) is the literal case-study example and is kept as an option.
"""
import numpy as np
import pandas as pd

from app.core.exceptions import InsufficientDataError, ValidationFailed
from app.hazards.base import DetectionParams, DetectionResult, EventColumn, Hazard, HazardSpec
from app.processing.aggregation import yearly_daily_stats
from app.processing.cleaning import clean_tmax
from app.processing.events import find_runs


def _adjusted_day_of_year(index: pd.DatetimeIndex) -> np.ndarray:
    """Day-of-year on a 365-day calendar (Feb 29 folds onto Feb 28)."""
    doy = index.dayofyear.values
    return np.where(index.is_leap_year & (doy >= 60), doy - 1, doy)


def calendar_day_thresholds(series: pd.Series, base_start: int, base_end: int, pct: float = 95.0,
                            window: int = 15, min_fraction: float = 0.7) -> np.ndarray:
    """95th percentile (or `pct`) of Tmax for each of the 365 calendar days, using a +/- window/2 day window."""
    base = series[(series.index.year >= base_start) & (series.index.year <= base_end)]
    if base.notna().sum() < 10 * 365:
        raise InsufficientDataError("Not enough valid data in the baseline period to compute percentiles")
    base = base[~((base.index.month == 2) & (base.index.day == 29))]
    grid = np.full((base_end - base_start + 1, 365), np.nan)
    grid[base.index.year.values - base_start, _adjusted_day_of_year(base.index) - 1] = base.values

    half = window // 2
    thresholds = np.full(365, np.nan)
    for day in range(365):
        columns = [(day + k) % 365 for k in range(-half, half + 1)]  # circular: wraps over the new year
        values = grid[:, columns].ravel()
        values = values[~np.isnan(values)]
        if values.size >= min_fraction * len(columns) * grid.shape[0]:
            thresholds[day] = np.percentile(values, pct)
    return thresholds


def threshold_series(index: pd.DatetimeIndex, by_day: np.ndarray) -> pd.Series:
    return pd.Series(by_day[_adjusted_day_of_year(index) - 1], index=index)


def annual_threshold_series(series: pd.Series, base_start: int, base_end: int, pct: float = 95.0) -> pd.Series:
    base = series[(series.index.year >= base_start) & (series.index.year <= base_end)].dropna()
    if len(base) < 10 * 365:
        raise InsufficientDataError("Not enough valid data in the baseline period to compute percentiles")
    return pd.Series(float(np.percentile(base, pct)), index=series.index)


def detect_events(tmax: pd.Series, threshold: pd.Series, min_days: int = 3) -> tuple[list[dict], pd.Series]:
    """Run-length detection. NaN days never count as hot and always break a run (conservative)."""
    hot = (tmax > threshold).values  # comparisons with NaN are False
    mask = np.zeros(len(tmax), dtype=bool)
    events: list[dict] = []
    for start, end in find_runs(hot, min_days):
        mask[start:end] = True
        segment = tmax.iloc[start:end]
        excess = segment.values - threshold.iloc[start:end].values
        events.append(
            {
                "start": segment.index[0].date().isoformat(),
                "end": segment.index[-1].date().isoformat(),
                "duration": int(end - start),
                "peak": round(float(segment.max()), 1),  # hottest Tmax in the event, °C
                "mean_excess": round(float(excess.mean()), 2),
                "peak_excess": round(float(excess.max()), 1),
                "intensity": round(float(excess.sum()), 1),  # cumulative °C-days above threshold
            }
        )
    return events, pd.Series(mask, index=tmax.index)


class HeatwaveHazard(Hazard):
    spec = HazardSpec(
        key="heatwave",
        name="Heatwave",
        variable="temperature_2m_max",
        noun="heatwave days",
        unit="days",
        event_word="events",
        primary_label="Heatwave days per year",
        events_label="Number of events",
        longest_label="Longest event (days)",
        intensity_label="Intensity (°C·days above threshold)",
        intensity_short="Intensity (cumulative °C·days above the threshold)",
        event_columns=(
            EventColumn("start", "Start"),
            EventColumn("end", "End"),
            EventColumn("duration", "Days"),
            EventColumn("peak", "Peak Tmax °C"),
            EventColumn("peak_excess", "Peak above threshold °C"),
            EventColumn("intensity", "Intensity °C·days"),
        ),
        caveats=(
            "Based on ERA5 reanalysis for a single ~25 km grid cell, not on weather-station observations.",
            "Heatwaves are defined relative to the local 1991-2020 climate: they show unusual heat for this place, not absolute danger levels.",
            "Temperature only: humidity (which drives heat stress) is not considered.",
        ),
    )

    def normalise(self, params: DetectionParams) -> DetectionParams:
        if params.min_duration < 2:
            raise ValidationFailed("A heatwave needs at least 2 consecutive days")
        return params

    def clean(self, dates, values):
        return clean_tmax(dates, values)

    def detect(self, series: pd.Series, params: DetectionParams) -> DetectionResult:
        if params.method == "daily":
            by_day = calendar_day_thresholds(series, params.baseline_start, params.baseline_end, params.percentile)
            threshold = threshold_series(series.index, by_day)
            where = (f"for that calendar day (±7-day window), ranging {np.nanmin(by_day):.1f} to "
                     f"{np.nanmax(by_day):.1f} °C through the year")
        else:
            threshold = annual_threshold_series(series, params.baseline_start, params.baseline_end, params.percentile)
            where = f"of all days ({float(threshold.iloc[0]):.1f} °C)"

        base = series[(series.index.year >= params.baseline_start) & (series.index.year <= params.baseline_end)]
        base_threshold = threshold.reindex(base.index)
        valid = base.notna() & base_threshold.notna()
        share = round(100 * float((base[valid] > base_threshold[valid]).mean()), 1)

        in_range = (series.index.year >= params.start_year) & (series.index.year <= params.end_year)
        tmax, thr = series[in_range], threshold[in_range]
        events, mask = detect_events(tmax, thr, params.min_duration)
        yearly = yearly_daily_stats(tmax, thr, mask, events, params.start_year, params.end_year)

        definition = {
            "text": (f"A heatwave is {params.min_duration}+ consecutive days with maximum temperature above the "
                     f"{params.percentile:g}th percentile {where}, measured against the "
                     f"{params.baseline_start}-{params.baseline_end} baseline."),
            "sanity": f"Sanity check: {share}% of baseline days exceed the threshold (expected about {100 - params.percentile:.0f}%).",
        }
        return DetectionResult(events, yearly, definition)
