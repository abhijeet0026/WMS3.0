import React, { useEffect, useState } from 'react';
import { fetchLegacyIssues, reconcileLegacyIssue } from '../api/client';
import { LegacyIssue } from '../types/wms';
import { FileSpreadsheet, ShieldAlert, CheckCircle2, ArrowRight } from 'lucide-react';
import { useAuth } from '../hooks/useAuth';
import { Toast, ToastType } from '../components/shared/Toast';

export const ReconciliationPage: React.FC = () => {
  const { currentUser, permissions } = useAuth();
  const [issues, setIssues] = useState<LegacyIssue[]>([]);
  const [loading, setLoading] = useState(true);
  const [reconcilingId, setReconcilingId] = useState<string | null>(null);
  const [toast, setToast] = useState<{ type: ToastType; title: string; message: string } | null>(null);

  // Reconciliation form states per issue
  const [actualQuantities, setActualQuantities] = useState<Record<string, string>>({});
  const [resolutionNotes, setResolutionNotes] = useState<Record<string, string>>({});

  useEffect(() => {
    if (permissions.canExecuteMigration) {
      loadIssues();
    }
  }, []);

  const loadIssues = async () => {
    try {
      setLoading(true);
      const data = await fetchLegacyIssues();
      setIssues(data);
    } catch (err: any) {
      setToast({ type: 'error', title: 'Load Error', message: err.message });
    } finally {
      setLoading(false);
    }
  };

  const handleReconcile = async (issueId: string) => {
    setToast(null);

    const qtyStr = actualQuantities[issueId];
    if (qtyStr === undefined || qtyStr === '') {
      setToast({ type: 'error', title: 'Input Required', message: 'Please enter the actual physical quantity found.' });
      return;
    }

    try {
      setReconcilingId(issueId);
      await reconcileLegacyIssue(issueId, Number(qtyStr), resolutionNotes[issueId]);
      
      setToast({ type: 'success', title: 'Reconciled', message: 'Legacy issue successfully reconciled and stock updated.' });
      loadIssues();
    } catch (err: any) {
      setToast({ type: 'error', title: 'Reconciliation Failed', message: err.message });
    } finally {
      setReconcilingId(null);
    }
  };

  if (!permissions.canExecuteMigration) {
    return (
      <div style={{ padding: '3rem', textAlign: 'center' }}>
        <ShieldAlert size={48} color="#ef4444" style={{ margin: '0 auto 1rem auto' }} />
        <h2 style={{ fontSize: '1.25rem', color: '#1f2937' }}>Access Denied</h2>
        <p style={{ color: '#6b7280', maxWidth: '400px', margin: '0 auto' }}>
          Legacy Excel data reconciliation is restricted to System Owners only.
        </p>
      </div>
    );
  }

  return (
    <div>
      <div className="app-page-header">
        <h1 className="app-page-title">
          <FileSpreadsheet size={22} color="var(--color-orange-primary)" />
          Legacy Excel <span className="app-page-title-accent">Reconciliation</span>
        </h1>
        <p className="app-page-subtitle">
          Resolve phantom stock discrepancies imported from the old spreadsheets. Owner-only access.
        </p>
      </div>

      {toast && <Toast {...toast} onDismiss={() => setToast(null)} />}

      <div className="app-panel">
        <h3 style={{ fontSize: '1.1rem', margin: '0 0 1rem 0' }}>Outstanding Conflicts ({issues.filter(i => i.status === 'UNRESOLVED').length})</h3>
        
        {loading ? (
          <p style={{ color: '#6b7280', textAlign: 'center', padding: '2rem' }}>Scanning for legacy issues...</p>
        ) : issues.filter(i => i.status === 'UNRESOLVED').length === 0 ? (
          <div style={{ textAlign: 'center', padding: '3rem', border: '1px dashed #e5e7eb', borderRadius: '4px' }}>
            <CheckCircle2 size={32} color="#10b981" style={{ margin: '0 auto 1rem auto' }} />
            <h4 style={{ margin: '0 0 0.5rem 0', color: '#1f2937' }}>System Clean</h4>
            <p style={{ margin: 0, color: '#6b7280', fontSize: '0.9rem' }}>All legacy Excel discrepancies have been reconciled.</p>
          </div>
        ) : (
          <div data-testid="reconciliation-table" style={{ display: 'grid', gap: '1.5rem' }}>
            {issues.filter(i => i.status === 'UNRESOLVED').map(issue => (
              <div key={issue.id} style={{ border: '1px solid #f87171', borderRadius: 'var(--radius-base)', overflow: 'hidden' }}>
                <div style={{ background: '#fee2e2', padding: '1rem', borderBottom: '1px solid #fca5a5', display: 'flex', justifyContent: 'space-between' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#b91c1c', fontWeight: 600 }}>
                    <ShieldAlert size={18} /> {issue.issue_type.replace('_', ' ')}
                  </div>
                  <span className="mono-text" style={{ fontSize: '0.85rem' }}>Issue ID: {issue.id}</span>
                </div>
                
                <div style={{ padding: '1.5rem', display: 'flex', gap: '2rem', flexWrap: 'wrap' }}>
                  <div style={{ flex: '1 1 300px' }}>
                    <h5 style={{ margin: '0 0 0.75rem 0', color: '#374151' }}>Discrepancy Details</h5>
                    <p style={{ margin: '0 0 1rem 0', color: '#6b7280', fontSize: '0.95rem' }}>{issue.description}</p>
                    
                    <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', background: '#f3f4f6', padding: '1rem', borderRadius: '4px' }}>
                      <div style={{ flex: 1, textAlign: 'center' }}>
                        <div style={{ fontSize: '0.75rem', textTransform: 'uppercase', color: '#6b7280', fontWeight: 600 }}>Excel Logged</div>
                        <div style={{ fontSize: '1.25rem', fontWeight: 700, color: '#1f2937' }}>{issue.excel_quantity}</div>
                      </div>
                      <ArrowRight color="#9ca3af" />
                      <div style={{ flex: 1, textAlign: 'center' }}>
                        <div style={{ fontSize: '0.75rem', textTransform: 'uppercase', color: '#6b7280', fontWeight: 600 }}>WMS Reality</div>
                        <div style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--color-orange-primary)' }}>?</div>
                      </div>
                    </div>
                  </div>

                  <div style={{ flex: '1 1 300px', background: '#f8fafc', padding: '1.25rem', borderRadius: '4px', border: '1px solid #e5e7eb' }}>
                    <h5 style={{ margin: '0 0 1rem 0', color: '#1f2937' }}>Manager Override</h5>
                    
                    <div style={{ marginBottom: '1rem' }}>
                      <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#374151', marginBottom: '0.25rem' }}>Actual Physical Count</label>
                      <input
                        type="number"
                        className="app-input mono"
                        value={actualQuantities[issue.id] || ''}
                        onChange={(e) => setActualQuantities({ ...actualQuantities, [issue.id]: e.target.value })}
                        placeholder="e.g. 14"
                      />
                    </div>
                    
                    <div style={{ marginBottom: '1rem' }}>
                      <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#374151', marginBottom: '0.25rem' }}>Override Notes</label>
                      <input
                        type="text"
                        className="app-input"
                        value={resolutionNotes[issue.id] || ''}
                        onChange={(e) => setResolutionNotes({ ...resolutionNotes, [issue.id]: e.target.value })}
                        placeholder="e.g. Found in wrong aisle, count verified"
                      />
                    </div>

                    <button
                      onClick={() => handleReconcile(issue.id)}
                      disabled={reconcilingId === issue.id}
                      className="btn-primary"
                      style={{ width: '100%' }}
                    >
                      {reconcilingId === issue.id ? 'Committing...' : 'Commit Reconciliation'}
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
