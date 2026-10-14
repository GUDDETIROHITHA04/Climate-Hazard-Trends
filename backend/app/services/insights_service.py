"""Turns trend statistics into plain-language, honest insights."""
from app.hazards.base import HazardSpec

COMMON_CAVEATS = (
    "Years with <90% valid data are excluded from trend tests.",
    "Year-to-year variability is large; a trend over ~30 years is indicative and does not by itself attribute the change to climate change.",
)


def build_insights(spec: HazardSpec, trends: dict, yearly: list[dict], events: list[dict], start: int, end: int) -> dict:
    trend, noun, unit = trends["primary"], spec.noun, spec.unit
    bullets: list[str] = []

    if not trend["ok"]:
        headline = f"Not enough reliable years to estimate a trend ({trend['reason']})."
    else:
        slope = trend["sen_slope_per_decade"]
        word = "increased" if slope > 0 else "decreased"
        p_value, pct = trend["mk_p"], trend["pct_change_fitted"]
        subject = noun[0].upper() + noun[1:]
        # The headline claims a change only if it is statistically significant.
        if trend["significant"] and pct is not None:
            headline = (f"{subject} have {word} by about {abs(pct):.0f}% between {start} and {end} "
                        f"(statistically significant, Mann-Kendall p = {p_value}).")
        elif trend["significant"]:
            headline = (f"{subject} have {word} significantly: {slope:+.2f} per decade (Mann-Kendall p = {p_value}); "
                        f"the starting level is near zero, so a % change is not meaningful.")
        else:
            headline = (f"No statistically significant trend in {noun} between {start} and {end} "
                        f"(Mann-Kendall p = {p_value}). Any apparent change is within normal year-to-year variability.")
        low, high = trend["sen_ci_per_decade"]
        bullets.append(f"Robust (Theil-Sen) trend: {slope:+.2f} {noun} per decade (95% CI {low:+.2f} to {high:+.2f}).")
        bullets.append(f"Average {noun} per year: {trend['first_period_mean']} in the first {trend['period_len']} years "
                       f"vs {trend['last_period_mean']} in the last {trend['period_len']}.")
        intensity = trends["intensity"]
        if intensity.get("ok"):
            bullets.append(f"{spec.intensity_short} trend: {intensity['sen_slope_per_decade']:+.2f} per decade "
                           f"({'significant' if intensity['significant'] else 'not significant'}, p = {intensity['mk_p']}).")

    reliable = [row for row in yearly if row["reliable"]]
    if reliable:
        worst = max(reliable, key=lambda row: row["primary"])
        if worst["primary"] > 0:
            bullets.append(f"Worst year: {worst['year']} with {worst['primary']} {noun} in {worst['events']} {spec.event_word}.")
    if events:
        longest = max(events, key=lambda event: event["duration"])
        bullets.append(f"{len(events)} {spec.event_word} in total; the longest lasted {longest['duration']} {unit} "
                       f"({longest['start']} to {longest['end']}).")
    else:
        bullets.append(f"No {spec.event_word} matched the definition in this period.")

    return {"headline": headline, "bullets": bullets, "caveats": [*spec.caveats, *COMMON_CAVEATS]}
