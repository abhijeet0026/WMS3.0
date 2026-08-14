import { UserRole, User } from '../types/wms';

export const usePermissions = (currentUser: User | null) => {
  const role = currentUser?.role || 'NEW_HIRE';
  const facilityScope = currentUser?.facility_scope;

  return {
    canViewOtherFacility: role === 'OWNER',
    canViewCostData: role === 'OWNER' || role === 'MANAGER',
    canManageStaffFor: (targetFacility: string) => {
      if (role === 'OWNER') return true;
      if (role === 'MANAGER' && facilityScope === targetFacility) return true;
      return false;
    },
    canViewAuditLog: role === 'OWNER' || role === 'MANAGER',
    canExecuteMigration: role === 'OWNER',
    canShipAndReceive: true, // Guided for NEW_HIRE, but generally true
  };
};
