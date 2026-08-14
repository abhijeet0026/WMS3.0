"""
FastAPI route module for system audit trail search and reporting.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, status, Depends, Query

from commons.logger import logger
from core.apis.routes.auth_routes import get_current_user_claims
from core.apis.schemas.responses.wms_schemas import AuditLogResponse
from core.controllers.wms_controllers import WMSController

audit_router = APIRouter()
logging = logger(__name__)


@audit_router.get(
    "/v1/audit/logs",
    status_code=status.HTTP_200_OK,
    response_model=List[AuditLogResponse],
)
async def get_audit_logs(
    warehouse_id: Optional[str] = Query(None, description="Filter by warehouse ID"),
    search: Optional[str] = Query(None, description="Search keyword across user, action, entity"),
    user_claims: Dict[str, Any] = Depends(get_current_user_claims),
):
    """
    Search and view system audit trail log history.

    Restricted to MANAGER and OWNER roles.

    Args:
        warehouse_id (Optional[str]): Warehouse filter.
        search (Optional[str]): Keyword search filter.
        user_claims (Dict[str, Any]): Authenticated user claims.

    Returns:
        List[AuditLogResponse]: Audit log entries.
    """
    try:
        logging.info("Calling GET /v1/audit/logs endpoint")
        result = WMSController().get_audit_logs(
            user_info=user_claims,
            warehouse_id=warehouse_id,
            search_query=search,
        )
        return [AuditLogResponse(**log) for log in result]
    except HTTPException as httperr:
        raise httperr
    except Exception as error:
        logging.error(f"Error in GET /v1/audit/logs endpoint: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error fetching audit logs",
        )
