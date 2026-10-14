import { Segmented, Typography } from "antd";
import { useState } from "react";
import { CircleMarker, MapContainer, Rectangle, TileLayer, useMapEvents } from "react-leaflet";
import { MAX_BOX_DEGREES } from "@/constants/analysis";
function ClickHandler({ onClick }) {
  useMapEvents({ click: (event) => onClick(event.latlng.lat, event.latlng.lng) });
  return null;
}
const normaliseLongitude = (lng) => ((((lng + 180) % 360) + 360) % 360) - 180;
export function MapRegionPicker({ region, onPick }) {
  const [mode, setMode] = useState("point");
  const [corner, setCorner] = useState(null);
  const [warning, setWarning] = useState(null);
  function handleClick(rawLat, rawLng) {
    setWarning(null);
    const lat = +rawLat.toFixed(3);
    const lon = +normaliseLongitude(rawLng).toFixed(3);
    if (mode === "point") {
      onPick({ type: "point", lat, lon, label: `${lat}°, ${lon}°` });
      return;
    }
    if (!corner) {
      setCorner({ lat, lon });
      return;
    }
    const south = Math.min(corner.lat, lat), north = Math.max(corner.lat, lat);
    const west = Math.min(corner.lon, lon), east = Math.max(corner.lon, lon);
    setCorner(null);
    if (north - south > MAX_BOX_DEGREES || east - west > MAX_BOX_DEGREES || north === south || east === west) {
      setWarning(`The box must have an area and be at most ${MAX_BOX_DEGREES}° on each side.`);
      return;
    }
    onPick({ type: "box", south, west, north, east, label: "Custom box" });
  }
  const hint = mode === "box" ? (corner ? "Now click the opposite corner." : "Click one corner, then the opposite corner.") : "Click anywhere on the map.";
  return (
    <div>
      <Segmented
        block
        value={mode}
        onChange={(next) => { setMode(next); setCorner(null); }}
        options={[{ label: "Click a point", value: "point" }, { label: "Draw a box", value: "box" }]}
      />
      <Typography.Paragraph
        type="secondary"
        style={{ margin: "8px 0", fontSize: 13 }}
      >
        {hint}
      </Typography.Paragraph>
      <div
        className="map-frame"
      >
        <MapContainer
          center={[20, 78]}
          zoom={4}
          scrollWheelZoom
          style={{ height: "100%", width: "100%" }}
        >
          <TileLayer
            attribution="© OpenStreetMap contributors"
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          <ClickHandler
            onClick={handleClick}
          />
          {region.type === "box" ? (<Rectangle
              bounds={[[region.south, region.west], [region.north, region.east]]}
            />) : (<CircleMarker
              center={[region.lat, region.lon]}
              radius={8}
            />)}
          {corner && <CircleMarker
              center={[corner.lat, corner.lon]}
              radius={5}
            />}
        </MapContainer>
      </div>
      {warning && <Typography.Text
          type="danger"
        >
          {warning}
        </Typography.Text>}
    </div>
  );
}
