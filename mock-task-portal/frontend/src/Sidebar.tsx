import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from './AuthContext';

const NAV = [
  { to: '/',                  label: 'Dashboard',          roles: ['SUPERADMIN','DEVELOPER','TESTER','DELIVERY','VIEWER'] },
  { to: '/tasks',             label: 'Task List',           roles: ['SUPERADMIN','DEVELOPER','TESTER','DELIVERY','VIEWER'] },
  { to: '/tasks/create',      label: 'Create Task',         roles: ['SUPERADMIN'] },
  { to: '/developer-view',    label: 'My Tasks (Dev)',      roles: ['DEVELOPER'] },
  { to: '/testing-l2-queue',  label: 'Testing L2 Queue',    roles: ['SUPERADMIN','TESTER'] },
  { to: '/rework-queue',      label: 'Rework Queue',        roles: ['SUPERADMIN','DEVELOPER','TESTER'] },
  { to: '/delivery-ready',    label: 'Delivery Ready',      roles: ['SUPERADMIN','DELIVERY'] },
  { to: '/delivery-completed',label: 'Delivery Completed',  roles: ['SUPERADMIN','DELIVERY'] },
];

export default function Sidebar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  if (!user) return null;

  const filteredNav = NAV.filter(n => n.roles.includes(user.role));

  async function handleLogout() {
    await logout();
    navigate('/login');
  }

  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        ⬡ Mock Task Portal
      </div>
      <div className="sidebar-user">
        <strong>{user.display_name}</strong>
        {user.role}
      </div>
      <nav className="sidebar-nav">
        {filteredNav.map(n => (
          <NavLink
            key={n.to}
            to={n.to}
            end={n.to === '/'}
            className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}
          >
            {n.label}
          </NavLink>
        ))}
      </nav>
      <div className="sidebar-footer">
        <button className="btn btn-ghost" style={{width:'100%',justifyContent:'center'}} onClick={handleLogout}>
          Logout
        </button>
      </div>
    </aside>
  );
}
