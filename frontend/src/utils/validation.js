import { LAST_COMPLETE_YEAR, MAX_BOX_DEGREES, MIN_TREND_YEARS, MIN_YEAR } from "@/constants/analysis";
/** Returns an error message, or null when the range is valid. */
export function validateYearRange(startYear, endYear) {
  if (!Number.isInteger(startYear) || !Number.isInteger(endYear))
    return "Enter valid years.";
  if (startYear < MIN_YEAR)
    return `Data starts in ${MIN_YEAR}.`;
  if (endYear > LAST_COMPLETE_YEAR)
    return `The latest complete year is ${LAST_COMPLETE_YEAR}.`;
  if (endYear - startYear + 1 < MIN_TREND_YEARS)
    return `Choose at least ${MIN_TREND_YEARS} years so a trend can be estimated.`;
  return null;
}
export function validateBox(south, west, north, east) {
  if ([south, west, north, east].some((v) => !Number.isFinite(v)))
    return "Enter all four edges.";
  if (south < -90 || north > 90 || west < -180 || east > 180)
    return "Latitude must be -90 to 90 and longitude -180 to 180.";
  if (!(south < north && west < east))
    return "South must be below north and west below east.";
  if (north - south > MAX_BOX_DEGREES || east - west > MAX_BOX_DEGREES)
    return `A box can be at most ${MAX_BOX_DEGREES}° on each side.`;
  return null;
}
export function validatePoint(lat, lon) {
  if (!Number.isFinite(lat) || !Number.isFinite(lon))
    return "Enter both latitude and longitude.";
  if (lat < -90 || lat > 90 || lon < -180 || lon > 180)
    return "Latitude must be -90 to 90 and longitude -180 to 180.";
  return null;
}
