import { Select } from "antd";
import { useRegionOptions } from "@/hooks/useRegionOptions";
export function StateDropdown({ selected, onSelect }) {
  const { options, loading, error } = useRegionOptions("state");
  return (
    <Select
      showSearch
      size="large"
      style={{ width: "100%" }}
      placeholder="Select a state or union territory"
      value={options.length ? selected?.id : undefined}
      loading={loading}
      status={error ? "error" : undefined}
      options={options.map((s) => ({ value: s.id, label: s.name }))}
      onChange={(id) => {
    const state = options.find((s) => s.id === id);
    if (state)
      onSelect(state);
  }}
      filterOption={(input, option) => String(option?.label ?? "").toLowerCase().includes(input.toLowerCase())}
      aria-label="State"
    />
  );
}
