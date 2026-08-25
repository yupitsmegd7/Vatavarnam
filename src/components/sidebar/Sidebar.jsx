import UserProfile from './UserProfile';
import NavMenu from './NavMenu';
import { navItems } from '../../data/navItems';

export default function Sidebar({ userName = 'Arya Jha' }) {
  const sidebarStyle = {
    width: 280,
    flexShrink: 0,
    padding: 'var(--space-6) var(--space-5)',
    boxSizing: 'border-box',
  };

  return (
    <aside className="sidebar" style={sidebarStyle}>
      <UserProfile name={userName} />
      <NavMenu items={navItems} />
    </aside>
  );
}
