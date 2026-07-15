import { useAuth } from '../authContext';
const navItems = ['Platform', 'Products', 'Dashboard', 'Test Management', 'Connection Targets', 'Automated Runs', 'Defects', 'Management Reports', 'System Health', 'Test Agents', 'Solutions', 'Resources', 'About'];
export function Header() {
  const { operator, logout } = useAuth();
  return <header className="site-header"><div className="header-inner"><a className="brand" href="#top"><span className="brand-mark">i5</span><span>iFive AutoQA</span></a><nav className="main-nav" aria-label="Primary navigation">{navItems.map((item) => <a href={`#${item.toLowerCase().replaceAll(' ', '-')}`} key={item}>{item}</a>)}</nav><div className="header-actions operator-header"><span>{operator.display_name}</span><strong className="role-badge">{operator.role}</strong><button className="button button-secondary" onClick={() => void logout()}>Logout</button></div></div></header>;
}
