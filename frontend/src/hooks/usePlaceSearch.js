import { useEffect, useState } from "react";
import { searchPlaces } from "@/services/regionService";
import { useDebouncedValue } from "./useDebouncedValue";
/** Remote geocoding for places that are not in the built-in city list. */
export function usePlaceSearch(query, state) {
  const debounced = useDebouncedValue(query.trim(), 450);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  useEffect(() => {
    if (debounced.length < 3) {
      setResults([]);
      return;
    }
    const controller = new AbortController();
    setLoading(true);
    searchPlaces(debounced, controller.signal, state)
      .then(setResults)
      .catch(() => setResults([]))
      .finally(() => setLoading(false));
    return () => controller.abort();
  }, [debounced, state]);
  return { results, loading };
}
