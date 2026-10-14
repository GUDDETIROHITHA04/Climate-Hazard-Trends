import { Select, Space, Typography } from "antd";
import { ColorDot } from "@/components/ColorDot";
import { HAZARD_BY_KEY, HAZARD_OPTIONS } from "@/config/hazards";
/** Dropdown where every hazard has its own colour (also used as the app accent and in the charts). */
export function HazardSelect({ value, onChange }) {
  return (
    <Select
      size="large"
      value={value}
      onChange={onChange}
      style={{ width: "100%" }}
      aria-label="Hazard type"
      options={HAZARD_OPTIONS.map((h) => ({ value: h.key, label: h.label }))}
      labelRender={({ value: key }) => {
    const hazard = HAZARD_BY_KEY[key];
    return (<Space
          size={8}
        >
          <ColorDot
            color={hazard.color}
          />
          <span>
            {hazard.label}
          </span>
        </Space>);
  }}
      optionRender={(option) => {
    const hazard = HAZARD_BY_KEY[option.value];
    return (<Space
          align="start"
          size={10}
        >
          <span
            style={{ marginTop: 6 }}
          >
            <ColorDot
              color={hazard.color}
            />
          </span>
          <div>
            <div
              style={{ fontWeight: 500 }}
            >
              {hazard.label}
            </div>
            <Typography.Text
              type="secondary"
              style={{ fontSize: 12, whiteSpace: "normal" }}
            >
              {hazard.description}
            </Typography.Text>
          </div>
        </Space>);
  }}
    />
  );
}
