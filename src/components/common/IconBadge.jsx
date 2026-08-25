const ICON_PATHS = {
  cart: (
    <path d="M6 6h15l-1.5 9h-12L6 6Zm0 0-1-3H2m6 18a1 1 0 1 0 0-2 1 1 0 0 0 0 2Zm10 0a1 1 0 1 0 0-2 1 1 0 0 0 0 2Z" />
  ),
  bus: (
    <path d="M4 16V6a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v10M4 16a2 2 0 0 0 2 2h1a1 1 0 0 0 1-1v-1h8v1a1 1 0 0 0 1 1h1a2 2 0 0 0 2-2M4 16h16M7 10h10" />
  ),
  home: (
    <path d="M4 11.5 12 4l8 7.5M6 10v9a1 1 0 0 0 1 1h4v-6h2v6h4a1 1 0 0 0 1-1v-9" />
  ),
};

export default function IconBadge({ icon = 'home', color = 'var(--icon-navy)', size = 44 }) {
  const badgeStyle = {
    display: 'inline-flex',
    alignItems: 'center',
    justifyContent: 'center',
    width: size,
    height: size,
    borderRadius: '50%',
    backgroundColor: color,
    flexShrink: 0,
  };

  return (
    <span className="icon-badge" style={badgeStyle}>
      <svg
        width={size * 0.45}
        height={size * 0.45}
        viewBox="0 0 24 24"
        fill="none"
        stroke="white"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      >
        {ICON_PATHS[icon] ?? ICON_PATHS.home}
      </svg>
    </span>
  );
}