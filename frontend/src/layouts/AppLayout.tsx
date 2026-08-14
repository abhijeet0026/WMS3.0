import React from 'react';
import { Outlet, Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { LogOut, Package } from 'lucide-react';
import { AssistantWidget } from '../components/app/AssistantWidget';
import '../styles/tokens.css';
import '../styles/app.css';

export const AppLayout: React.FC = () => {
  const { currentUser, logout, permissions } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const navLinks = [
    { path: '/app/dashboard', label: 'Dashboard', show: true },
    { path: '/app/receive', label: 'Receiving', show: true },
    { path: '/app/ship', label: 'Shipping', show: true },
    { path: '/app/audit-log', label: 'Audit Trail', show: permissions.canViewAuditLog },
    { path: '/app/reconciliation', label: 'Legacy Sync', show: permissions.canExecuteMigration },
    { path: '/app/accounts', label: 'Staff Accounts', show: permissions.canManageStaffFor('RENO') || permissions.canManageStaffFor('COLUMBUS') },
  ];

  // Derive current page title
  const currentLink = navLinks.find(l => location.pathname === l.path);

  return (
    <div className="app-wrapper">
      <nav className="app-nav">
        <Link to="/app/dashboard" className="app-nav-brand" aria-label="Go to dashboard">
          <div className="app-nav-brand-mark">
            <Package size={18} />
          </div>
          <div className="app-nav-brand-text">
            <span className="app-nav-brand-accent">WHITFIELD</span>
            <span className="app-nav-brand-sep" />
            <span className="app-nav-brand-sub">WMS</span>
          </div>
        </Link>

        <div className="app-nav-links">
          {navLinks.filter(link => link.show).map(link => (
            <Link
              key={link.path}
              to={link.path}
              className={location.pathname === link.path ? 'active' : ''}
            >
              {link.label}
            </Link>
          ))}
        </div>

        <div className="app-nav-user">
          <div className="app-user-meta">
            <span className="app-user-name">{currentUser?.full_name}</span>
            <div className="app-user-meta-row">
              <span data-testid="current-user-role" className="badge badge-neutral app-user-role">
                {currentUser?.role}
              </span>
              {currentUser?.facility_scope && (
                <span data-testid="facility-label" className="app-user-facility">
                  {currentUser.facility_scope}
                </span>
              )}
            </div>
          </div>
          <button onClick={handleLogout} className="btn-secondary app-nav-logout">
            <LogOut size={13} /> Sign Out
          </button>
        </div>
      </nav>

      {currentLink && (
        <div className="app-subheader">
          <span>Whitfield WMS</span>
          <span className="app-subheader-arrow">›</span>
          <span className="app-subheader-title">{currentLink.label}</span>
        </div>
      )}

      <main className="app-main">
        <Outlet />
      </main>

      <AssistantWidget />
    </div>
  );
};
