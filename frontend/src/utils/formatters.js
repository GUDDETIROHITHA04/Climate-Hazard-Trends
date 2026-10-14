export const formatSigned = (value, digits = 2) => {
  if (value === null || value === undefined || Number.isNaN(value))
    return "n/a";
  const rounded = Number(value.toFixed(digits));
  return rounded > 0 ? `+${rounded}` : String(rounded);
};
export const capitalize = (text) => (text ? text[0].toUpperCase() + text.slice(1) : text);
export const formatPercent = (fraction) => `${Math.round(fraction * 100)}%`;
export const formatCoordinates = (lat, lon) => `${Math.abs(lat).toFixed(2)}°${lat >= 0 ? "N" : "S"}, ${Math.abs(lon).toFixed(2)}°${lon >= 0 ? "E" : "W"}`;
