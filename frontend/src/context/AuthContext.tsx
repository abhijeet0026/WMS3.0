import React, { createContext, useState, ReactNode, useEffect } from 'react';
import { User } from '../types/wms';
import { usePermissions as createUsePermissions } from '../hooks/usePermissions';

interface AuthContextType {
  currentUser: User | null;
  login: (user: User) => void;
  logout: () => void;
  permissions: ReturnType<typeof createUsePermissions>;
}

export const AuthContext = createContext<AuthContextType | null>(null);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [currentUser, setCurrentUser] = useState<User | null>(() => {
    const saved = localStorage.getItem('wms_user');
    return saved ? JSON.parse(saved) : null;
  });

  const permissions = createUsePermissions(currentUser);

  const login = (user: User) => {
    setCurrentUser(user);
    localStorage.setItem('wms_user', JSON.stringify(user));
  };

  const logout = () => {
    setCurrentUser(null);
    localStorage.removeItem('wms_user');
  };

  return (
    <AuthContext.Provider value={{ currentUser, login, logout, permissions }}>
      {children}
    </AuthContext.Provider>
  );
};
