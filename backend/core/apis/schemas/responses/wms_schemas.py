"""
Response Pydantic schemas for Whitfield Fulfillment WMS API endpoints.
"""

from datetime import datetime
from typing import List, Optional, Any
from pydantic import BaseModel, ConfigDict
from core.models.wms_models import UserRole, ShipmentStatus, OrderStatus, ItemCondition


class UserResponse(BaseModel):
    """Authenticated user response schema."""
    id: str
    username: str
    email: Optional[str] = None
    full_name: str
    role: UserRole
    facility_scope: Optional[str] = None
    access_token: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ProductResponse(BaseModel):
    """Product catalog details schema."""
    id: str
    sku: str
    upc: str
    name: str
    description: Optional[str] = None
    seller_id: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class InventoryItemResponse(BaseModel):
    """Stock level schema by product and warehouse."""
    id: str
    product_id: str
    product_sku: str
    product_upc: str
    product_name: str
    warehouse_id: str
    seller_id: Optional[str] = None
    seller_name: Optional[str] = None
    quantity_good: int
    quantity_damaged: int
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ShipmentResponse(BaseModel):
    """Shipment details schema."""
    id: str
    tracking_number: str
    ticket_number: Optional[str] = None
    warehouse_id: str
    seller_id: str
    status: ShipmentStatus
    created_by_user_id: str
    received_at: Optional[datetime] = None
    created_at: datetime
    is_duplicate_attempt: bool = False

    model_config = ConfigDict(from_attributes=True)


class OrderResponse(BaseModel):
    """Order response schema."""
    id: str
    order_number: str
    warehouse_id: str
    seller_id: str
    customer_name: Optional[str] = None
    status: OrderStatus
    created_by_user_id: str
    shipped_at: Optional[datetime] = None
    weight_lbs: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AuditLogResponse(BaseModel):
    """Audit log entry response schema."""
    id: str
    timestamp: datetime
    user_id: str
    user_name: str
    role: str
    warehouse_id: Optional[str] = None
    action: str
    entity_type: str
    entity_id: str
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    details: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class VoiceAssistantResponse(BaseModel):
    """Response payload for voice and chat assistant queries."""
    intent: str
    spoken_response: str
    action_executed: bool = False
    data: Optional[Any] = None


class LegacyIssueResponse(BaseModel):
    """Legacy spreadsheet anomaly item response."""
    id: str
    issue_type: str
    description: str
    warehouse_id: str
    seller_name: str
    product_sku: str
    excel_quantity: int
    actual_physical_quantity: Optional[int] = None
    status: str

    model_config = ConfigDict(from_attributes=True)
