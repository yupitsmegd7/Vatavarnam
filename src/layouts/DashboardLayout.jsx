import Sidebar from '../components/sidebar/Sidebar';

export default function DashboardLayout({ children }) {
  const outerStyle = {
    display: 'flex',
    minHeight: '100vh',
    background: 'var(--color-bg-outer)',
    boxSizing: 'border-box',
  };

  const sidebarWrapStyle = {
    position: 'sticky',
    top: 0,
    alignSelf: 'flex-start',
    height: '100vh',
    flexShrink: 0,
  };

  const contentStyle = {
    flex: 1,
    minWidth: 0,
    padding: 'var(--space-5)',
    display: 'flex',
    flexDirection: 'column',
    gap: 'var(--space-7)',
  };

  return (
    <div className="dashboard-layout" style={outerStyle}>
      <div style={sidebarWrapStyle}>
        <Sidebar userName="Vatavarnanam" />
      </div>

      <div style={contentStyle}>{children}</div>
    </div>
  );
}
