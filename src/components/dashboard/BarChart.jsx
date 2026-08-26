export default function BarChart({ data = [], height = 160 }) {
  const containerStyle = {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    gap: 4,
    height,
    marginBottom: 'var(--space-6)',
    paddingTop: 10,
  };

  const colStyle = {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    flex: 1,
    height: '100%',
    gap: 4,
  };

  const barWrapperStyle = {
    flex: 1,
    width: '100%',
    display: 'flex',
    alignItems: 'flex-end',
    justifyContent: 'center',
  };

  const barStyle = (bar) => ({
    width: '100%',
    minWidth: 4,
    maxWidth: 12,
    height: `${bar.value * 100}%`,
    borderRadius: 'var(--radius-full)',
    background: bar.highlighted ? 'var(--color-accent-blue)' : 'var(--color-accent-blue-soft)',
    transition: 'transform 0.2s ease',
    cursor: 'pointer',
  });

  const topLabelStyle = {
    fontSize: 9,
    fontWeight: 700,
    color: 'var(--color-text-heading)',
  };

  const bottomLabelStyle = {
    fontSize: 9,
    color: 'var(--color-text-muted)',
    fontWeight: 600,
    whiteSpace: 'nowrap',
  };

  const legendContainerStyle = {
    display: 'flex',
    justifyContent: 'flex-end',
    gap: 12,
    width: '100%',
    marginBottom: 10,
  };

  const legendItemStyle = {
    display: 'flex',
    alignItems: 'center',
    gap: 4,
    fontSize: 10,
    color: 'var(--color-text-muted)',
    fontWeight: 600,
  };

  const dotStyle = (highlighted) => ({
    width: 8,
    height: 8,
    borderRadius: '50%',
    background: highlighted ? 'var(--color-accent-blue)' : 'var(--color-accent-blue-soft)',
  });

  return (
    <div style={{ width: '100%', marginBottom: 'var(--space-6)' }}>
      <div style={legendContainerStyle}>
        <div style={legendItemStyle}>
          <div style={dotStyle(false)} /> AQI ≤ 100 (Safe)
        </div>
        <div style={legendItemStyle}>
          <div style={dotStyle(true)} /> AQI > 100 (Unhealthy)
        </div>
      </div>
      <div
        className="bar-chart"
        style={containerStyle}
        role="img"
        aria-label="Hourly pollution chart"
      >
        {data.map((bar) => (
          <div key={bar.id} style={colStyle} title={bar.tooltip || bar.id}>
            {bar.topLabel && <span style={topLabelStyle}>{bar.topLabel}</span>}
            <div style={barWrapperStyle}>
              <div
                style={barStyle(bar)}
                onMouseOver={(e) => (e.currentTarget.style.transform = 'scaleY(1.05)')}
                onMouseOut={(e) => (e.currentTarget.style.transform = 'scaleY(1)')}
              />
            </div>
            <span style={bottomLabelStyle}>{bar.label || String(bar.id).substring(8, 10)}</span>
          </div>
        ))}
      </div>
    </div>
  );
}