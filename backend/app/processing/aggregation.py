"""Aggregate daily hazard flags into one row per year."""
import calendar

import numpy as np
import pandas as pd


def yearly_daily_stats(values: pd.Series, threshold: pd.Series, mask: pd.Series, events: list[dict],
                       start_year: int, end_year: int, min_coverage: float = 0.9) -> list[dict]:
    """One record per year for hazards detected on daily data (heatwave, heavy rainfall).

    `primary` = number of hazard days, `intensity` = cumulative exceedance over the threshold on hazard days.
    A year with less than `min_coverage` valid days is flagged `reliable=False` and excluded from trend tests.
    """
    excess = (values - threshold).where(mask, 0.0)
    rows = []
    for year in range(start_year, end_year + 1):
        in_year = values.index.year == year
        n_days = 366 if calendar.isleap(year) else 365
        coverage = float(values[in_year].notna().sum()) / n_days
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
                "intensity": round(float(excess[in_year].sum()), 1),
            }
        )
    return rows
