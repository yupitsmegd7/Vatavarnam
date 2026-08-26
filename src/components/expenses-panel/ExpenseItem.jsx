import ProgressBar from '../common/ProgressBar';

function formatNumber(value) {
  const isNegative = value < 0;
  const absValue = Math.abs(value);

  const [whole, decimal = '0'] = absValue.toFixed(1).split('.');
  const paddedDecimal = decimal.padEnd(1, '0');
  const wholeWithSeparators = whole.replace(/\B(?=(\d{3})+(?!\d))/g, '.');

  return `${isNegative ? '-' : ''}${wholeWithSeparators}.${paddedDecimal}`;
}

export default function ExpenseItem({ label, value, percent, color, severity, model }) {
  const itemStyle = {
    display: 'flex',
    flexDirection: 'column',
    gap: 'var(--space-2)',
  };

  const rowStyle = {
    display: 'flex',
    alignItems: 'baseline',
    justifyContent: 'space-between',
  };

  const labelStyle = {
    fontSize: 15,
    fontWeight: 600,
    color: 'var(--color-text-on-dark)',
    display: 'flex',
    alignItems: 'center',
    gap: 6,
  };

  const valueStyle = {
    fontSize: 14,
    fontWeight: 600,
    color: 'var(--color-text-on-dark-muted)',
    display: 'flex',
    alignItems: 'center',
    gap: 6,
  };

  const severityDotStyle = {
    width: 6,
    height: 6,
    borderRadius: '50%',
    backgroundColor: color || '#10b981',
    boxShadow: `0 0 5px ${color || '#10b981'}`,
    display: 'inline-block',
  };

  return (
    <div style={itemStyle}>
      <div style={rowStyle}>
        <span style={labelStyle}>
          {color && <span style={severityDotStyle} title={severity || 'Severity Indicator'} />}
          {label}
        </span>
        <span style={valueStyle}>
          {formatNumber(value)}
        </span>
      </div>
      <ProgressBar percent={percent} color={color} />
    </div>
  );
}