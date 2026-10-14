"""Synthetic weather data for tests.

Real API data is never used in unit tests: it is slow, changes over time and cannot be controlled.
With synthetic data we know the truth, e.g. "a 5-day spell of +15 °C was injected in July 2005, the detector must find it".
"""
import numpy as np
import pandas as pd


def make_temperature_series(start: int = 1990, end: int = 2020, warming_per_year: float = 0.0, seed: int = 0,
                            hot_spell: tuple[str, int, float] | None = None) -> pd.Series:
    """Seasonal Tmax with autocorrelated noise. `hot_spell=(first_day, n_days, boost_celsius)` injects a heatwave."""
    index = pd.date_range(f"{start}-01-01", f"{end}-12-31", freq="D")
    rng = np.random.default_rng(seed)
    seasonal = 28 + 8 * np.sin(2 * np.pi * (index.dayofyear.values - 100) / 365.25)
    noise = np.zeros(len(index))
    for i in range(1, len(index)):
        noise[i] = 0.6 * noise[i - 1] + rng.normal(0, 1.5)
    series = pd.Series(seasonal + noise + warming_per_year * (index.year.values - start), index=index)
    if hot_spell:
        first_day, n_days, boost = hot_spell
        series.loc[first_day: pd.Timestamp(first_day) + pd.Timedelta(days=n_days - 1)] += boost
    return series


def make_rainfall_series(start: int = 1990, end: int = 2020, seed: int = 0, intensity_trend: float = 0.0) -> pd.Series:
    """Monsoon-like rainfall: wet-season probability + gamma amounts. Negative `intensity_trend` = drying."""
    index = pd.date_range(f"{start}-01-01", f"{end}-12-31", freq="D")
    rng = np.random.default_rng(seed)
    season = 0.5 + 0.45 * np.sin(2 * np.pi * (index.dayofyear.values - 120) / 365.25)  # peak around July
    is_wet = rng.random(len(index)) < season * 0.6
    amounts = rng.gamma(0.8, 10.0, len(index)) * (1 + intensity_trend * (index.year.values - start))
    return pd.Series(np.where(is_wet, amounts, 0.0), index=index)
