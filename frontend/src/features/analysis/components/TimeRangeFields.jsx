
import {
  Col,
  InputNumber,
  Row,
  Space,
  Typography,
} from "antd";
import {
  LAST_COMPLETE_YEAR,
  MIN_YEAR,
} from "@/constants/analysis";

export function TimeRangeFields({
  startYear,
  endYear,
  onChange,
}) {
  return (
    <Row gutter={8}>
      <Col span={12}>
        <Space.Compact style={{ width: "100%" }}>
          <Typography.Text
            style={{
              display: "flex",
              alignItems: "center",
              padding: "0 12px",
              border: "1px solid #d9d9d9",
              borderRight: 0,
              borderRadius: "6px 0 0 6px",
              background: "#f5f5f5",
              whiteSpace: "nowrap",
              flexShrink: 0,
            }}
          >
            From
          </Typography.Text>

          <InputNumber
            style={{ width: "100%" }}
            size="large"
            min={MIN_YEAR}
            max={LAST_COMPLETE_YEAR}
            value={startYear}
            onChange={(value) =>
              onChange({
                startYear: value ?? NaN,
                endYear,
              })
            }
            aria-label="Start year"
          />
        </Space.Compact>
      </Col>

      <Col span={12}>
        <Space.Compact style={{ width: "100%" }}>
          <Typography.Text
            style={{
              display: "flex",
              alignItems: "center",
              padding: "0 12px",
              border: "1px solid #d9d9d9",
              borderRight: 0,
              borderRadius: "6px 0 0 6px",
              background: "#f5f5f5",
              whiteSpace: "nowrap",
              flexShrink: 0,
            }}
          >
            To
          </Typography.Text>

          <InputNumber
            style={{ width: "100%" }}
            size="large"
            min={MIN_YEAR}
            max={LAST_COMPLETE_YEAR}
            value={endYear}
            onChange={(value) =>
              onChange({
                startYear,
                endYear: value ?? NaN,
              })
            }
            aria-label="End year"
          />
        </Space.Compact>
      </Col>
    </Row>
  );
}
