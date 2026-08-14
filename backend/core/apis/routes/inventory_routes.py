"""
FastAPI route module for inventory stock monitoring and product catalog.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, status, Depends, Query

from commons.logger import logger
from core.apis.routes.auth_routes import get_current_user_claims
from core.apis.schemas.responses.wms_schemas import InventoryItemResponse, ProductResponse
from core.controllers.wms_controllers import WMSController

inventory_router = APIRouter()
logging = logger(__name__)


@inventory_router.get(
    "/v1/inventory",
    status_code=status.HTTP_200_OK,
    response_model=List[InventoryItemResponse],
)
async def get_inventory(
    warehouse_id: Optional[str] = Query(None, description="Optional warehouse filter (RENO / COLUMBUS)"),
    user_claims: Dict[str, Any] = Depends(get_current_user_claims),
):
    """
    Get live inventory stock levels broken down by SKU, warehouse, and seller.

    Args:
        warehouse_id (Optional[str]): Warehouse filter query parameter.
        user_claims (Dict[str, Any]): Authenticated user claims.

    Returns:
        List[InventoryItemResponse]: List of inventory items.
    """
    try:
        logging.info("Calling GET /v1/inventory endpoint")
        result = WMSController().get_inventory(user_info=user_claims, warehouse_id=warehouse_id)
        return [InventoryItemResponse(**item) for item in result]
    except HTTPException as httperr:
        raise httperr
    except Exception as error:
        logging.error(f"Error in GET /v1/inventory endpoint: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error fetching inventory",
        )


@inventory_router.get(
    "/v1/products",
    status_code=status.HTTP_200_OK,
    response_model=List[ProductResponse],
)
async def get_products(user_claims: Dict[str, Any] = Depends(get_current_user_claims)):
    """
    Get all registered products catalog.

    Args:
        user_claims (Dict[str, Any]): Authenticated user claims.

    Returns:
        List[ProductResponse]: List of products.
    """
    try:
        logging.info("Calling GET /v1/products endpoint")
        result = WMSController().get_products(user_info=user_claims)
        return [ProductResponse(**p) for p in result]
    except Exception as error:
        logging.error(f"Error in GET /v1/products endpoint: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error fetching products",
        )
