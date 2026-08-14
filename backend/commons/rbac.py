"""
RBAC (Role-Based Access Control) utility for FastAPI endpoints.
"""
from typing import List, Dict, Any, Callable
from fastapi import HTTPException, status, Depends
from core.apis.routes.auth_routes import get_current_user_claims

def require_role(allowed_roles: List[str]) -> Callable:
    """
    Dependency generator that checks if the current user has one of the allowed roles.
    """
    def role_checker(user_claims: Dict[str, Any] = Depends(get_current_user_claims)) -> Dict[str, Any]:
        user_role = user_claims.get("role")
        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access forbidden: requires one of {allowed_roles}"
            )
        return user_claims
    return role_checker

def require_facility_access(target_facility: str, user_claims: Dict[str, Any]) -> None:
    """
    Raises HTTP 403 if the user does not have access to the target facility.
    OWNER has global access.
    """
    user_role = user_claims.get("role")
    facility_scope = user_claims.get("facility_scope")

    if user_role == "OWNER":
        return
    
    if not facility_scope or facility_scope != target_facility:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access forbidden: user scoped to {facility_scope}, requested {target_facility}"
        )
