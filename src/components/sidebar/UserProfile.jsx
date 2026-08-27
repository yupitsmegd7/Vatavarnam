<<<<<<< HEAD
export default function UserProfile({ name, photoSrc }) {
  const wrapperStyle = {
    display: 'flex',
    flexDirection: 'column',
    gap: 'var(--space-4)',
    marginBottom: 'var(--space-7)',
  };

  const photoStyle = {
    width: 92,
    height: 92,
    borderRadius: 'var(--radius-md)',
    background: '#d9d3d2',
    overflow: 'hidden',
  };

  const photoImgStyle = {
    width: '100%',
    height: '100%',
    objectFit: 'cover',
  };

  const nameStyle = {
    margin: 0,
    color: 'var(--color-text-on-dark)',
    fontSize: 22,
    fontWeight: 600,
  };

  return (
    <div style={wrapperStyle}>
      <div style={photoStyle}>
        {photoSrc && <img src={photoSrc} alt={name} style={photoImgStyle} />}
      </div>
      <h2 style={nameStyle}>{name}</h2>
    </div>
  );
}
=======
export default function UserProfile({ name }) {
  const wrapperStyle = {
    display: 'flex',
    flexDirection: 'column',
    gap: 'var(--space-3)',
    marginBottom: 'var(--space-7)',
    alignItems: 'flex-start',
  };

  const logoStyle = {
    width: 140,
    height: 140,
    borderRadius: 'var(--radius-md)',
    overflow: 'hidden',
    background: '#0d0d0d',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  };

  const logoImgStyle = {
    width: '100%',
    height: '100%',
    objectFit: 'contain',
  };

  const nameStyle = {
    margin: 0,
    color: 'var(--color-text-on-dark)',
    fontSize: 22,
    fontWeight: 600,
  };

  return (
    <div style={wrapperStyle}>
      <div style={logoStyle}>
        <img src="/logo.png" alt="Vatavarnam Logo" style={logoImgStyle} />
      </div>
      <h2 style={nameStyle}>{name}</h2>
    </div>
  );
}
>>>>>>> prototype1
