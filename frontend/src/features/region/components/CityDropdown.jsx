import { Select, Spin } from "antd";
import { useMemo, useState } from "react";
import { usePlaceSearch } from "@/hooks/usePlaceSearch";
import { useRegionOptions } from "@/hooks/useRegionOptions";
const toItem = (r) => ({
  value: r.id,
  label: r.state ? `${r.name}, ${r.state}` : r.name,
  searchText: `${r.name} ${r.state ?? ""}`.toLowerCase(),
});
/** Built-in Indian cities grouped by state, plus worldwide search when the user types 3+ letters. */
export function CityDropdown({ selected, onSelect }) {
  const { options, loading, error } = useRegionOptions("city");
  const [query, setQuery] = useState("");
  const { results, loading: searching } = usePlaceSearch(query);
  const { groups, lookup } = useMemo(() => {
    const byState = new Map();
    const index = new Map();
    options.forEach((city) => {
      index.set(city.id, city);
      const key = city.state ?? "Other";
      byState.set(key, [...(byState.get(key) ?? []), { ...toItem(city), label: city.name }]);
    });
    const localGroups = [...byState.entries()]
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([state, items]) => ({ label: state, options: items }));
    const remote = results.filter((r) => !index.has(r.id));
    remote.forEach((r) => index.set(r.id, r));
    if (selected && !index.has(selected.id))
      index.set(selected.id, selected);
    const extra = [...remote, ...(selected && !options.some((o) => o.id === selected.id) && !remote.some((r) => r.id === selected.id) ? [selected] : [])];
    const groupsWithRemote = extra.length
      ? [...localGroups, { label: "Other places", options: extra.map(toItem) }]
      : localGroups;
    return { groups: groupsWithRemote, lookup: index };
  }, [options, results, selected]);
  return (
    <Select
      showSearch
      allowClear={false}
      size="large"
      style={{ width: "100%" }}
      placeholder="Select or search a city"
      value={options.length ? selected?.id : undefined}
      loading={loading || searching}
      status={error ? "error" : undefined}
      options={groups}
      onSearch={setQuery}
      onChange={(id) => {
    const region = lookup.get(id);
    if (region)
      onSelect(region);
  }}
      filterOption={(input, option) => (option?.searchText ?? String(option?.label ?? "").toLowerCase()).includes(input.toLowerCase())}
      notFoundContent={searching ? <Spin
          size="small"
        /> : "No match. Type 3+ letters to search any place."}
      aria-label="City"
    />
  );
}
