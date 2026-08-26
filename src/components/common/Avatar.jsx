export default function Avatar({ src, alt = '', size = 40, fallbackColor = '#e8e2e1' }) {
  const avatarStyle = {
    display: 'inline-flex',
    width: size,
    height: size,
    borderRadius: '50%',
    overflow: 'hidden',
    border: '2px solid var(--color-bg-card)',
    flexShrink: 0,
    backgroundColor: src ? 'transparent' : fallbackColor,
  };

  const imgStyle = {
    width: '100%',
    height: '100%',
    objectFit: 'cover',
  };

  return (
    <span className="avatar" style={avatarStyle}>
      {src && <img src={src} alt={alt} style={imgStyle} />}
    </span>
  );
}