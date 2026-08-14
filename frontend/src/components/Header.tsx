import React from 'react';
import { Warehouse, UserCheck, Activity, LogOut, Home, RefreshCw, Mail, ShieldAlert } from 'lucide-react';
import { User, UserRole } from '../types/wms';
import { usePermissions } from '../hooks/usePermissions';

interface HeaderProps {
  currentUser: User | null;
  currentRole: UserRole;
  selectedWarehouse: string;
  setSelectedWarehouse: (wh: string) => void;
  activeTab: string;
  setActiveTab: (tab: string) => void;
  onLogout: () => void;
  onNavigateToLanding: () => void;
  onNavigateToLogin: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  currentUser,
  currentRole,
  selectedWarehouse,
  setSelectedWarehouse,
  activeTab,
  setActiveTab,
  onLogout,
  onNavigateToLanding,
  onNavigateToLogin,
}) => {
  const getRoleBadgeStyle = (role: UserRole) => {
    switch (role) {
      case 'OWNER':
        return { bg: 'rgba(99, 102, 241, 0.2)', border: 'rgba(99, 102, 241, 0.4)', text: '#a5b4fc', label: 'Owner (Admin)' };
      case 'MANAGER':
        return { bg: 'rgba(16, 185, 129, 0.2)', border: 'rgba(16, 185, 129, 0.4)', text: '#6ee7b7', label: 'Facility Manager' };
      case 'TRUSTED_STAFF':
        return { bg: 'rgba(6, 182, 212, 0.2)', border: 'rgba(6, 182, 212, 0.4)', text: '#67e8f9', label: 'Trusted Staff' };
      case 'NEW_HIRE':
        return { bg: 'rgba(245, 158, 11, 0.2)', border: 'rgba(245, 158, 11, 0.4)', text: '#fde047', label: 'New Hire' };
    }
  };

  const roleStyle = getRoleBadgeStyle(currentRole);
  const permissions = usePermissions(currentUser);

  return (
    <header className="glass-panel" style={{ borderRadius: 0, borderTop: 0, borderLeft: 0, borderRight: 0, padding: '0.85rem 2rem', position: 'sticky', top: 0, zIndex: 50 }}>
      <div style={{ maxWidth: '1400px', margin: '0 auto', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
        
        {/* Brand Logo */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
          <div 
            onClick={onNavigateToLanding}
            title="Return to Landing Page"
            style={{ width: '42px', height: '42px', borderRadius: '10px', background: 'linear-gradient(135deg, #6366f1, #10b981)', display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: '0 4px 14px rgba(99, 102, 241, 0.4)', cursor: 'pointer' }}
          >
            <Warehouse size={24} color="#ffffff" />
          </div>
          <div>
            <h1 style={{ fontSize: '1.2rem', lineHeight: '1.2', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              Whitfield Fulfillment WMS
              <span className="badge badge-success" style={{ fontSize: '0.65rem' }}>
                <Activity size={10} /> Live DB Lock
              </span>
            </h1>
            <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Reno, NV & Columbus, OH Facilities</p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', background: 'rgba(15, 23, 42, 0.6)', padding: '0.3rem', borderRadius: '10px', border: '1px solid var(--border-color)' }}>
          {[
            { id: 'dashboard', label: 'Dashboard' },
            { id: 'receiving', label: 'Receiving (UPC Scan)' },
            { id: 'shipping', label: 'Shipping (Pick & Pack)' },
            ...(permissions.canViewAuditLog ? [{ id: 'audit', label: 'Audit Trail (Who/What)' }] : []),
            ...(permissions.canExecuteMigration ? [{ id: 'migration', label: 'Excel Data Cleanup' }] : []),
            ...(permissions.canManageStaffFor('RENO') || permissions.canManageStaffFor('COLUMBUS') ? [{ id: 'users', label: 'Manage Staff' }] : []),
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              style={{
                padding: '0.45rem 0.85rem',
                borderRadius: '8px',
                fontSize: '0.83rem',
                fontWeight: activeTab === tab.id ? 600 : 400,
                background: activeTab === tab.id ? 'var(--accent-primary)' : 'transparent',
                color: activeTab === tab.id ? '#ffffff' : 'var(--text-muted)',
              }}
            >
              {tab.label}
            </button>
          ))}
        </nav>

        {/* Right Controls: Warehouse Scope, Profile Badge & Security Auth Actions */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
          
          {/* Warehouse Selector */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
            <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Warehouse:</label>
            <select
              value={selectedWarehouse}
              onChange={(e) => setSelectedWarehouse(e.target.value)}
              style={{ padding: '0.35rem 0.65rem', fontSize: '0.8rem' }}
              disabled={!permissions.canViewOtherFacility && currentUser?.facility_scope !== null}
            >
              {permissions.canViewOtherFacility && <option value="ALL">All Warehouses</option>}
              {(permissions.canViewOtherFacility || currentUser?.facility_scope === 'RENO') && <option value="RENO">Reno, NV</option>}
              {(permissions.canViewOtherFacility || currentUser?.facility_scope === 'COLUMBUS') && <option value="COLUMBUS">Columbus, OH</option>}
            </select>
          </div>

          {/* Authenticated User Profile Pill (Fixed Role, No Dropdown Bypass) */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.55rem', background: roleStyle.bg, padding: '0.35rem 0.8rem', borderRadius: '10px', border: `1px solid ${roleStyle.border}` }}>
            <UserCheck size={16} color={roleStyle.text} />
            <div style={{ display: 'flex', flexDirection: 'column' }}>
              <div style={{ fontSize: '0.78rem', color: '#ffffff', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                {currentUser?.full_name || 'Authenticated User'}
                <span className="badge" style={{ fontSize: '0.65rem', background: 'rgba(0,0,0,0.3)', color: roleStyle.text, border: `1px solid ${roleStyle.text}40`, padding: '0.1rem 0.4rem' }}>
                  {roleStyle.label}
                </span>
              </div>
              {currentUser?.email && (
                <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '0.2rem' }}>
                  <Mail size={10} /> {currentUser.email}
                </div>
              )}
            </div>
          </div>

          {/* Security Action Buttons */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <button
              onClick={onNavigateToLanding}
              title="Return to Landing Page"
              className="btn-secondary"
              style={{ padding: '0.4rem 0.65rem', fontSize: '0.8rem', display: 'flex', alignItems: 'center', gap: '0.3rem' }}
            >
              <Home size={14} /> Landing
            </button>
            <button
              onClick={onNavigateToLogin}
              title="Switch Account / Login with different credentials"
              className="btn-secondary"
              style={{ padding: '0.4rem 0.65rem', fontSize: '0.8rem', display: 'flex', alignItems: 'center', gap: '0.3rem' }}
            >
              <RefreshCw size={14} /> Switch User
            </button>
            <button
              onClick={onLogout}
              title="Log out securely"
              className="btn-danger"
              style={{ padding: '0.4rem 0.65rem', fontSize: '0.8rem', display: 'flex', alignItems: 'center', gap: '0.3rem' }}
            >
              <LogOut size={14} /> Logout
            </button>
          </div>

        </div>

      </div>
    </header>
  );
};
