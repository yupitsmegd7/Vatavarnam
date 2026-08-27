import Sidebar from '../components/sidebar/Sidebar';
<<<<<<< HEAD
import ExpensesPanel from '../components/expenses-panel/ExpensesPanel';
import { expensesData } from '../data/expensesData';

export default function DashboardLayout({ children, rightPanel }) {
  const layoutStyle = {
    display: 'flex',
    minHeight: '100vh',
    background: 'var(--color-bg-outer)',
    padding: 'var(--space-5)',
    gap: 'var(--space-5)',
    boxSizing: 'border-box',
  };

  const mainStyle = {
    flex: 1,
    minWidth: 0,
    display: 'flex',
  };

  const cardStyle = {
    flex: 1,
    background: 'var(--color-bg-card)',
    borderRadius: 'var(--radius-xl)',
    padding: 'var(--space-6) var(--space-7)',
    boxSizing: 'border-box',
  };

  const defaultRightPanel = (
    <ExpensesPanel
      title="Where your money go?"
      items={expensesData}
      mission={{
        title: 'Serenity in Vicinity',
        description:
          'Creating awareness about the air that surrounds us and our loved ones.',
        ctaLabel: 'Our Mission',
      }}
    />
  );

  return (
    <div className="dashboard-layout" style={layoutStyle}>
      <Sidebar userName="Arya Jha" />

      <main style={mainStyle}>
        <div style={cardStyle}>{children}</div>
      </main>

      {rightPanel ?? defaultRightPanel}
=======

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
>>>>>>> prototype1
    </div>
  );
}
