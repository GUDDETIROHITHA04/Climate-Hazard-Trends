import { Select, Slider, Space, Typography } from "antd";
import { HAZARD_BY_KEY } from "@/config/hazards";
/** Only shows the settings that make sense for the selected hazard. */
export function DefinitionSettings({ values, onChange }) {
  const hazard = HAZARD_BY_KEY[values.hazard];
  return (
    <Space
      direction="vertical"
      size={16}
      style={{ width: "100%" }}
    >
      {hazard.percentile && (<div>
          <Typography.Text>
            {hazard.percentile.label}
            :
            <b>
              {values.percentile}
              th
            </b>
          </Typography.Text>
          <Slider
            min={hazard.percentile.min}
            max={hazard.percentile.max}
            value={values.percentile}
            onChange={(percentile) => onChange({ percentile })}
          />
        </div>)}
      <div>
        <Typography.Text>
          {hazard.duration.label}
          :
          <b>
            {values.minDuration}
          </b>
        </Typography.Text>
        <Slider
          min={hazard.duration.min}
          max={hazard.duration.max}
          value={values.minDuration}
          onChange={(minDuration) => onChange({ minDuration })}
        />
      </div>
      {hazard.supportsMethod && (<div>
          <Typography.Text>Threshold type</Typography.Text>
          <Select
            style={{ width: "100%", marginTop: 4 }}
            value={values.method}
            onChange={(method) => onChange({ method })}
            options={[
    { value: "daily", label: "Per calendar day (recommended)" },
    { value: "annual", label: "One value for the whole year" },
  ]}
          />
        </div>)}
    </Space>
  );
}
