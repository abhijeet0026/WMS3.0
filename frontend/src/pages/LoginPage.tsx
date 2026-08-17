import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { API_BASE } from '../api/client';
import { useAuth } from '../hooks/useAuth';
import { User } from '../types/wms';
import '../styles/tokens.css';
import '../styles/app.css'; // Use app styles for the basic form inputs

export const LoginPage: React.FC = () => {
  const [identifier, setIdentifier] = useState<string>('');
  const [password, setPassword] = useState<string>('');
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg(null);
    setIsLoading(true);

    if (!identifier.trim() || !password.trim()) {
      setErrorMsg('Please enter your Email ID or Username and Password.');
      setIsLoading(false);
      return;
    }

    try {
      // Attempt backend login endpoint call
      const response = await fetch(`${API_BASE}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: identifier.trim(),
          password: password.trim(),
        }),
      });

      if (response.ok) {
        const userData: User = await response.json();
        login(userData);
        navigate('/app/dashboard');
      } else {
        setErrorMsg('Authentication failed: Invalid Email ID / Username or Password.');
      }
    } catch (err) {
      console.warn('Backend server offline or endpoint error:', err);
      setErrorMsg('Cannot connect to authentication server. Please try again later.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', backgroundColor: '#f3f4f6' }}>
      <div style={{ width: '100%', maxWidth: '400px', backgroundColor: '#ffffff', padding: '2.5rem', borderRadius: '8px', boxShadow: '0 4px 6px rgba(0, 0, 0, 0.05)', border: '1px solid #e5e7eb' }}>
        
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 800, color: '#1C1C1A', margin: '0 0 0.5rem 0' }}>WHITFIELD WMS</h1>
          <p style={{ color: '#6b7280', fontSize: '0.9rem', margin: 0 }}>Sign in to continue to your workspace.</p>
        </div>

        {errorMsg && (
          <div data-testid="login-error" style={{ backgroundColor: '#fee2e2', color: '#b91c1c', padding: '0.75rem', borderRadius: '4px', fontSize: '0.85rem', marginBottom: '1.5rem' }}>
            {errorMsg}
          </div>
        )}

        <form onSubmit={handleLogin} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div>
            <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#374151', marginBottom: '0.25rem' }}>
              Username or Email
            </label>
            <input
              data-testid="login-email"
              type="text"
              value={identifier}
              onChange={(e) => setIdentifier(e.target.value)}
              className="app-input"
              placeholder="e.g. dan.whitfield@..."
              required
            />
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#374151', marginBottom: '0.25rem' }}>
              Password
            </label>
            <input
              data-testid="login-password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="app-input"
              placeholder="••••••••"
              required
            />
          </div>

          <button
            data-testid="login-submit"
            type="submit"
            className="btn-primary"
            disabled={isLoading}
            style={{ marginTop: '0.5rem', padding: '0.75rem', width: '100%' }}
          >
            {isLoading ? 'Authenticating...' : 'Sign In'}
          </button>
        </form>

      </div>
    </div>
  );
};
