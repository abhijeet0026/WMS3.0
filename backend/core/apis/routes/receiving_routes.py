"""
FastAPI route module for atomic and idempotent shipment receiving operations.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, status, Depends, Query

from commons.logger import logger
from core.apis.routes.auth_routes import get_current_user_claims
from core.apis.schemas.requests.wms_schemas import ReceiveShipmentRequest
from core.apis.schemas.responses.wms_schemas import ShipmentResponse
from core.controllers.wms_controllers import WMSController

receiving_router = APIRouter()
logging = logger(__name__)


@receiving_router.post(
    "/v1/receiving/shipments",
    status_code=status.HTTP_201_CREATED,
    response_model=ShipmentResponse,
)
async def receive_shipment(
    request: ReceiveShipmentRequest,
    user_claims: Dict[str, Any] = Depends(get_current_user_claims),
):
    """
    Atomically process incoming seller shipment receiving.

    Idempotent: If tracking number has already been received, returns existing shipment record.

    Args:
        request (ReceiveShipmentRequest): Shipment payload.
        user_claims (Dict[str, Any]): Authenticated user claims.

    Returns:
        ShipmentResponse: Created or existing shipment record.
    """
    try:
        logging.info("Calling POST /v1/receiving/shipments endpoint")
        result, is_dup = WMSController().receive_shipment(
            user_info=user_claims,
            request_data=request.model_dump(),
        )
        from fastapi import Response
        response_model = ShipmentResponse(**result)
        if is_dup:
            return Response(content=response_model.model_dump_json(), status_code=status.HTTP_200_OK, media_type="application/json")
        return response_model
    except HTTPException as httperr:
        raise httperr
    except Exception as error:
        logging.error(f"Error in POST /v1/receiving/shipments endpoint: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during receiving",
        )


@receiving_router.get(
    "/v1/receiving/shipments",
    status_code=status.HTTP_200_OK,
    response_model=List[ShipmentResponse],
)
async def get_shipments(
    warehouse_id: Optional[str] = Query(None, description="Warehouse filter"),
    user_claims: Dict[str, Any] = Depends(get_current_user_claims),
):
    """
    List inbound shipments.

    Args:
        warehouse_id (Optional[str]): Warehouse filter query parameter.
        user_claims (Dict[str, Any]): Authenticated user claims.

    Returns:
        List[ShipmentResponse]: List of shipments.
    """
    try:
        logging.info("Calling GET /v1/receiving/shipments endpoint")
        result = WMSController().get_shipments(user_info=user_claims, warehouse_id=warehouse_id)
        return [ShipmentResponse(**s) for s in result]
    except Exception as error:
        logging.error(f"Error in GET /v1/receiving/shipments endpoint: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error fetching shipments",
        )
