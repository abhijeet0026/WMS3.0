import React, { useEffect, useState } from 'react';
import { fetchAuditLogs } from '../api/client';
import { AuditLog } from '../types/wms';
import { History, Search, ShieldCheck, User as UserIcon, Clock, Tag } from 'lucide-react';
import { useAuth } from '../hooks/useAuth';

export const AuditLogPage: React.FC = () => {
  const { currentUser, permissions } = useAuth();
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [accessDenied, setAccessDenied] = useState(false);
  const [expandedLogId, setExpandedLogId] = useState<string | null>(null);

  // Facility filter
  const [warehouseId, setWarehouseId] = useState(currentUser?.facility_scope || 'ALL');

  useEffect(() => {
    loadAuditHistory();
  }, [warehouseId, searchQuery]);

  const loadAuditHistory = async () => {
    // RBAC check: Only OWNER and MANAGER can view full audit log
    if (!permissions.canViewAuditLog) {
      setAccessDenied(true);
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      const data = await fetchAuditLogs(warehouseId === 'ALL' ? undefined : warehouseId, searchQuery);
      setLogs(data);
    } catch (err: any) {
      console.error('Audit Log Error:', err);
    } finally {
      setLoading(false);
    }
  };

  if (accessDenied) {
    return (
      <div style={{ padding: '3rem', textAlign: 'center' }}>
        <ShieldCheck size={48} color="#9ca3af" style={{ margin: '0 auto 1rem auto' }} />
        <h2 style={{ fontSize: '1.25rem', color: '#1f2937' }}>Access Restricted</h2>
        <p style={{ color: '#6b7280', maxWidth: '400px', margin: '0 auto' }}>
          Your current role does not have authorization to view the master audit trail.
        </p>
      </div>
    );
  }

  return (
    <div>
      <div className="app-page-header">
        <h1 className="app-page-title">
          <History size={22} color="var(--color-orange-primary)" />
          Audit <span className="app-page-title-accent">Trail</span>
        </h1>
        <p className="app-page-subtitle">
          Immutable log of all system writes, drops, and overrides. Every row is stamped with who, when, and what.
        </p>
      </div>

      <div className="app-panel" style={{ padding: '1rem 1.5rem', display: 'flex', gap: '1.5rem', alignItems: 'center', background: '#f8fafc' }}>
        <div style={{ flex: 1, position: 'relative' }}>
          <Search size={16} color="#9ca3af" style={{ position: 'absolute', left: '0.75rem', top: '50%', transform: 'translateY(-50%)' }} />
          <input
            type="text"
            placeholder="Search logs by action, user, or entity ID..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="app-input"
            style={{ width: '100%', paddingLeft: '2rem', marginTop: 0 }}
          />
        </div>

        {permissions.canViewOtherFacility && (
          <select
            data-testid="facility-filter"
            value={warehouseId}
            onChange={(e) => setWarehouseId(e.target.value)}
            className="app-input"
            style={{ width: '200px', marginTop: 0 }}
          >
            <option value="ALL">All Facilities</option>
            <option value="RENO">Reno, NV</option>
            <option value="COLUMBUS">Columbus, OH</option>
          </select>
        )}
      </div>

      <div className="app-panel">
        {loading ? (
          <p style={{ color: '#6b7280', textAlign: 'center', padding: '2rem' }}>Fetching secure logs...</p>
        ) : logs.length === 0 ? (
          <p style={{ color: '#9ca3af', textAlign: 'center', padding: '3rem' }}>No audit records found matching criteria.</p>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            {logs.map((log) => (
              <div data-testid="audit-log-row" key={log.id} style={{ border: '1px solid #e5e7eb', borderRadius: '4px', overflow: 'hidden' }}>
                {/* Log Header Row */}
                <div 
                  style={{ padding: '1rem', background: expandedLogId === log.id ? '#f3f4f6' : '#ffffff', display: 'flex', alignItems: 'center', justifyContent: 'space-between', cursor: 'pointer', transition: 'background 0.2s' }}
                  onClick={() => setExpandedLogId(expandedLogId === log.id ? null : log.id)}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '2rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: '#4b5563', width: '150px' }}>
                      <Clock size={14} /> <span className="mono-text" style={{ fontSize: '0.8rem' }}>{new Date(log.timestamp).toLocaleString()}</span>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: '#1f2937', width: '160px', fontWeight: 600 }}>
                      <UserIcon size={14} color="#9ca3af" /> {log.user_name}
                    </div>
                    <div>
                      <span className="badge badge-neutral" style={{ marginRight: '0.75rem' }}>{log.action}</span>
                      <span className="mono-text" style={{ fontSize: '0.85rem' }}>{log.entity_type} <span style={{ color: '#9ca3af' }}>{log.entity_id}</span></span>
                    </div>
                  </div>
                  <div style={{ fontSize: '0.8rem', color: 'var(--color-orange-primary)', fontWeight: 600 }}>
                    {expandedLogId === log.id ? 'Close Diff' : 'Inspect Diff'}
                  </div>
                </div>

                {/* Expanded Diff Details */}
                {expandedLogId === log.id && (
                  <div style={{ padding: '1.25rem', borderTop: '1px solid #e5e7eb', background: '#f8fafc', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
                    <div>
                      <h5 style={{ margin: '0 0 0.5rem 0', fontSize: '0.85rem', color: '#6b7280', textTransform: 'uppercase' }}>Old State</h5>
                      <pre className="mono-text" style={{ margin: 0, padding: '1rem', background: '#ffffff', border: '1px solid #e5e7eb', borderRadius: '4px', whiteSpace: 'pre-wrap', color: '#ef4444' }}>
                        {log.old_value ? JSON.stringify(log.old_value, null, 2) : 'null'}
                      </pre>
                    </div>
                    <div>
                      <h5 style={{ margin: '0 0 0.5rem 0', fontSize: '0.85rem', color: '#6b7280', textTransform: 'uppercase' }}>New State</h5>
                      <pre className="mono-text" style={{ margin: 0, padding: '1rem', background: '#ffffff', border: '1px solid #e5e7eb', borderRadius: '4px', whiteSpace: 'pre-wrap', color: '#10b981' }}>
                        {log.new_value ? JSON.stringify(log.new_value, null, 2) : 'null'}
                      </pre>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

    </div>
  );
};
