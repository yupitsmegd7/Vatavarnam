export default function ProgressBar({ percent = 0, color }) {
  const clamped = Math.min(100, Math.max(0, percent));

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
    background: color || 'var(--color-accent-green)',
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