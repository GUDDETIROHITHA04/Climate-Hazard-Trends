import { Card, Tabs } from "antd";
import { HAZARD_BY_KEY } from "@/config/hazards";
import { ColorDot } from "@/components/ColorDot";
import { DownloadButtons } from "./DownloadButtons";
import { EventsTable } from "./EventsTable";
import { YearlyDataTable } from "./YearlyDataTable";
/** Top of the results: the data tables with the download buttons next to them. */
export function DataTablesCard({ data, submitted }) {
  const hazard = HAZARD_BY_KEY[data.hazard];
  const { hazard_meta: meta } = data;
  return (
    <Card
      title={<span
          style={{ display: "inline-flex", alignItems: "center", gap: 8 }}
        >
          <ColorDot
            color={hazard.color}
          />
          {meta.name}
          data ·
          {data.region.label}
        </span>}
      extra={<DownloadButtons
          values={submitted}
          hasEvents={data.events.length > 0}
        />}
      styles={{ header: { flexWrap: "wrap", gap: 8 } }}
    >
      <Tabs
        items={[
    { key: "yearly", label: "Yearly summary", children: <YearlyDataTable
            rows={data.yearly}
            meta={meta}
          /> },
    {
      key: "events",
      label: `${meta.event_word[0].toUpperCase()}${meta.event_word.slice(1)} (${data.events.length})`,
      children: <EventsTable
            events={data.events}
            meta={meta}
          />,
    },
  ]}
      />
    </Card>
  );
}
