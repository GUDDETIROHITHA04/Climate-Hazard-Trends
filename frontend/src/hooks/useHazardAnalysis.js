import { useCallback, useRef, useState } from "react";
import { fetchAnalysis } from "@/services/analysisService";
/** Runs an analysis, cancels the previous request, and remembers which values produced the current result. */
export function useHazardAnalysis() {
  const [data, setData] = useState(null);
  const [submitted, setSubmitted] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const controllerRef = useRef(null);
  const run = useCallback(async (values) => {
    controllerRef.current?.abort();
    const controller = new AbortController();
    controllerRef.current = controller;
    setLoading(true);
    setError(null);
    try {
      setData(await fetchAnalysis(values, controller.signal));
      setSubmitted(values);
    }
    catch (e) {
      if (e.name !== "AbortError")
        setError(e.message);
    }
    finally {
      if (controllerRef.current === controller)
        setLoading(false);
    }
  }, []);
  return { data, submitted, loading, error, run, setError };
}
