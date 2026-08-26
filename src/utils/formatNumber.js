/**
 * Formats a number the way the design displays values, e.g. -326.800, 872.400.
 * Uses a period as the thousands separator and always shows 3 decimal-like digits,
 * matching the numeric style used throughout the Today list and expenses panel.
 */
export function formatNumber(value) {
  const isNegative = value < 0;
  const absValue = Math.abs(value);

  const [whole, decimal = '0'] = absValue.toFixed(1).split('.');
  const paddedDecimal = decimal.padEnd(3, '0');
  const wholeWithSeparators = whole.replace(/\B(?=(\d{3})+(?!\d))/g, '.');

  return `${isNegative ? '-' : ''}${wholeWithSeparators}.${paddedDecimal}`;
}