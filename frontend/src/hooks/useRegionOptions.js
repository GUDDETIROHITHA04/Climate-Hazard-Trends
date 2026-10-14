import { useEffect, useState } from "react";
import { fetchRegions } from "@/services/regionService";

const cache = new Map();

/** Loads a list once and reuses it while the user moves between filters. */
export function useRegionOptions(type, state) {
  const cacheKey = `${type}:${state ?? "all"}`;
  const [options, setOptions] = useState(cache.get(cacheKey) ?? []);
  const [loading, setLoading] = useState(!cache.has(cacheKey));
  const [error, setError] = useState(null);

  useEffect(() => {
    const cachedOptions = cache.get(cacheKey);
    if (cachedOptions) {
      setOptions(cachedOptions);
      setLoading(false);
      setError(null);
      return undefined;
    }

    const controller = new AbortController();
    setLoading(true);
    setError(null);

    fetchRegions(type, controller.signal, state)
      .then((data) => {
        cache.set(cacheKey, data);
        setOptions(data);
      })
      .catch((requestError) => {
        if (requestError.name !== "AbortError") {
          setError(requestError.message);
        }
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoading(false);
      });

    return () => controller.abort();
  }, [cacheKey, type, state]);

  return { options, loading, error };
}
