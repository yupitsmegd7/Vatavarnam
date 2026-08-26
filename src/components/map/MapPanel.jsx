export default function MapPanel({ src, alt = 'Hotspot map', label = 'Delhi NCR — hotspot map' }) {
  const wrapperStyle = {
    width: 340,
    flexShrink: 0,
    borderRadius: 'var(--radius-xl)',
    overflow: 'hidden',
    background: '#16232a',
  };

  const imgStyle = {
    width: '100%',
    height: '100%',
    objectFit: 'cover',
    display: 'block',
  };

  const placeholder = (
    <svg viewBox="0 0 340 480" width="100%" height="100%" role="img" aria-label={alt}>
      <rect width="340" height="480" fill="#16232a" />
      <g stroke="#2c3f47" strokeWidth="2" fill="none">
        <path d="M0 120 L340 90" />
        <path d="M0 220 L340 260" />
        <path d="M0 360 L340 330" />
        <path d="M60 0 L100 480" />
        <path d="M230 0 L200 480" />
      </g>
      <g fill="#e55353">
        <circle cx="120" cy="140" r="6" />
        <circle cx="180" cy="180" r="6" />
        <circle cx="90" cy="260" r="6" />
        <circle cx="220" cy="240" r="6" />
        <circle cx="160" cy="320" r="6" />
        <circle cx="240" cy="360" r="6" />
      </g>
      <text x="170" y="450" fill="#8a99a1" fontSize="14" textAnchor="middle" fontFamily="sans-serif">
        {label}
      </text>
    </svg>
  );

  return (
    <div className="map-panel" style={wrapperStyle}>
      {src ? <img src={src} alt={alt} style={imgStyle} /> : placeholder}
    </div>
  );
}
