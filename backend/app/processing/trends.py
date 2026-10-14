"""Trend statistics: Mann-Kendall (significance), Theil-Sen (robust slope), OLS (for comparison)."""
import numpy as np
from scipy import stats


def mann_kendall(y):
    """Two-sided Mann-Kendall test with tie correction. Returns (tau, p_value)."""
    y = np.asarray(y, dtype=float)
    n = len(y)
    s = sum(np.sign(y[j] - y[i]) for i in range(n - 1) for j in range(i + 1, n))
    _, counts = np.unique(y, return_counts=True)
    var = (n * (n - 1) * (2 * n + 5) - np.sum(counts * (counts - 1) * (2 * counts + 5))) / 18.0
    if var <= 0:
        return 0.0, 1.0
    z = (s - np.sign(s)) / np.sqrt(var)  # continuity correction (0 if s == 0)
    p = 2 * (1 - stats.norm.cdf(abs(z)))
    tau = s / (n * (n - 1) / 2)
    return float(tau), float(p)


def analyze_trend(years, values, alpha=0.05, min_points=8):
    pts = [(y, v) for y, v in zip(years, values) if v is not None and not np.isnan(v)]
    if len(pts) < min_points:
        return {"ok": False, "reason": f"Only {len(pts)} reliable years (need >= {min_points})", "n": len(pts)}
    x = np.array([p[0] for p in pts], dtype=float)
    y = np.array([p[1] for p in pts], dtype=float)

    tau, p = mann_kendall(y)
    slope, intercept, lo, hi = stats.theilslopes(y, x)  # 95% CI by default
    ols = stats.linregress(x, y)

    fit = lambda yr: float(intercept + slope * yr)
    f0, f1 = fit(x[0]), fit(x[-1])
    pct_change = ((f1 - f0) / f0 * 100) if f0 >= 0.5 else None  # % is meaningless from a ~0 baseline

    k = max(3, len(y) // 3)  # compare first vs last third of the record
    first, last = float(y[:k].mean()), float(y[-k:].mean())

    return {
        "ok": True,
        "n": len(pts),
        "direction": "increasing" if slope > 0 else "decreasing" if slope < 0 else "flat",
        "significant": bool(p < alpha),
        "mk_tau": round(tau, 3),
        "mk_p": round(p, 4),
        "sen_slope_per_decade": round(float(slope) * 10, 3),
        "sen_ci_per_decade": [round(float(lo) * 10, 3), round(float(hi) * 10, 3)],
        "ols_slope_per_decade": round(float(ols.slope) * 10, 3),
        "ols_p": round(float(ols.pvalue), 4),
        "fitted_start": round(f0, 2),
        "fitted_end": round(f1, 2),
        "pct_change_fitted": None if pct_change is None else round(pct_change, 1),
        "first_period_mean": round(first, 2),
        "last_period_mean": round(last, 2),
        "period_len": k,
        "line": [{"year": int(yr), "value": round(fit(yr), 3)} for yr in range(int(x[0]), int(x[-1]) + 1)],
    }
