
import { Table, Tag } from "antd";
import { useState } from "react";
import { formatPercent } from "@/utils/formatters";

export function YearlyDataTable({ rows, meta }) {
  const [page, setPage] = useState(1);
  const [limit, setLimit] = useState(10);

  const numeric = (key) => (a, b) =>
    Number(a[key] ?? 0) - Number(b[key] ?? 0);

  const columns = [
    {
      title: "Year",
      dataIndex: "year",
      sorter: numeric("year"),
      defaultSortOrder: "descend",
      width: 90,
      fixed: "left",
    },
    {
      title: meta.primary_label,
      dataIndex: "primary",
      sorter: numeric("primary"),
      align: "right",
      width: 150,
    },
    {
      title: meta.events_label,
      dataIndex: "events",
      sorter: numeric("events"),
      align: "right",
      width: 140,
    },
    {
      title: meta.longest_label,
      dataIndex: "longest",
      sorter: numeric("longest"),
      align: "right",
      width: 150,
    },
    {
      title: meta.intensity_label,
      dataIndex: "intensity",
      sorter: numeric("intensity"),
      align: "right",
      width: 150,
    },
    {
      title: "Data coverage",
      dataIndex: "coverage",
      render: formatPercent,
      sorter: numeric("coverage"),
      align: "right",
      width: 140,
    },
    {
      title: "Used in trend",
      dataIndex: "reliable",
      align: "center",
      width: 140,
      filters: [
        { text: "Included", value: true },
        { text: "Excluded", value: false },
      ],
      onFilter: (value, record) => record.reliable === value,
      render: (reliable) =>
        reliable ? (
          <Tag color="success">Included</Tag>
        ) : (
          <Tag color="warning">Excluded</Tag>
        ),
    },
  ];

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
