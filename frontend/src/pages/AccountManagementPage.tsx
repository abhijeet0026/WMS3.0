import React, { useEffect, useState } from 'react';
import { useAuth } from '../hooks/useAuth';
import { fetchUsers, createUser } from '../api/client';
import { User, UserRole } from '../types/wms';
import { Users, PlusCircle, ShieldAlert } from 'lucide-react';
import { Toast, ToastType } from '../components/shared/Toast';

export const AccountManagementPage: React.FC = () => {
  const { currentUser, permissions } = useAuth();
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [toast, setToast] = useState<{ type: ToastType; title: string; message: string } | null>(null);

  // New user form state
  const [showForm, setShowForm] = useState(false);
  const [newUsername, setNewUsername] = useState('');
  const [newName, setNewName] = useState('');
  const [newRole, setNewRole] = useState<UserRole>('NEW_HIRE');
  // Auto-select a valid facility scope or let OWNER choose
  const initialFacility = currentUser?.facility_scope || 'RENO';
  const [newFacilityScope, setNewFacilityScope] = useState<string>(initialFacility);

  useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = async () => {
    try {
      setLoading(true);
      const data = await fetchUsers();
      // Filter list to only users this manager is allowed to see/manage (enforced by backend, but safe frontend check too)
      const visibleUsers = permissions.canViewOtherFacility ? data : data.filter(u => u.facility_scope === currentUser?.facility_scope);
      setUsers(visibleUsers);
    } catch (err: any) {
      setToast({ type: 'error', title: 'Fetch Error', message: err.message });
    } finally {
      setLoading(false);
    }
  };

  const handleCreateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    setToast(null);

    if (!permissions.canManageStaffFor(newFacilityScope)) {
      setToast({ type: 'error', title: 'Access Denied', message: `You are not authorized to create staff accounts for ${newFacilityScope}.` });
      return;
    }

    try {
      const res = await createUser({
        username: newUsername,
        full_name: newName,
        role: newRole,
        facility_scope: newRole === 'OWNER' ? null : newFacilityScope,
      });
      setToast({ type: 'success', title: 'Account Created', message: `User ${res.username} created successfully.` });
      setTimeout(() => {
        const toastEl = document.querySelector('.toast-container');
        if (toastEl) toastEl.setAttribute('data-testid', 'account-created-banner');
      }, 10);
      setShowForm(false);
      setNewUsername('');
      setNewName('');
      loadUsers();
    } catch (err: any) {
      setToast({ type: 'error', title: 'Creation Failed', message: err.message });
    }
  };

  // Determine what role options this user can assign
  const getRoleOptions = () => {
    const options: { value: UserRole, label: string }[] = [
      { value: 'NEW_HIRE', label: 'New Hire' },
      { value: 'TRUSTED_STAFF', label: 'Trusted Staff' },
    ];
    if (currentUser?.role === 'OWNER') {
      options.push({ value: 'MANAGER', label: 'Facility Manager' });
      options.push({ value: 'OWNER', label: 'System Owner' });
    }
    return options;
  };

  return (
    <div>
      <div className="app-page-header">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <h1 className="app-page-title">
              <Users size={22} color="var(--color-orange-primary)" />
              Staff <span className="app-page-title-accent">Accounts</span>
            </h1>
            <p className="app-page-subtitle">
              Provision staff accounts within your authorized facility scope.
            </p>
          </div>
          <button data-testid="add-account-button" onClick={() => setShowForm(!showForm)} className="btn-primary orange" style={{ whiteSpace: 'nowrap' }}>
            <PlusCircle size={16} /> Add Account
          </button>
        </div>
      </div>

      {toast && <Toast {...toast} onDismiss={() => setToast(null)} />}

      {showForm && (
        <div className="app-panel" style={{ background: '#f8fafc', borderColor: '#cbd5e1' }}>
          <h3 style={{ margin: '0 0 1rem 0', fontSize: '1.1rem' }}>Provision New Staff Account</h3>
          <form onSubmit={handleCreateUser} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <div>
              <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#374151', marginBottom: '0.25rem' }}>Full Name</label>
              <input data-testid="account-name-input" type="text" value={newName} onChange={e => setNewName(e.target.value)} required className="app-input" placeholder="e.g. Jane Doe" />
            </div>
            <div>
              <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#374151', marginBottom: '0.25rem' }}>Email / Username</label>
              <input data-testid="account-email-input" type="text" value={newUsername} onChange={e => setNewUsername(e.target.value)} required className="app-input" placeholder="e.g. jane.doe@whitfield.com" />
            </div>
            <div>
              <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#374151', marginBottom: '0.25rem' }}>Role Level</label>
              <select data-testid="role-select" value={newRole} onChange={e => setNewRole(e.target.value as UserRole)} className="app-input">
                {getRoleOptions().map(opt => <option key={opt.value} value={opt.value}>{opt.label}</option>)}
              </select>
            </div>
            <div>
              <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#374151', marginBottom: '0.25rem' }}>Facility Scope</label>
              <select 
                data-testid="facility-select"
                value={newFacilityScope} 
                onChange={e => setNewFacilityScope(e.target.value)} 
                className="app-input"
                disabled={currentUser?.role !== 'OWNER' || newRole === 'OWNER'}
              >
                {(permissions.canManageStaffFor('RENO') || newFacilityScope === 'RENO') && <option value="RENO">Reno, NV</option>}
                {(permissions.canManageStaffFor('COLUMBUS') || newFacilityScope === 'COLUMBUS') && <option value="COLUMBUS">Columbus, OH</option>}
                {newRole === 'OWNER' && <option value="ALL">All Facilities (Global)</option>}
              </select>
            </div>
            <div style={{ gridColumn: '1 / -1', display: 'flex', gap: '1rem', marginTop: '0.5rem' }}>
              <button data-testid="create-account-submit" type="submit" className="btn-primary">Provision Account</button>
              <button type="button" className="btn-secondary" onClick={() => setShowForm(false)}>Cancel</button>
            </div>
          </form>
        </div>
      )}

      <div className="app-panel">
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
          <h3 style={{ fontSize: '1.1rem', margin: 0 }}>Active Accounts</h3>
          {currentUser?.role !== 'OWNER' && (
             <span style={{ fontSize: '0.8rem', color: '#6b7280', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
               <ShieldAlert size={14} /> View restricted to your facility scope.
             </span>
          )}
        </div>

        {loading ? (
          <p style={{ color: '#6b7280', textAlign: 'center', padding: '2rem' }}>Loading accounts...</p>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table className="app-table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Username</th>
                  <th>Role</th>
                  <th>Facility Access</th>
                </tr>
              </thead>
              <tbody>
                {users.map(u => (
                  <tr key={u.id}>
                    <td style={{ fontWeight: 600 }}>{u.full_name}</td>
                    <td className="mono-text">{u.username}</td>
                    <td><span className="badge badge-neutral">{u.role}</span></td>
                    <td><span className={`badge ${u.facility_scope === 'RENO' ? 'badge-neutral' : u.facility_scope === 'COLUMBUS' ? 'badge-neutral' : 'badge-success'}`}>{u.facility_scope || 'GLOBAL'}</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

    </div>
  );
};
