export function ColorDot({ color, size = 10 }) {
  return (
    <span
      aria-hidden="true"
      style={{ display: "inline-block", 
        width: size,
        height: size, 
        borderRadius: "50%", 
        background: color, 
        flex: "none" }}
    />
  );
}
