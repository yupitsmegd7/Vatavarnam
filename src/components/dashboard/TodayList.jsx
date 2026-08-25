import TodayListItem from './TodayListItem';

export default function TodayList({ items = [] }) {
  const headerStyle = {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 'var(--space-2)',
  };

  const titleStyle = {
    margin: 0,
    fontSize: 24,
    fontWeight: 800,
    color: 'var(--color-text-heading)',
  };

  const moreButtonStyle = {
    background: 'none',
    border: 'none',
    color: 'var(--color-text-muted)',
    fontSize: 14,
    letterSpacing: 2,
    cursor: 'pointer',
  };

  const listStyle = {
    borderTop: '1px solid rgba(0, 0, 0, 0.06)',
    margin: 0,
    padding: 0,
    listStyle: 'none',
  };

  return (
    <section>
      <div style={headerStyle}>
        <h2 style={titleStyle}>Today</h2>
        <button type="button" style={moreButtonStyle} aria-label="More options">
          &bull;&bull;&bull;
        </button>
      </div>
      <ul style={listStyle}>
        {items.map((item, index) => (
          <li
            key={item.id}
            style={{
              borderTop: index === 0 ? 'none' : '1px solid rgba(0, 0, 0, 0.06)',
            }}
          >
            <TodayListItem item={item} />
          </li>
        ))}
      </ul>
    </section>
  );
}