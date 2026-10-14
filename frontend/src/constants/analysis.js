export const MIN_YEAR = 1950;
export const LAST_COMPLETE_YEAR = new Date().getFullYear() - 1;
export const MIN_TREND_YEARS = 10;
export const MAX_BOX_DEGREES = 5;
export const DEFAULT_FORM_VALUES = {
  region: { type: "point", lat: 17.385, lon: 78.487, label: "Hyderabad, Telangana" },
  hazard: "heatwave",
  startYear: 1991,
  endYear: 2020,
  percentile: 95,
  minDuration: 3,
  method: "daily",
};
