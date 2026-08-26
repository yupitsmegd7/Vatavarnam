export default function Card({ children, style, as: Tag = 'div', ...rest }) {
  const baseStyle = {
    background: 'var(--color-bg-panel-item)',
    borderRadius: 'var(--radius-lg)',
  };

  return (
    <Tag className="card" style={{ ...baseStyle, ...style }} {...rest}>
      {children}
    </Tag>
  );
}