export default function BarChart({ data = [], height = 130 }) {
  const containerStyle = {
    display: 'flex',
    alignItems: 'flex-end',
    gap: 10,
    height,
    marginBottom: 'var(--space-6)',
  };

  const barStyle = (bar) => ({
    flex: 1,
    minWidth: 6,
    maxWidth: 22,
    height: `${bar.value * 100}%`,
    borderRadius: 'var(--radius-full)',
    background: bar.highlighted ? 'var(--color-accent-blue)' : 'var(--color-accent-blue-soft)',
    transition: 'transform 0.2s ease',
  });

  return (
    <div
      className="bar-chart"
      style={containerStyle}
      role="img"
      aria-label="Hourly prediction chart"
    >
      {data.map((bar) => (
        <div
          key={bar.id}
          style={barStyle(bar)}
          onMouseOver={(e) => (e.currentTarget.style.transform = 'scaleY(1.03)')}
          onMouseOut={(e) => (e.currentTarget.style.transform = 'scaleY(1)')}
        />
      ))}
    </div>
  );
}