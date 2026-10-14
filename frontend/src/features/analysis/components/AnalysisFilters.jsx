import { Button, Card, Collapse, Form } from "antd";

import { HazardSelect } from "@/features/hazard/components/HazardSelect";
import { RegionSelector } from "@/features/region/components/RegionSelector";

import { DefinitionSettings } from "./DefinitionSettings";
import { TimeRangeFields } from "./TimeRangeFields";

export function AnalysisFilters({ values, loading, onChange, onSubmit }) {
    const definitionPanel = [
        {
            key: "definition",
            label: "Definition settings",
            children: <DefinitionSettings values={values} onChange={onChange} />,
        },
    ];

    return (
        <Card title="Analysis settings" className="filters-card">
            <Form layout="vertical" onFinish={onSubmit} requiredMark={false}>
                <Form.Item label="Region">
                    <RegionSelector
                        region={values.region}
                        onChange={(region) => onChange({ region })}
                    />
                </Form.Item>

                <Form.Item label="Hazard">
                    <HazardSelect
                        value={values.hazard}
                        onChange={(hazard) => onChange({ hazard })}
                    />
                </Form.Item>

                <Form.Item label="Time range">
                    <TimeRangeFields
                        startYear={values.startYear}
                        endYear={values.endYear}
                        onChange={onChange}
                    />
                </Form.Item>

                <Collapse ghost items={definitionPanel} />

                <Button
                    type="primary"
                    htmlType="submit"
                    size="large"
                    block
                    loading={loading}
                    style={{ marginTop: 16 }}
                >
                    Analyze
                </Button>
            </Form>
        </Card>
    );
}
