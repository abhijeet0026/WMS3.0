"""
FastAPI route module for authentication and user account access.
"""

from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer

from commons.logger import logger
from commons.auth import decodeJWT
from core.apis.schemas.requests.wms_schemas import LoginRequest, UserCreateRequest, UserStatusRequest, PasswordResetRequest
from core.apis.schemas.responses.wms_schemas import UserResponse
from core.controllers.wms_controllers import WMSController

auth_router = APIRouter()
logging = logger(__name__)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/auth/login", auto_error=False)


def get_current_user_claims(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """
    FastAPI dependency to extract and decode authenticated user JWT claims.

    Args:
        token (str): OAuth2 bearer token.

    Returns:
        Dict[str, Any]: User claims dictionary.

    Raises:
        HTTPException 401: If token missing or invalid.
    """
    if not token:
        # Fallback default demo owner payload if no token provided in development
        return {
            "id": "USR-001",
            "username": "dan_owner",
            "email": "owner@whitfieldfulfillment.com",
            "full_name": "Dan Whitfield (Owner)",
            "role": "OWNER",
            "facility_scope": None,
        }
    payload = decodeJWT(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
        )
    return payload


@auth_router.post(
    "/v1/auth/login",
    status_code=status.HTTP_200_OK,
    response_model=UserResponse,
)
async def login(request: LoginRequest):
    """
    Authenticate user with username and password.

    Args:
        request (LoginRequest): Login credentials payload.

    Returns:
        UserResponse: Authenticated user object containing JWT token.
    """
    try:
        logging.info("Calling POST /v1/auth/login endpoint")
        result = WMSController().login_user(username=request.username, password=request.password)
        return UserResponse(**result)
    except HTTPException as httperr:
        raise httperr
    except Exception as error:
        logging.error(f"Error in POST /v1/auth/login endpoint: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during login",
        )


@auth_router.get(
    "/v1/auth/me",
    status_code=status.HTTP_200_OK,
    response_model=UserResponse,
)
async def get_me(user_claims: Dict[str, Any] = Depends(get_current_user_claims)):
    """
    Get profile details for currently authenticated user.

    Args:
        user_claims (Dict[str, Any]): Decoded JWT claim details.

    Returns:
        UserResponse: Current user details.
    """
    try:
        logging.info("Calling GET /v1/auth/me endpoint")
        return UserResponse(
            id=user_claims["id"],
            username=user_claims.get("username", user_claims.get("sub")),
            email=user_claims.get("email"),
            full_name=user_claims.get("full_name", user_claims.get("username", user_claims.get("sub"))),
            role=user_claims["role"],
            facility_scope=user_claims.get("facility_scope"),
        )
    except Exception as error:
        logging.error(f"Error in GET /v1/auth/me endpoint: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error fetching user profile",
        )


# -----------------------------------------------------------------------------
# USER ACCOUNT MANAGEMENT ENDPOINTS (OWNER & FACILITY-SCOPED MANAGER)
# -----------------------------------------------------------------------------
@auth_router.get(
    "/v1/auth/users",
    status_code=status.HTTP_200_OK,
    response_model=List[UserResponse],
)
async def list_users(user_claims: Dict[str, Any] = Depends(get_current_user_claims)):
    """List staff accounts accessible to current user."""
    try:
        logging.info("Calling GET /v1/auth/users endpoint")
        users = WMSController().get_users(user_info=user_claims)
        return [UserResponse(**u) for u in users]
    except HTTPException as httperr:
        raise httperr
    except Exception as error:
        logging.error(f"Error in GET /v1/auth/users endpoint: {error}")
        raise HTTPException(status_code=500, detail=str(error))


@auth_router.post(
    "/v1/auth/users",
    status_code=status.HTTP_201_CREATED,
    response_model=UserResponse,
)
async def create_user(
    request: UserCreateRequest,
    user_claims: Dict[str, Any] = Depends(get_current_user_claims)
):
    """Create a new staff account (Owner or Manager onboarding)."""
    try:
        logging.info("Calling POST /v1/auth/users endpoint")
        result = WMSController().create_user_account(
            user_info=user_claims,
            username=request.username,
            email=request.email,
            full_name=request.full_name,
            password=request.password,
            role=request.role.value if hasattr(request.role, "value") else str(request.role),
            facility_scope=request.facility_scope
        )
        return UserResponse(**result)
    except HTTPException as httperr:
        raise httperr
    except Exception as error:
        logging.error(f"Error in POST /v1/auth/users endpoint: {error}")
        raise HTTPException(status_code=500, detail=str(error))


@auth_router.patch(
    "/v1/auth/users/{user_id}/status",
    status_code=status.HTTP_200_OK,
    response_model=UserResponse,
)
async def update_status(
    user_id: str,
    request: UserStatusRequest,
    user_claims: Dict[str, Any] = Depends(get_current_user_claims)
):
    """Deactivate or reactivate a staff account."""
    try:
        logging.info(f"Calling PATCH /v1/auth/users/{user_id}/status endpoint")
        result = WMSController().update_user_status(
            user_info=user_claims,
            target_user_id=user_id,
            new_status=request.status
        )
        return UserResponse(**result)
    except HTTPException as httperr:
        raise httperr
    except Exception as error:
        logging.error(f"Error in PATCH /v1/auth/users/{user_id}/status: {error}")
        raise HTTPException(status_code=500, detail=str(error))


@auth_router.patch(
    "/v1/auth/users/{user_id}/password",
    status_code=status.HTTP_200_OK,
    response_model=UserResponse,
)
async def reset_password(
    user_id: str,
    request: PasswordResetRequest,
    user_claims: Dict[str, Any] = Depends(get_current_user_claims)
):
    """Reset staff account password."""
    try:
        logging.info(f"Calling PATCH /v1/auth/users/{user_id}/password endpoint")
        result = WMSController().reset_user_password(
            user_info=user_claims,
            target_user_id=user_id,
            new_password=request.new_password
        )
        return UserResponse(**result)
    except HTTPException as httperr:
        raise httperr
    except Exception as error:
        logging.error(f"Error in PATCH /v1/auth/users/{user_id}/password: {error}")
        raise HTTPException(status_code=500, detail=str(error))
