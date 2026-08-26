export default function BarChart({ data = [], height = 150 }) {
  const containerStyle = {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    gap: 4,
    height,
    width: '100%',
    marginBottom: 'var(--space-6)',
    paddingTop: 8,
    boxSizing: 'border-box',
  };

  const colStyle = {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    flex: 1,
    minWidth: 0,
    height: '100%',
    gap: 4,
  };

  const barWrapperStyle = {
    flex: 1,
    width: '100%',
    display: 'flex',
    alignItems: 'flex-end',
    justifyContent: 'center',
    minHeight: 0,
  };

  const barStyle = (bar) => ({
    width: '100%',
    minWidth: 3,
    maxWidth: 14,
    height: `${Math.min(100, Math.max(6, bar.value * 100))}%`,
    borderRadius: 'var(--radius-full)',
    background: bar.highlighted ? 'var(--color-accent-blue)' : 'var(--color-accent-blue-soft)',
    transition: 'transform 0.2s ease, height 0.3s ease',
    cursor: 'pointer',
  });

  const topLabelStyle = {
    fontSize: 9,
    fontWeight: 700,
    color: 'var(--color-text-heading)',
    whiteSpace: 'nowrap',
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
    gap: 14,
    width: '100%',
    marginBottom: 8,
  };

  const legendItemStyle = {
    display: 'flex',
    alignItems: 'center',
    gap: 5,
    fontSize: 11,
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
    <div style={{ width: '100%', maxWidth: '100%', boxSizing: 'border-box' }}>
      <div style={legendContainerStyle}>
        <div style={legendItemStyle}>
          <div style={dotStyle(false)} /> AQI ≤ 100 (Safe)
        </div>
        <div style={legendItemStyle}>
          <div style={dotStyle(true)} /> {'AQI > 100 (Unhealthy)'}
        </div>
      </div>
      <div
        className="bar-chart"
        style={containerStyle}
        role="img"
        aria-label="Hourly pollution chart"
      >
        {data.map((bar) => (
          <div key={bar.id} style={colStyle} title={bar.tooltip || String(bar.id)}>
            {bar.topLabel !== undefined && <span style={topLabelStyle}>{bar.topLabel}</span>}
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