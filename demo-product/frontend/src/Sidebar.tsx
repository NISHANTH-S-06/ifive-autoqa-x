import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from './AuthContext';

const NAV_ITEMS = [
  { to: '/dashboard', label: 'Dashboard', roles: ['DEMO_ADMIN', 'HR_USER', 'INVENTORY_USER', 'VIEWER'] },
  { to: '/hr/employees', label: 'Employees', roles: ['DEMO_ADMIN', 'HR_USER', 'VIEWER'] },
  { to: '/hr/employees/new', label: '+ Create Employee', roles: ['DEMO_ADMIN', 'HR_USER'] },
  { to: '/inventory/products', label: 'Product List', roles: ['DEMO_ADMIN', 'INVENTORY_USER', 'VIEWER'] },
  { to: '/inventory/stock-count', label: 'Stock Count', roles: ['DEMO_ADMIN', 'INVENTORY_USER'] },
  { to: '/demo-settings', label: '⚙ Demo Bug Toggles', roles: ['DEMO_ADMIN'] },
];

export default function Sidebar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  if (!user) return null;

  const userRole = user.role;
  const filteredNav = NAV_ITEMS.filter(item => item.roles.includes(userRole));

  async function handleLogout() {
    await logout();
    navigate('/login');
  }

  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        📦 Demo ERP Product
      </div>
      <div className="sidebar-user">
        <strong>{user.display_name}</strong>
        <span style={{ fontSize: 11 }}>Role: {user.role}</span>
      </div>
      <nav className="sidebar-nav">
        {filteredNav.map(item => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}
          >
            {item.label}
          </NavLink>
        ))}
      </nav>
      <div className="sidebar-footer">
        <button className="btn btn-ghost" style={{ width: '100%' }} onClick={handleLogout}>
          Logout
        </button>
      </div>
    </aside>
  );
}
