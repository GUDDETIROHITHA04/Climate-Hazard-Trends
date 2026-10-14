import { HAZARD_BY_KEY } from "@/config/hazards";
import { buildUrl, getJson } from "./httpClient";
/** Converts form state into API query parameters, sending only the settings that apply to the hazard. */
export function buildAnalysisQuery(values) {
  const hazard = HAZARD_BY_KEY[values.hazard];
  const region = values.region.type === "box"
    ? { south: values.region.south, west: values.region.west, north: values.region.north, east: values.region.east }
    : { lat: values.region.lat, lon: values.region.lon, label: values.region.label };
  return {
    ...region,
    hazard: values.hazard,
    start_year: values.startYear,
    end_year: values.endYear,
    min_duration: values.minDuration,
    percentile: hazard.percentile ? values.percentile : undefined,
    method: hazard.supportsMethod ? values.method : undefined,
  };
}
export function fetchAnalysis(values, signal) {
  return getJson("/analysis", buildAnalysisQuery(values), signal);
}
export function buildExportUrl(values, kind) {
  return buildUrl("/analysis/export", { ...buildAnalysisQuery(values), kind });
}
