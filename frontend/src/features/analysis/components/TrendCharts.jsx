import { Card, Col, Row } from "antd";
import { BarController, BarElement, CategoryScale, Chart as ChartJS, Legend, LinearScale, LineController, LineElement, PointElement, Tooltip, } from "chart.js";
import { Chart } from "react-chartjs-2";
import { HAZARD_BY_KEY } from "@/config/hazards";
import { capitalize } from "@/utils/formatters";
ChartJS.register(CategoryScale, LinearScale, BarElement, BarController, LineElement, LineController, PointElement, Tooltip, Legend);
const INK = "#1F2933";
const EXCLUDED_COLOR = "#C9D0D8";
function buildOptions(yTitle, y2Title) {
  return {
    responsive: true,
    maintainAspectRatio: false,
    interaction: { mode: "index", intersect: false },
    plugins: { legend: { position: "bottom", labels: { boxWidth: 12, boxHeight: 12 } } },
    scales: {
      x: { grid: { display: false }, ticks: { maxTicksLimit: 10 } },
      y: { beginAtZero: true, title: { display: !!yTitle, text: yTitle }, ticks: { precision: 0 } },
      ...(y2Title
        ? { y2: { position: "right", beginAtZero: true, title: { display: true, text: y2Title }, ticks: { precision: 0 }, grid: { drawOnChartArea: false } } }
        : {}),
    },
  };
}
export function TrendCharts({ data }) {
  const { yearly, trends, hazard_meta: meta } = data;
  const color = HAZARD_BY_KEY[data.hazard].color;
  const labels = yearly.map((r) => r.year);
  const unitTitle = capitalize(meta.unit);
  const bars = (key, label) => ({
    type: "bar",
    label,
    data: yearly.map((r) => r[key]),
    backgroundColor: yearly.map((r) => (r.reliable ? color : EXCLUDED_COLOR)),
    borderRadius: 3,
  });
  const trend = trends.primary;
  const fitted = trend.ok && trend.line ? Object.fromEntries(trend.line.map((p) => [p.year, p.value])) : {};
  const frequency = {
    labels,
    datasets: [
      bars("primary", meta.primary_label),
      { type: "line", label: "5-year rolling mean", data: yearly.map((r) => r.rolling), borderColor: INK, backgroundColor: INK, pointRadius: 0, borderWidth: 2.5, tension: 0.3 },
      ...(trend.ok
        ? [{ type: "line", label: "Trend (Theil–Sen)", data: labels.map((y) => fitted[y] ?? null), borderColor: INK, borderDash: [6, 4], pointRadius: 0, borderWidth: 1.5 }]
        : []),
    ],
  };
  const duration = {
    labels,
    datasets: [
      bars("events", meta.events_label),
      { type: "line", label: meta.longest_label, data: yearly.map((r) => r.longest), yAxisID: "y2", borderColor: INK, backgroundColor: INK, pointRadius: 2.5, borderWidth: 2 },
    ],
  };
  const intensity = { labels, datasets: [bars("intensity", meta.intensity_label)] };
  return (
    <Row
      gutter={[16, 16]}
    >
      <Col
        span={24}
      >
        <Card
          title={meta.primary_label}
          extra={<span
              className="muted-note"
            >Grey bars: year excluded from trend (too much missing data)</span>}
        >
          <div
            className="chart-box"
          >
            <Chart
              type="bar"
              data={frequency}
              options={buildOptions(unitTitle)}
            />
          </div>
        </Card>
      </Col>
      <Col
        xs={24}
        xl={12}
      >
        <Card
          title="Frequency and duration"
        >
          <div
            className="chart-box"
          >
            <Chart
              type="bar"
              data={duration}
              options={buildOptions(meta.events_label, unitTitle)}
            />
          </div>
        </Card>
      </Col>
      <Col
        xs={24}
        xl={12}
      >
        <Card
          title={meta.intensity_label}
        >
          <div
            className="chart-box"
          >
            <Chart
              type="bar"
              data={intensity}
              options={buildOptions("")}
            />
          </div>
        </Card>
      </Col>
    </Row>
  );
}
