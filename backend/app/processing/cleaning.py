"""Cleaning of noisy daily temperature records."""
import numpy as np
import pandas as pd


def clean_tmax(dates, values, lo=-70.0, hi=60.0, spike=20.0, max_gap=2):
    """Returns (daily Series with NaN for unusable days, report dict).

    1. Rebuild a complete daily index (missing dates become NaN).
    2. Drop physically impossible values (outside [lo, hi] °C).
    3. Drop isolated spikes: > `spike` °C away from the 15-day centred median.
    4. Interpolate only SHORT gaps (<= max_gap days, inside the record). Longer gaps stay NaN
       so we never invent data for a heatwave.
    """
    s = pd.Series(np.array(values, dtype="float64"), index=pd.to_datetime(dates))
    s = s[~s.index.duplicated()].sort_index().asfreq("D")
    raw_missing = int(s.isna().sum())

    out_of_range = (s < lo) | (s > hi)
    med = s.rolling(15, center=True, min_periods=5).median()
    spikes = (s - med).abs() > spike
    bad = (out_of_range | spikes).fillna(False)
    s[bad] = np.nan

    before = int(s.isna().sum())
    # Fill a gap only if the WHOLE gap is short; pandas' `limit` would fill the first
    # days of a long gap, which is exactly what we must not do.
    gap_id = s.notna().cumsum()
    gap_len = s.isna().groupby(gap_id).transform("sum")
    too_long = s.isna() & (gap_len > max_gap)
    s = s.interpolate(limit_area="inside")
    s[too_long] = np.nan
    interpolated = before - int(s.isna().sum())

    report = {
        "days": int(len(s)),
        "missing_raw": raw_missing,
        "outliers_removed": int(bad.sum()),
        "interpolated_days": interpolated,
        "missing_after_cleaning": int(s.isna().sum()),
        "coverage_pct": round(100 * float(s.notna().mean()), 2),
    }
    return s, report


def clean_precip(dates, values, hi=1000.0):
    """Daily precipitation (mm). Negative/absurd values are removed. Gaps are NOT interpolated:
    rainfall is intermittent, so filling a missing day would invent (or erase) a rain event."""
    s = pd.Series(np.array(values, dtype="float64"), index=pd.to_datetime(dates))
    s = s[~s.index.duplicated()].sort_index().asfreq("D")
    raw_missing = int(s.isna().sum())
    bad = ((s < -0.01) | (s > hi)).fillna(False)
    s[bad] = np.nan
    s = s.clip(lower=0)  # tiny negative values are float noise
    return s, {
        "days": int(len(s)), "missing_raw": raw_missing, "outliers_removed": int(bad.sum()),
        "interpolated_days": 0, "missing_after_cleaning": int(s.isna().sum()),
        "coverage_pct": round(100 * float(s.notna().mean()), 2),
    }
