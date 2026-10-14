import { getJson } from "./httpClient";

export const fetchRegions = (type, signal, state) =>
  getJson("/regions", { type, state }, signal);

export const searchPlaces = (q, signal, state) =>
  getJson("/regions/search", { q, state }, signal);
