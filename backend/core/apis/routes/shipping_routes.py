"""
FastAPI route module for atomic order creation and concurrency-safe shipping execution.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, status, Depends, Query

from commons.logger import logger
from core.apis.routes.auth_routes import get_current_user_claims
from core.apis.schemas.requests.wms_schemas import CreateOrderRequest, ShipOrderRequest
from core.apis.schemas.responses.wms_schemas import OrderResponse
from core.controllers.wms_controllers import WMSController

shipping_router = APIRouter()
logging = logger(__name__)


@shipping_router.post(
    "/v1/shipping/orders",
    status_code=status.HTTP_201_CREATED,
    response_model=OrderResponse,
)
async def create_order(
    request: CreateOrderRequest,
    user_claims: Dict[str, Any] = Depends(get_current_user_claims),
):
    """
    Create a new pending order ready for pick, pack, and ship.

    Args:
        request (CreateOrderRequest): Order creation details.
        user_claims (Dict[str, Any]): Authenticated user claims.

    Returns:
        OrderResponse: Created pending order.
    """
    try:
        logging.info("Calling POST /v1/shipping/orders endpoint")
        result = WMSController().create_order(user_info=user_claims, request_data=request.model_dump())
        return OrderResponse(**result)
    except HTTPException as httperr:
        raise httperr
    except Exception as error:
        logging.error(f"Error in POST /v1/shipping/orders endpoint: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error creating order",
        )


@shipping_router.post(
    "/v1/shipping/ship",
    status_code=status.HTTP_200_OK,
    response_model=OrderResponse,
)
async def ship_order(
    request: ShipOrderRequest,
    user_claims: Dict[str, Any] = Depends(get_current_user_claims),
):
    """
    Atomically pick, pack, weigh, and ship an order.

    Concurrently verifies stock availability and decrements stock in 1 single transaction.
    Raises 409 Conflict if stock is insufficient.

    Args:
        request (ShipOrderRequest): Order shipping details.
        user_claims (Dict[str, Any]): Authenticated user claims.

    Returns:
        OrderResponse: Updated order marked SHIPPED.
    """
    try:
        logging.info("Calling POST /v1/shipping/ship endpoint")
        result = WMSController().ship_order(user_info=user_claims, request_data=request.model_dump())
        return OrderResponse(**result)
    except HTTPException as httperr:
        raise httperr
    except Exception as error:
        logging.error(f"Error in POST /v1/shipping/ship endpoint: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during order shipping",
        )


@shipping_router.get(
    "/v1/shipping/orders",
    status_code=status.HTTP_200_OK,
    response_model=List[OrderResponse],
)
async def get_orders(
    warehouse_id: Optional[str] = Query(None, description="Warehouse filter"),
    user_claims: Dict[str, Any] = Depends(get_current_user_claims),
):
    """
    List orders in queue.

    Args:
        warehouse_id (Optional[str]): Warehouse filter query parameter.
        user_claims (Dict[str, Any]): Authenticated user claims.

    Returns:
        List[OrderResponse]: Order queue list.
    """
    try:
        logging.info("Calling GET /v1/shipping/orders endpoint")
        result = WMSController().get_orders(user_info=user_claims, warehouse_id=warehouse_id)
        return [OrderResponse(**o) for o in result]
    except Exception as error:
        logging.error(f"Error in GET /v1/shipping/orders endpoint: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error fetching orders",
        )
