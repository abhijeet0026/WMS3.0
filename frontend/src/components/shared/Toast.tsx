import React from 'react';
import { ShieldAlert, CheckCircle, AlertCircle, AlertTriangle } from 'lucide-react';

export type ToastType = 'success' | 'duplicate' | 'error' | 'warning';

interface ToastProps {
  type: ToastType;
  title: string;
  message: string;
  onDismiss?: () => void;
}

export const Toast: React.FC<ToastProps> = ({ type, title, message, onDismiss }) => {
  const getStyles = () => {
    switch (type) {
      case 'duplicate':
        return { bg: '#fef3c7', border: '#f59e0b', color: '#b45309', icon: <ShieldAlert size={24} color="#f59e0b" /> };
      case 'success':
        return { bg: '#d1fae5', border: '#10b981', color: '#047857', icon: <CheckCircle size={24} color="#10b981" /> };
      case 'warning':
        return { bg: '#fee2e2', border: '#ef4444', color: '#b91c1c', icon: <AlertTriangle size={24} color="#ef4444" /> };
      case 'error':
      default:
        return { bg: '#fee2e2', border: '#ef4444', color: '#b91c1c', icon: <AlertCircle size={24} color="#ef4444" /> };
    }
  };

  const styles = getStyles();

  return (
    <div style={{
      backgroundColor: styles.bg,
      border: `1px solid ${styles.border}`,
      padding: '1rem',
      borderRadius: 'var(--radius-base)',
      display: 'flex',
      alignItems: 'flex-start',
      gap: '1rem',
      marginBottom: '1.5rem',
      position: 'relative'
    }}>
      <div style={{ flexShrink: 0, marginTop: '2px' }}>
        {styles.icon}
      </div>
      <div style={{ flex: 1 }}>
        <h4 style={{ margin: '0 0 0.25rem 0', color: styles.color, fontSize: '0.95rem', fontWeight: 600 }}>{title}</h4>
        <p style={{ margin: 0, color: styles.color, fontSize: '0.85rem' }}>{message}</p>
      </div>
      {onDismiss && (
        <button onClick={onDismiss} style={{ background: 'transparent', border: 'none', cursor: 'pointer', color: styles.color, padding: '0.2rem' }}>
          &times;
        </button>
      )}
    </div>
  );
};
