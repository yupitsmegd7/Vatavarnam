export default function ProgressBar({ percent = 0, color }) {
  const clamped = Math.min(100, Math.max(0, percent));

  const getDynamicColor = (pct) => {
    if (pct <= 25) return '#10b981'; // Green
    if (pct <= 50) return '#facc15'; // Yellow
    if (pct <= 75) return '#f97316'; // Orange
    return '#ef4444'; // Red
  };

  const trackStyle = {
    width: '100%',
    height: 4,
    borderRadius: 'var(--radius-full)',
    background: 'var(--color-track)',
    overflow: 'hidden',
  };

  const fillStyle = {
    height: '100%',
    width: `${clamped}%`,
    background: color || getDynamicColor(clamped),
    borderRadius: 'var(--radius-full)',
    transition: 'width 0.4s ease, background 0.3s ease',
  };

  return (
    <div
      className="progress-bar"
      style={trackStyle}
      role="progressbar"
      aria-valuenow={clamped}
      aria-valuemin={0}
      aria-valuemax={100}
    >
      <div style={fillStyle} />
    </div>
  );
}