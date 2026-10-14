import { Alert, Col, ConfigProvider, Empty, Row } from "antd";
import { useEffect, useMemo, useState } from "react";
import { DEFAULT_FORM_VALUES } from "@/constants/analysis";
import { HAZARD_BY_KEY } from "@/config/hazards";
import { AnalysisFilters } from "@/features/analysis/components/AnalysisFilters";
import { AnalysisResults } from "@/features/analysis/components/AnalysisResults";
import { ResultsSkeleton } from "@/features/analysis/components/ResultsSkeleton";
import { useHazardAnalysis } from "@/hooks/useHazardAnalysis";
import { AppLayout } from "@/layouts/AppLayout";
import { buildAnalysisQuery } from "@/services/analysisService";
import { validateYearRange } from "@/utils/validation";
export function AnalyzerPage() {
  const [values, setValues] = useState(DEFAULT_FORM_VALUES);
  const { data, submitted, loading, error, run, setError } = useHazardAnalysis();
  const hazard = HAZARD_BY_KEY[values.hazard];
  useEffect(() => {
    void run(DEFAULT_FORM_VALUES);
  }, [run]);
  function handleChange(changes) {
    setValues((current) => {
      const next = { ...current, ...changes };
      if (changes.hazard && changes.hazard !== current.hazard) {
        const config = HAZARD_BY_KEY[changes.hazard];
        next.minDuration = config.duration.default; // each hazard has its own sensible defaults
        if (config.percentile)
          next.percentile = config.percentile.default;
      }
      return next;
    });
  }
  function handleSubmit() {
    const message = validateYearRange(values.startYear, values.endYear);
    if (message)
      return setError(message);
    void run(values);
  }
  const isDirty = useMemo(() => !!submitted && JSON.stringify(buildAnalysisQuery(values)) !== JSON.stringify(buildAnalysisQuery(submitted)), [values, submitted]);
  return (
    <ConfigProvider
      theme={{ token: { colorPrimary: hazard.color, borderRadius: 8, fontFamily: "Inter, system-ui, -apple-system, 'Segoe UI', sans-serif" } }}
    >
      <AppLayout
        accentColor={hazard.color}
      >
        <Row
          gutter={[24, 24]}
          align="top"
          className="analyzer-layout"
        >
          <Col
            xs={24}
            lg={9}
            xl={7}
            className="analyzer-sidebar"
          >
            <AnalysisFilters
              values={values}
              loading={loading}
              onChange={handleChange}
              onSubmit={handleSubmit}
            />
          </Col>
          <Col
            xs={24}
            lg={15}
            xl={17}
            className="analyzer-results"
          >
            {error && <Alert
                type="error"
                showIcon
                message={error}
                closable
                onClose={() => setError(null)}
                style={{ marginBottom: 16 }}
              />}
            {isDirty && !loading && <Alert
                type="info"
                showIcon
                message="Settings changed. Click Analyze to update the results."
                style={{ marginBottom: 16 }}
              />}
            {loading && !data && <ResultsSkeleton />}
            {data && submitted && <AnalysisResults
                data={data}
                submitted={submitted}
                stale={loading}
              />}
            {!data && !loading && !error && <Empty
                description="Choose a region and a hazard, then click Analyze."
              />}
          </Col>
        </Row>
      </AppLayout>
    </ConfigProvider>
  );
}
