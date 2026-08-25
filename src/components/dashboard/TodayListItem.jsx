import IconBadge from '../common/IconBadge';

function formatNumber(value) {
  const isNegative = value < 0;
  const absValue = Math.abs(value);

  const [whole, decimal = '0'] = absValue.toFixed(1).split('.');
  const paddedDecimal = decimal.padEnd(3, '0');
  const wholeWithSeparators = whole.replace(/\B(?=(\d{3})+(?!\d))/g, '.');

  return `${isNegative ? '-' : ''}${wholeWithSeparators}.${paddedDecimal}`;
}

export default function TodayListItem({ item }) {
  const { label, time, place, value, icon, color } = item;

  const rowStyle = {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: 'var(--space-4) 0',
  };

  const leadingStyle = {
    display: 'flex',
    alignItems: 'center',
    gap: 'var(--space-4)',
  };

  const labelStyle = {
    margin: '0 0 2px',
    fontSize: 18,
    fontWeight: 700,
    color: 'var(--color-text-heading)',
  };

  const metaStyle = {
    margin: 0,
    fontSize: 14,
    color: 'var(--color-text-muted)',
  };

  const valueStyle = {
    fontSize: 18,
    fontWeight: 700,
    color: 'var(--color-text-heading)',
  };

  return (
    <div style={rowStyle}>
      <div style={leadingStyle}>
        <IconBadge icon={icon} color={color} />
        <div>
          <p style={labelStyle}>{label}</p>
          <p style={metaStyle}>
            {time} &nbsp;&bull;&nbsp; {place}
          </p>
        </div>
      </div>
      <span style={valueStyle}>{formatNumber(value)}</span>
    </div>
  );
}