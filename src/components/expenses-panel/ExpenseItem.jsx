import ProgressBar from '../common/ProgressBar';

function formatNumber(value) {
  const isNegative = value < 0;
  const absValue = Math.abs(value);

  const [whole, decimal = '0'] = absValue.toFixed(1).split('.');
  const paddedDecimal = decimal.padEnd(3, '0');
  const wholeWithSeparators = whole.replace(/\B(?=(\d{3})+(?!\d))/g, '.');

  return `${isNegative ? '-' : ''}${wholeWithSeparators}.${paddedDecimal}`;
}

export default function ExpenseItem({ label, value, percent }) {
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
  };

  const valueStyle = {
    fontSize: 14,
    fontWeight: 600,
    color: 'var(--color-text-on-dark-muted)',
  };

  return (
    <div style={itemStyle}>
      <div style={rowStyle}>
        <span style={labelStyle}>{label}</span>
        <span style={valueStyle}>{formatNumber(value)}</span>
      </div>
      <ProgressBar percent={percent} />
    </div>
  );
}