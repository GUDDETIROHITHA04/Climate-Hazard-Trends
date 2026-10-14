import { Alert, Select, Segmented, Space, Typography } from "antd";
import { useEffect, useState } from "react";
import { formatCoordinates } from "@/utils/formatters";
import { useRegionOptions } from "@/hooks/useRegionOptions";
import { usePlaceSearch } from "@/hooks/usePlaceSearch";
import { CoordinatesForm } from "./CoordinatesForm";
import { MapRegionPicker } from "./MapRegionPicker";
const MODE_OPTIONS = [
  { label: "Area", value: "area" },
  { label: "Lat/Lon", value: "coordinates" },
  { label: "Map", value: "map" },
];
const DEFAULT_STATE = {
  id: "telangana", name: "Telangana", lat: 18.1124, lon: 79.0193, state: null,
};
const DEFAULT_CITY = {
  id: "hyderabad", name: "Hyderabad", state: "Telangana", lat: 17.385, lon: 78.487,
};
const toPoint = (option, label) => ({ type: "point", lat: option.lat, lon: option.lon, label });
/** Select a state first, then optionally narrow the analysis to one of its cities. */
export function RegionSelector({ region, onChange }) {
  const [mode, setMode] = useState("area");
  const [selectedState, setSelectedState] = useState(DEFAULT_STATE);
  const [selectedCity, setSelectedCity] = useState(DEFAULT_CITY);
  const [cityQuery, setCityQuery] = useState("");
  const { results: searchedCities, loading: citySearchLoading } = usePlaceSearch(cityQuery, selectedState?.name);
  const { options: states, loading: statesLoading, error: statesError } = useRegionOptions("state");
  const { options: cities, loading: citiesLoading, error: citiesError } = useRegionOptions("city", selectedState?.name);
  useEffect(() => {
    if (states.length && !states.some((item) => item.id === selectedState?.id)) {
      const initialState = states.find((item) => item.name === "Telangana") ?? states[0];
      setSelectedState(initialState);
    }
  }, [states, selectedState?.id]);
  useEffect(() => {
    if (cities.length && selectedCity && !cities.some((item) => item.id === selectedCity.id)) {
      setSelectedCity(null);
    }
  }, [cities, selectedCity]);
  const description = region.type === "box"
    ? `${region.label}: ${formatCoordinates(region.south, region.west)} to ${formatCoordinates(region.north, region.east)}`
    : `${region.label} (${formatCoordinates(region.lat, region.lon)})`;
  function handleStateChange(stateId) {
    const nextState = states.find((item) => item.id === stateId);
    if (!nextState)
      return;
    setSelectedState(nextState);
    setSelectedCity(null);
    setCityQuery("");
    onChange(toPoint(nextState, `${nextState.name} (state centre)`));
  }
  function handleCityChange(cityId) {
    const nextCity = [...cities, ...searchedCities].find((item) => item.id === cityId);
    if (!nextCity)
      return;
    setSelectedCity(nextCity);
    onChange(toPoint(nextCity, `${nextCity.name}, ${nextCity.state}`));
  }
  return (
    <Space
      direction="vertical"
      size={12}
      style={{ width: "100%" }}
    >
      <Segmented
        block
        value={mode}
        onChange={setMode}
        options={MODE_OPTIONS}
        aria-label="Region type"
      />
      {mode === "area" && <Space
          direction="vertical"
          size={8}
          style={{ width: "100%" }}
        >
          <Typography.Text
            strong
          >State / Union Territory *</Typography.Text>
          <Select
            showSearch
            size="large"
            style={{ width: "100%" }}
            placeholder="Select a state or union territory"
            value={selectedState?.id}
            loading={statesLoading}
            status={statesError ? "error" : undefined}
            options={states.map((item) => ({ value: item.id, label: item.name }))}
            onChange={handleStateChange}
            filterOption={(input, option) => String(option?.label ?? "").toLowerCase().includes(input.toLowerCase())}
            aria-label="State or Union Territory"
          />
          {statesError && <Alert
              type="error"
              showIcon
              message={statesError}
            />}
          <Typography.Text
            strong
          >City (optional)</Typography.Text>
          <Select
            showSearch
            allowClear
            size="large"
            style={{ width: "100%" }}
            placeholder={selectedState ? `Select a city in ${selectedState.name}` : "Select a state first"}
            value={selectedCity?.id}
            disabled={!selectedState || citiesLoading}
            loading={citiesLoading || citySearchLoading}
            status={citiesError ? "error" : undefined}
            options={[
    ...cities.map((item) => ({ value: item.id, label: item.name })),
    ...searchedCities
      .filter((item) => !cities.some((city) => city.id === item.id))
      .map((item) => ({ value: item.id, label: item.name })),
  ]}
            onSearch={setCityQuery}
            onChange={handleCityChange}
            onClear={() => {
    setSelectedCity(null);
    if (selectedState)
      onChange(toPoint(selectedState, `${selectedState.name} (state centre)`));
  }}
            filterOption={(input, option) => String(option?.label ?? "").toLowerCase().includes(input.toLowerCase())}
            aria-label="City"
            notFoundContent={(citiesLoading || citySearchLoading) ? "Searching places..." : (cityQuery.trim().length < 3 ? "Type 3 or more letters to search more cities and towns" : "No matching place found in this state")}
          />
          {citiesError && <Alert
              type="error"
              showIcon
              message={citiesError}
            />}
          <Typography.Text
            type="secondary"
            style={{ fontSize: 12 }}
          >Choose a state to see the included cities, or type at least 3 letters to search for additional cities and towns in that state. If you leave City empty, the analysis uses the state's central grid cell (about 25 km).</Typography.Text>
        </Space>}
      {mode === "coordinates" && <CoordinatesForm
          onApply={onChange}
        />}
      {mode === "map" && <MapRegionPicker
          region={region}
          onPick={onChange}
        />}
      <Alert
        type="info"
        showIcon
        message="Selected area"
        description={description}
      />
    </Space>
  );
}
