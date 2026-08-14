import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { MarketingLayout } from './layouts/MarketingLayout';
import { AppLayout } from './layouts/AppLayout';
import { RequireRole } from './components/shared/RequireRole';

// Stubbed pages for now
import { HomePage } from './pages/marketing/HomePage';
import { LoginPage } from './pages/LoginPage';
import { DashboardPage } from './pages/DashboardPage';
import { ReceiveShipmentPage } from './pages/ReceiveShipmentPage';
import { ShipOrderPage } from './pages/ShipOrderPage';
import { AccountManagementPage } from './pages/AccountManagementPage';
import { AuditLogPage } from './pages/AuditLogPage';
import { ReconciliationPage } from './pages/ReconciliationPage';

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Marketing Surface */}
          <Route element={<MarketingLayout />}>
            <Route path="/" element={<HomePage />} />
          </Route>

          {/* Minimal Surface (Login) */}
          <Route path="/login" element={<LoginPage />} />

          {/* Internal App Surface */}
          <Route path="/app" element={<RequireRole><AppLayout /></RequireRole>}>
            <Route index element={<Navigate to="/app/dashboard" replace />} />
            <Route path="dashboard" element={<DashboardPage />} />
            
            <Route path="receive" element={
              <RequireRole allowedRoles={['OWNER', 'MANAGER', 'TRUSTED_STAFF', 'NEW_HIRE']}>
                <ReceiveShipmentPage />
              </RequireRole>
            } />
            
            <Route path="ship" element={
              <RequireRole allowedRoles={['OWNER', 'MANAGER', 'TRUSTED_STAFF', 'NEW_HIRE']}>
                <ShipOrderPage />
              </RequireRole>
            } />
            
            <Route path="accounts" element={
              <RequireRole allowedRoles={['OWNER', 'MANAGER']}>
                <AccountManagementPage />
              </RequireRole>
            } />
            
            <Route path="audit-log" element={
              <RequireRole allowedRoles={['OWNER', 'MANAGER']}>
                <AuditLogPage />
              </RequireRole>
            } />
            
            <Route path="reconciliation" element={
              <RequireRole allowedRoles={['OWNER']}>
                <ReconciliationPage />
              </RequireRole>
            } />
          </Route>

          {/* Catch-all */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
