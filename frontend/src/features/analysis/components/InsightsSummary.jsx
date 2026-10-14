
import {
  Alert,
  Card,
  Col,
  Collapse,
  Descriptions,
  Row,
  Statistic,
  Typography,
} from "antd";
import { capitalize, formatSigned } from "@/utils/formatters";

/**
 * Text part of the results: headline, key numbers, explanation and limits.
 * Shown below the tables and charts.
 */
export function InsightsSummary({ data }) {
  const {
    insights,
    trends,
    events,
    hazard_meta: meta,
    data_quality: quality,
    definition,
  } = data;

  const trend = trends.primary;

  const longest = events.reduce(
    (max, event) => Math.max(max, Number(event.duration)),
    0
  );

  return (
    <Card
      title={`Insights: ${meta.name}, ${data.params.start_year}–${data.params.end_year}`}
    >
      <Typography.Title
        level={4}
        style={{ marginTop: 0, maxWidth: "46ch" }}
      >
        {insights.headline}
      </Typography.Title>

      <Typography.Paragraph type="secondary">
        {data.region.label}
        {" · ERA5 grid cell "}
        {data.grid.lat}°, {data.grid.lon}°
        {data.meta.cache_hit ? " · served from cache" : ""}
      </Typography.Paragraph>

      <Row gutter={[12, 12]} style={{ marginBottom: 16 }}>
        <Col xs={12} md={6}>
          <Card size="small">
            <Statistic
              title="Trend per decade"
              value={
                trend.ok
                  ? formatSigned(trend.sen_slope_per_decade)
                  : "n/a"
              }
              suffix={meta.unit}
            />
          </Card>
        </Col>

        <Col xs={12} md={6}>
          <Card size="small">
            <Statistic
              title="Mann–Kendall p-value"
              value={trend.ok ? (trend.mk_p ?? "n/a") : "n/a"}
              suffix={
                trend.ok
                  ? trend.significant
                    ? "significant"
                    : "not significant"
                  : ""
              }
              valueStyle={{ fontSize: 22 }}
            />
          </Card>
        </Col>

        <Col xs={12} md={6}>
          <Card size="small">
            <Statistic
              title={capitalize(meta.event_word)}
              value={events.length}
            />
          </Card>
        </Col>

        <Col xs={12} md={6}>
          <Card size="small">
            <Statistic
              title="Longest"
              value={longest}
              suffix={meta.unit}
            />
          </Card>
        </Col>
      </Row>

      <ul className="insight-list">
        {insights.bullets.map((bullet) => (
          <li key={bullet}>{bullet}</li>
        ))}
      </ul>

      {quality.notes.length > 0 && (
        <Alert
          type="info"
          showIcon
          message={quality.notes.join(" ")}
          style={{ marginBottom: 16 }}
        />
      )}

      <Collapse
        ghost
        items={[
          {
            key: "method",
            label: "How this is calculated",
            children: (
              <>
                <Typography.Paragraph>
                  {definition.text}
                </Typography.Paragraph>

                <Typography.Paragraph type="secondary">
                  {definition.sanity}
                </Typography.Paragraph>

                <Descriptions
                  size="small"
                  bordered
                  column={{ xs: 1, md: 2 }}
                  title="Data quality"
                >
                  <Descriptions.Item label="Coverage">
                    {quality.coverage_pct}%
                  </Descriptions.Item>

                  <Descriptions.Item label="Outliers removed">
                    {quality.outliers_removed}
                  </Descriptions.Item>

                  <Descriptions.Item label="Short gaps interpolated">
                    {quality.interpolated_days} days
                  </Descriptions.Item>

                  <Descriptions.Item label="Days left empty">
                    {quality.missing_after_cleaning}
                  </Descriptions.Item>

                  <Descriptions.Item label="Years excluded from trend">
                    {quality.years_excluded.length
                      ? quality.years_excluded.join(", ")
                      : "none"}
                  </Descriptions.Item>

                  <Descriptions.Item label="Source">
                    {data.meta.source}
                  </Descriptions.Item>
                </Descriptions>
              </>
            ),
          },
          {
            key: "limits",
            label: "Limits of this analysis",
            children: (
              <ul className="insight-list">
                {insights.caveats.map((caveat) => (
                  <li key={caveat}>{caveat}</li>
                ))}
              </ul>
            ),
          },
        ]}
      />
    </Card>
  );
}
