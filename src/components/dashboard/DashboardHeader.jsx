import AvatarGroup from '../common/AvatarGroup';

export default function DashboardHeader({ title, dateRange, collaborators = [] }) {
  const headerStyle = {
    display: 'flex',
    alignItems: 'flex-start',
    justifyContent: 'space-between',
    marginBottom: 'var(--space-6)',
  };

  const titleStyle = {
    margin: '0 0 8px',
    fontSize: 40,
    fontWeight: 800,
    color: 'var(--color-text-heading)',
    letterSpacing: '-0.01em',
  };

  const dateStyle = {
    margin: 0,
    color: 'var(--color-text-muted)',
    fontSize: 15,
    fontWeight: 500,
  };

  return (
    <header className="dashboard-header" style={headerStyle}>
      <div>
        <h1 style={titleStyle}>{title}</h1>
        <p style={dateStyle}>{dateRange}</p>
      </div>
      <AvatarGroup avatars={collaborators} />
    </header>
  );
}