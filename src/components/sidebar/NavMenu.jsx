import { Link, useLocation } from 'react-router-dom';

export default function NavMenu({ items }) {
  const location = useLocation();

  const listStyle = {
    display: 'flex',
    flexDirection: 'column',
    gap: 'var(--space-6)',
    margin: 0,
    padding: 0,
    listStyle: 'none',
  };

  const itemStyle = (isActive, isLinked) => ({
    background: 'none',
    border: 'none',
    padding: 0,
    textAlign: 'left',
    display: 'inline-block',
    color: isActive ? 'var(--color-text-on-dark)' : 'var(--color-text-on-dark-muted)',
    fontSize: 16,
    fontWeight: 700,
    letterSpacing: '0.01em',
    lineHeight: 1.3,
    cursor: isLinked ? 'pointer' : 'default',
    transition: 'color 0.2s ease',
  });

  return (
    <nav aria-label="Main navigation">
      <ul style={listStyle}>
        {items.map((item) => {
          const isActive = item.to === location.pathname;
          const isLinked = Boolean(item.to);

          return (
            <li key={item.id}>
              {isLinked ? (
                <Link
                  to={item.to}
                  style={itemStyle(isActive, isLinked)}
                  aria-current={isActive ? 'page' : undefined}
                  onMouseOver={(e) => {
                    if (!isActive) e.currentTarget.style.color = 'var(--color-text-on-dark)';
                  }}
                  onMouseOut={(e) => {
                    if (!isActive) e.currentTarget.style.color = 'var(--color-text-on-dark-muted)';
                  }}
                >
                  {item.label}
                </Link>
              ) : (
                <span style={itemStyle(isActive, isLinked)}>{item.label}</span>
              )}
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
