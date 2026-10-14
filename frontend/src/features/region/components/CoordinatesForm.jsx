
import {
  Alert,
  Button,
  Col,
  InputNumber,
  Row,
  Segmented,
  Space,
  Typography,
} from "antd";
import { useState } from "react";
import { MAX_BOX_DEGREES } from "@/constants/analysis";
import { validateBox, validatePoint } from "@/utils/validation";

const FIELD_LABELS = {
  lat: "Latitude",
  lon: "Longitude",
  south: "South",
  north: "North",
  west: "West",
  east: "East",
};

export function CoordinatesForm({ onApply }) {
  const [shape, setShape] = useState("point");

  const [values, setValues] = useState({
    lat: null,
    lon: null,
    south: null,
    west: null,
    north: null,
    east: null,
  });

  const [error, setError] = useState(null);

  const fields =
    shape === "point"
      ? ["lat", "lon"]
      : ["south", "north", "west", "east"];

  function apply() {
    const v = (field) => values[field] ?? NaN;

    if (shape === "point") {
      const message = validatePoint(v("lat"), v("lon"));

      if (message) {
        return setError(message);
      }

      setError(null);

      onApply({
        type: "point",
        lat: v("lat"),
        lon: v("lon"),
        label: `${v("lat")}°, ${v("lon")}°`,
      });
    } else {
      const message = validateBox(
        v("south"),
        v("west"),
        v("north"),
        v("east")
      );

      if (message) {
        return setError(message);
      }

      setError(null);

      onApply({
        type: "box",
        south: v("south"),
        west: v("west"),
        north: v("north"),
        east: v("east"),
        label: "Custom box",
      });
    }
  }

  return (
    <Space
      direction="vertical"
      size={12}
      style={{ width: "100%" }}
    >
      <Segmented
        block
        value={shape}
        onChange={setShape}
        options={[
          { label: "Single point", value: "point" },
          {
            label: `Box (max ${MAX_BOX_DEGREES}°)`,
            value: "box",
          },
        ]}
      />

      <Row gutter={[8, 8]}>
        {fields.map((field) => (
          <Col span={12} key={field}>
            <Space.Compact style={{ width: "100%" }}>
              <Typography.Text
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  padding: "0 8px",
                  minWidth: 58,
                  background: "#f5f5f5",
                  border: "1px solid #d9d9d9",
                  borderRight: 0,
                  borderRadius: "6px 0 0 6px",
                  fontSize: 12,
                }}
              >
                {FIELD_LABELS[field].slice(0, 3)}
              </Typography.Text>

              <InputNumber
                style={{ width: "100%" }}
                placeholder={FIELD_LABELS[field]}
                aria-label={FIELD_LABELS[field]}
                value={values[field]}
                onChange={(next) =>
                  setValues((prev) => ({
                    ...prev,
                    [field]: next,
                  }))
                }
              />
            </Space.Compact>
          </Col>
        ))}
      </Row>

      {error && (
        <Alert
          type="error"
          showIcon
          message={error}
        />
      )}

      <Button block onClick={apply}>
        Use these coordinates
      </Button>
    </Space>
  );
}
