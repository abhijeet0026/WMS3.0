"""
Request Pydantic schemas for Whitfield Fulfillment WMS API endpoints.
"""

from typing import List, Optional
from pydantic import BaseModel, Field
from core.models.wms_models import UserRole, ItemCondition


class LoginRequest(BaseModel):
    """Payload for user authentication login."""
    username: str = Field(..., description="User account username or email ID")
    password: str = Field(..., description="User password")


class UserCreateRequest(BaseModel):
    """Payload for creating a staff account."""
    username: str = Field(..., description="Unique account username")
    email: str = Field(..., description="User official email ID")
    full_name: str = Field(..., description="User full name")
    password: str = Field(..., description="Account initial password")
    role: UserRole = Field(..., description="Assigned role tier")
    facility_scope: Optional[str] = Field(default=None, description="Warehouse facility code ('RENO' / 'COLUMBUS')")


class UserStatusRequest(BaseModel):
    """Payload for updating user account status."""
    status: str = Field(..., description="Target status ('ACTIVE' / 'INACTIVE')")


class PasswordResetRequest(BaseModel):
    """Payload for resetting a user's password."""
    new_password: str = Field(..., description="New password string")


class ShipmentItemCreate(BaseModel):
    """Line item creation request within a shipment."""
    product_id: str = Field(..., description="Product catalog ID or SKU")
    quantity: int = Field(..., gt=0, description="Quantity received")
    condition: ItemCondition = Field(default=ItemCondition.GOOD, description="Condition of items")
    damage_reason: Optional[str] = Field(default=None, description="Explanation if damaged")


class ReceiveShipmentRequest(BaseModel):
    """Payload to atomically receive an inbound seller shipment."""
    tracking_number: str = Field(..., description="Carrier tracking number or drop-off ticket")
    warehouse_id: str = Field(..., description="Warehouse location code (RENO / COLUMBUS)")
    seller_id: str = Field(..., description="Seller identifier")
    items: List[ShipmentItemCreate] = Field(..., min_items=1, description="List of received shipment lines")


class OrderItemCreate(BaseModel):
    """Line item creation request within an outbound order."""
    product_id: str = Field(..., description="Product catalog ID or SKU")
    quantity: int = Field(..., gt=0, description="Quantity to pull and ship")


class CreateOrderRequest(BaseModel):
    """Payload to create an outbound order ready for picking."""
    order_number: str = Field(..., description="Unique customer order reference")
    warehouse_id: str = Field(..., description="Warehouse code (RENO / COLUMBUS)")
    seller_id: str = Field(..., description="Seller identifier")
    customer_name: str = Field(..., description="Customer destination name")
    items: List[OrderItemCreate] = Field(..., min_items=1, description="Order item lines")


class ShipOrderRequest(BaseModel):
    """Payload to atomically pick, pack, weigh, and ship an order."""
    order_id: str = Field(..., description="Target order ID")
    weight_lbs: Optional[str] = Field(default="1.5 lbs", description="Package total weight")


class VoiceAssistantRequest(BaseModel):
    """Payload for natural language chat/voice input parsing."""
    user_query: str = Field(..., description="Transcribed voice command or user chat message")
    warehouse_id: Optional[str] = Field(default=None, description="Current context warehouse ID")


class ReconcileIssueRequest(BaseModel):
    """Payload for manual reconciliation of legacy Excel bad data."""
    issue_id: str = Field(..., description="Legacy spreadsheet issue ID")
    actual_physical_quantity: int = Field(..., ge=0, description="Verified physical stock count")
    notes: Optional[str] = Field(default=None, description="Manager cleanup notes")
