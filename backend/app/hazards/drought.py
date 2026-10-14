"""Drought via SPI (Standardized Precipitation Index, McKee et al. 1993).

1. Monthly rainfall totals (months with <90% valid days become missing).
2. Rolling `scale`-month sums (SPI-3 = short-term / agricultural-type drought).
3. For each calendar month, fit a gamma distribution on the 1991-2020 baseline (zeros handled as a point
   mass) and convert the cumulative probability to a standard-normal z-score = SPI.
4. Drought month = SPI <= -1 (moderate or worse). Event = >= `min_duration` consecutive drought months.
"""
import numpy as np
import pandas as pd
from scipy import stats

from app.core.exceptions import InsufficientDataError
from app.hazards.base import DetectionParams, DetectionResult, EventColumn, Hazard, HazardSpec
from app.processing.cleaning import clean_precip
from app.processing.events import find_runs

SPI_THRESHOLD = -1.0
SPI_SCALE_MONTHS = 3


def monthly_totals(series: pd.Series, min_coverage: float = 0.9) -> pd.Series:
    total = series.resample("MS").sum(min_count=1)
    valid_days = series.resample("MS").count()
    all_days = series.resample("MS").size()
    total = total * all_days / valid_days.replace(0, np.nan)  # scale up slightly incomplete months
    total[valid_days < min_coverage * all_days] = np.nan
    return total


def compute_spi(monthly: pd.Series, base_start: int, base_end: int, scale: int = SPI_SCALE_MONTHS) -> pd.Series:
    accumulated = monthly.rolling(scale, min_periods=scale).sum()
    spi = np.full(len(accumulated), np.nan)
    values = accumulated.values
    for month in range(1, 13):
        in_month = accumulated.index.month == month
        in_baseline = in_month & (accumulated.index.year >= base_start) & (accumulated.index.year <= base_end) & ~np.isnan(values)
        baseline = values[in_baseline]
        if len(baseline) < 20:
            continue
        zero_share = float((baseline == 0).mean())
        positive = baseline[baseline > 0]
        if len(positive) < 10:
            continue
        shape, _, scale_param = stats.gamma.fit(positive, floc=0)
        cumulative = zero_share + (1 - zero_share) * stats.gamma.cdf(values[in_month], shape, loc=0, scale=scale_param)
        spi[in_month] = stats.norm.ppf(np.clip(cumulative, 1e-4, 1 - 1e-4))
    return pd.Series(spi, index=accumulated.index)


def detect_droughts(spi: pd.Series, min_months: int = 2, threshold: float = SPI_THRESHOLD) -> tuple[list[dict], pd.Series]:
    flagged = (spi <= threshold).fillna(False).values  # NaN months break a drought (conservative)
    mask = np.zeros(len(spi), dtype=bool)
    events: list[dict] = []
    for start, end in find_runs(flagged, min_months):
        mask[start:end] = True
        segment = spi.iloc[start:end]
        events.append(
            {
                "start": segment.index[0].strftime("%Y-%m"),
                "end": segment.index[-1].strftime("%Y-%m"),
                "duration": int(end - start),
                "peak": round(float(segment.min()), 2),  # lowest SPI
                "intensity": round(float((-segment).sum()), 2),  # severity = cumulative SPI deficit
            }
        )
    return events, pd.Series(mask, index=spi.index)


def yearly_spi_stats(spi: pd.Series, mask: pd.Series, events: list[dict], start_year: int, end_year: int,
                     min_coverage: float = 0.9) -> list[dict]:
    rows = []
    for year in range(start_year, end_year + 1):
        in_year = spi.index.year == year
        coverage = float(spi[in_year].notna().sum()) / 12
        year_events = [e for e in events if int(e["start"][:4]) == year]
        rows.append(
            {
                "year": year,
                "coverage": round(coverage, 3),
                "reliable": coverage >= min_coverage,
                "primary": int(mask[in_year].sum()),
                "events": len(year_events),
                "longest": max((e["duration"] for e in year_events), default=0),
                "mean_duration": round(float(np.mean([e["duration"] for e in year_events])), 2) if year_events else None,
                "intensity": round(float((-spi[in_year]).where(mask[in_year], 0.0).sum()), 2),
            }
        )
    return rows


class DroughtHazard(Hazard):
    spec = HazardSpec(
        key="drought",
        name="Drought",
        variable="precipitation_sum",
        noun="drought months",
        unit="months",
        event_word="droughts",
        primary_label="Drought months per year",
        events_label="Number of droughts",
        longest_label="Longest drought (months)",
        intensity_label="Severity (cumulative SPI deficit)",
        intensity_short="Severity (cumulative SPI deficit)",
        event_columns=(
            EventColumn("start", "Start"),
            EventColumn("end", "End"),
            EventColumn("duration", "Months"),
            EventColumn("peak", "Lowest SPI"),
            EventColumn("intensity", "Severity"),
        ),
        caveats=(
            "SPI measures rainfall deficit only; it ignores temperature, evaporation and irrigation, so it is meteorological, not agricultural, drought.",
            "SPI-3 compares each 3-month period with the same period in 1991-2020, so a season that is normally dry is not flagged.",
            "ERA5 rainfall is a ~25 km grid average and may differ from local rain gauges.",
        ),
        lookback_years=1,  # SPI-3 needs two months of history before the first analysed month
    )

    def normalise(self, params: DetectionParams) -> DetectionParams:
        return params.with_changes(percentile=0, method="none")

    def clean(self, dates, values):
        return clean_precip(dates, values)

    def detect(self, series: pd.Series, params: DetectionParams) -> DetectionResult:
        spi = compute_spi(monthly_totals(series), params.baseline_start, params.baseline_end)
        base = spi[(spi.index.year >= params.baseline_start) & (spi.index.year <= params.baseline_end)].dropna()
        if len(base) < 120:
            raise InsufficientDataError("Not enough valid rainfall data in the baseline period to compute SPI")
        share = round(100 * float((base <= SPI_THRESHOLD).mean()), 1)

        spi_range = spi[(spi.index.year >= params.start_year) & (spi.index.year <= params.end_year)]
        events, mask = detect_droughts(spi_range, params.min_duration)
        yearly = yearly_spi_stats(spi_range, mask, events, params.start_year, params.end_year)
        definition = {
            "text": (f"A drought is {params.min_duration}+ consecutive months where the 3-month Standardized Precipitation "
                     f"Index (SPI-3) is at or below {SPI_THRESHOLD:g}, fitted on the "
                     f"{params.baseline_start}-{params.baseline_end} baseline."),
            "sanity": f"Sanity check: {share}% of baseline months are at or below the threshold (expected about 16% for a normal distribution).",
        }
        return DetectionResult(events, yearly, definition)
