"""
FastAPI route module for pre-cutover Excel spreadsheet data reconciliation.
"""

from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, status, Depends

from commons.logger import logger
from core.apis.routes.auth_routes import get_current_user_claims
from core.apis.schemas.requests.wms_schemas import ReconcileIssueRequest
from core.apis.schemas.responses.wms_schemas import LegacyIssueResponse
from core.controllers.wms_controllers import WMSController

migration_router = APIRouter()
logging = logger(__name__)


@migration_router.get(
    "/v1/migration/issues",
    status_code=status.HTTP_200_OK,
    response_model=List[LegacyIssueResponse],
)
async def get_legacy_issues(user_claims: Dict[str, Any] = Depends(get_current_user_claims)):
    """
    List known legacy Excel anomalies (e.g., phantom doubled stock, oversold stock).

    Args:
        user_claims (Dict[str, Any]): Authenticated user claims.

    Returns:
        List[LegacyIssueResponse]: Legacy issues list.
    """
    try:
        logging.info("Calling GET /v1/migration/issues endpoint")
        result = WMSController().get_legacy_issues(user_info=user_claims)
        return [LegacyIssueResponse(**issue) for issue in result]
    except HTTPException as httperr:
        raise httperr
    except Exception as error:
        logging.error(f"Error in GET /v1/migration/issues endpoint: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error fetching legacy spreadsheet issues",
        )


@migration_router.post(
    "/v1/migration/reconcile",
    status_code=status.HTTP_200_OK,
    response_model=LegacyIssueResponse,
)
async def reconcile_issue(
    request: ReconcileIssueRequest,
    user_claims: Dict[str, Any] = Depends(get_current_user_claims),
):
    """
    Reconcile a legacy spreadsheet issue with physical verified quantity.

    Restricted to MANAGER and OWNER roles.

    Args:
        request (ReconcileIssueRequest): Issue reconciliation parameters.
        user_claims (Dict[str, Any]): Authenticated user claims.

    Returns:
        LegacyIssueResponse: Reconciled issue record.
    """
    try:
        logging.info("Calling POST /v1/migration/reconcile endpoint")
        result = WMSController().reconcile_issue(
            user_info=user_claims,
            request_data=request.model_dump(),
        )
        return LegacyIssueResponse(**result)
    except HTTPException as httperr:
        raise httperr
    except Exception as error:
        logging.error(f"Error in POST /v1/migration/reconcile endpoint: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during data reconciliation",
        )
