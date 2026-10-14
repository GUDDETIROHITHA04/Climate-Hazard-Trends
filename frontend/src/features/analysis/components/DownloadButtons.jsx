import { DownloadOutlined } from "@ant-design/icons";
import { Button, Space } from "antd";
import { buildExportUrl } from "@/services/analysisService";
export function DownloadButtons({ values, hasEvents }) {
  return (
    <Space
      wrap
      className="download-actions"
    >
      <Button
        type="text"
        className="download-link-button"
        icon={<DownloadOutlined />}
        href={buildExportUrl(values, "yearly")}
      >Download yearly data (CSV)</Button>
      <Button
        type="text"
        className="download-link-button"
        icon={<DownloadOutlined />}
        href={hasEvents ? buildExportUrl(values, "events") : undefined}
        disabled={!hasEvents}
      >Download events (CSV)</Button>
    </Space>
  );
}
