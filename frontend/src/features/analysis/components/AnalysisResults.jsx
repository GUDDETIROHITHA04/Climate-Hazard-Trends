import { Space } from "antd";
import { DataTablesCard } from "./DataTablesCard";
import { InsightsSummary } from "./InsightsSummary";
import { TrendCharts } from "./TrendCharts";
/** Order: table (with download buttons) on top, charts in the middle, text insights at the bottom. */
export function AnalysisResults({ data, submitted, stale }) {
  return (
    <Space
      direction="vertical"
      size={16}
      style={{ width: "100%", opacity: stale ? 0.55 : 1, transition: "opacity .2s" }}
    >
      <DataTablesCard
        data={data}
        submitted={submitted}
      />
      <TrendCharts
        data={data}
      />
      <InsightsSummary
        data={data}
      />
    </Space>
  );
}
