<<<<<<< HEAD
import { Link, useLocation } from 'react-router-dom';

export default function NavMenu({ items }) {
  const location = useLocation();
=======
import { useEffect, useState } from 'react';

export default function NavMenu({ items }) {
  const scrollTargets = items.filter((item) => item.target);
  const [activeId, setActiveId] = useState(scrollTargets[0]?.id ?? null);

  useEffect(() => {
    if (scrollTargets.length === 0) return undefined;

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const matched = scrollTargets.find((item) => item.target === entry.target.id);
            if (matched) setActiveId(matched.id);
          }
        });
      },
      // Treat a section as "active" once it's roughly in the vertical middle
      // of the viewport, rather than only when fully in view.
      { rootMargin: '-35% 0px -55% 0px', threshold: 0 }
    );

    scrollTargets.forEach((item) => {
      const el = document.getElementById(item.target);
      if (el) observer.observe(el);
    });

    return () => observer.disconnect();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [items]);

  const handleClick = (item) => {
    if (!item.target) return;
    const el = document.getElementById(item.target);
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'start' });
      setActiveId(item.id);
    }
  };
>>>>>>> prototype1

  const listStyle = {
    display: 'flex',
    flexDirection: 'column',
    gap: 'var(--space-6)',
    margin: 0,
    padding: 0,
    listStyle: 'none',
  };

<<<<<<< HEAD
  const itemStyle = (isActive, isLinked) => ({
=======
  const itemStyle = (isActive, isClickable) => ({
>>>>>>> prototype1
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
<<<<<<< HEAD
    cursor: isLinked ? 'pointer' : 'default',
=======
    cursor: isClickable ? 'pointer' : 'default',
>>>>>>> prototype1
    transition: 'color 0.2s ease',
  });

  return (
    <nav aria-label="Main navigation">
      <ul style={listStyle}>
        {items.map((item) => {
<<<<<<< HEAD
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
=======
          const isActive = item.id === activeId;
          const isClickable = Boolean(item.target);

          return (
            <li key={item.id}>
              <button
                type="button"
                style={itemStyle(isActive, isClickable)}
                aria-current={isActive ? 'page' : undefined}
                onClick={() => handleClick(item)}
                onMouseOver={(e) => {
                  if (!isActive && isClickable) e.currentTarget.style.color = 'var(--color-text-on-dark)';
                }}
                onMouseOut={(e) => {
                  if (!isActive && isClickable) e.currentTarget.style.color = 'var(--color-text-on-dark-muted)';
                }}
              >
                {item.label}
              </button>
>>>>>>> prototype1
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
