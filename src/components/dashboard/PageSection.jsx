export default function PageSection({ id, children, rightPanel }) {
  const rowStyle = {
    display: 'flex',
    alignItems: 'flex-start',
    gap: 'var(--space-5)',
    scrollMarginTop: 'var(--space-5)',
  };

  const cardStyle = {
    flex: 1,
    minWidth: 0,
    background: 'var(--color-bg-card)',
    borderRadius: 'var(--radius-xl)',
    padding: 'var(--space-6) var(--space-7)',
    boxSizing: 'border-box',
  };

  return (
    <section id={id} style={rowStyle}>
      <div style={cardStyle}>{children}</div>
      {rightPanel}
    </section>
  );
}
