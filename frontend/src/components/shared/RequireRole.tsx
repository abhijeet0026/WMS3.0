import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';

export const RequireRole: React.FC<{ children: React.ReactNode, requireLogin?: boolean, allowedRoles?: string[] }> = ({ children, requireLogin = true, allowedRoles }) => {
  const { currentUser } = useAuth();
  const location = useLocation();

  if (requireLogin && !currentUser) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (allowedRoles && currentUser && !allowedRoles.includes(currentUser.role)) {
    return <Navigate to="/app/dashboard" replace />;
  }

  // If there are specific roles allowed for a route, it would be passed as a prop,
  // but the prompt specifies "a disallowed role gets redirected to /dashboard".
  // Since we don't have route-level exact role arrays in this component, we can handle it at the page level 
  // or pass an allowedRoles[] prop. For now, we just enforce login.

  return <>{children}</>;
};
