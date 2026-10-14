/**
 * UI configuration for every hazard: dropdown label, colour and which settings apply.
 * Result labels (chart titles, units) come from the API (`hazard_meta`), not from here.
 */
export const HAZARD_OPTIONS = [
  {
    key: "heatwave",
    label: "Heatwave",
    color: "#D4380D",
    description: "Consecutive days of unusually high maximum temperature",
    duration: { label: "Minimum consecutive days", min: 2, max: 7, default: 3 },
    percentile: { label: "Temperature percentile", min: 85, max: 99, default: 95 },
    supportsMethod: true,
  },
  {
    key: "heavy_rainfall",
    label: "Heavy rainfall",
    color: "#096DD9",
    description: "Days with rainfall above the local wet-day percentile",
    duration: { label: "Minimum consecutive heavy days", min: 1, max: 3, default: 1 },
    percentile: { label: "Wet-day percentile", min: 85, max: 99, default: 95 },
    supportsMethod: false,
  },
  {
    key: "drought",
    label: "Drought",
    color: "#D48806",
    description: "Months with a strong rainfall deficit (SPI-3 ≤ −1)",
    duration: { label: "Minimum consecutive months", min: 1, max: 6, default: 2 },
    percentile: null,
    supportsMethod: false,
  },
];
export const HAZARD_BY_KEY = Object.fromEntries(HAZARD_OPTIONS.map((h) => [h.key, h]));
