
import { Table } from "antd";
import { useMemo, useState } from "react";

/**
 * Columns come from the API, so each hazard shows the fields that make sense for it.
 */
export function EventsTable({ events, meta }) {
  const [page, setPage] = useState(1);
  const [limit, setLimit] = useState(10);

  const rows = useMemo(
    () =>
      [...events].sort(
        (a, b) => Number(b.intensity) - Number(a.intensity)
      ),
    [events]
  );

  const columns = meta.event_columns.map((column, index) => ({
    title: column.label,
    dataIndex: column.key,
    align: index < 2 ? "left" : "right",
    sorter: (a, b) =>
      typeof a[column.key] === "number"
        ? Number(a[column.key]) - Number(b[column.key])
        : String(a[column.key]).localeCompare(String(b[column.key])),
  }));

  return (

    <Table
      size="middle"
      rowKey="year"
      columns={columns}
      dataSource={rows}
      pagination={{
        current: page,
        pageSize: limit,
        total: rows.length,
        showSizeChanger: true,
        pageSizeOptions: ["5", "10", "20", "50"],
        showTotal: (total, range) =>
          `${range[0]}–${range[1]} of ${total} years`,
        onChange: (currentPage, pageSize) => {
          setPage(currentPage);
          setLimit(pageSize);
        },
        hideOnSinglePage: false,
      }}
      scroll={{
        x: 1060,
        y: 400,
      }}
    />

  );
}