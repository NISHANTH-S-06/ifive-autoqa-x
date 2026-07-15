import { useAuth } from '../authContext';
import { ChangePasswordPanel } from './PasswordControls';
import { MySessionsPanel } from './SessionPanels';

export function AccountSecurityPanel() {
  const { operator } = useAuth();
  return <section className="section" id="account-security"><div className="section-inner"><div className="section-title"><h2>Account Security</h2><p>Manage your local password and active sessions.</p></div><div className="split"><ChangePasswordPanel username={operator.username} displayName={operator.display_name} /><MySessionsPanel /></div></div></section>;
}
