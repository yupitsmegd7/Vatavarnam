export default function Button({ children, variant = 'dark', onClick, ...rest }) {
  const baseStyle = {
    border: 'none',
    borderRadius: 'var(--radius-md)',
    padding: '14px 20px',
    fontWeight: 700,
    fontSize: 13,
    letterSpacing: '0.04em',
    textTransform: 'uppercase',
    fontFamily: 'inherit',
    cursor: 'pointer',
    width: '100%',
    transition: 'opacity 0.2s ease, transform 0.2s ease',
  };

  const variants = {
    dark: {
      background: '#17151f',
      color: '#ffffff',
    },
    light: {
      background: '#ffffff',
      color: '#17151f',
      border: '1px solid rgba(0, 0, 0, 0.1)',
    },
  };

  const style = {
    ...baseStyle,
    ...(variants[variant] ?? variants.dark),
  };

  return (
    <button
      className={`btn btn--${variant}`}
      style={style}
      onClick={onClick}
      onMouseOver={(e) => (e.currentTarget.style.opacity = '0.9')}
      onMouseOut={(e) => (e.currentTarget.style.opacity = '1')}
      {...rest}
    >
      {children}
    </button>
  );
}