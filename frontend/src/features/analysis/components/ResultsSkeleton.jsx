import { Card, Skeleton, Typography } from "antd";
export function ResultsSkeleton() {
  return (
    <Card
      aria-label="Loading results"
    >
      <Skeleton
        active
        paragraph={{ rows: 8 }}
      />
      <Typography.Text
        type="secondary"
      >Fetching 30+ years of daily data. The first request for a place can take 10–20 seconds; repeat requests are instant.</Typography.Text>
    </Card>
  );
}
