"""
Database persistence models for Whitfield Fulfillment WMS.

Defines schemas for Users, Warehouses, Sellers, Products, Inventory,
Shipments, Orders, Audit Logs, and Data Reconciliations.
"""

from datetime import datetime, timezone
import enum
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum, Text, JSON
from sqlalchemy.orm import relationship
from core.database.database import Base


class UserRole(str, enum.Enum):
    """Enumeration of system access roles."""
    OWNER = "OWNER"
    MANAGER = "MANAGER"
    TRUSTED_STAFF = "TRUSTED_STAFF"
    NEW_HIRE = "NEW_HIRE"


class ItemCondition(str, enum.Enum):
    """Condition of received product stock."""
    GOOD = "GOOD"
    DAMAGED = "DAMAGED"


class ShipmentStatus(str, enum.Enum):
    """Status of incoming seller shipments."""
    PENDING = "PENDING"
    RECEIVED = "RECEIVED"


class OrderStatus(str, enum.Enum):
    """Status of outgoing customer orders."""
    PENDING = "PENDING"
    SHIPPED = "SHIPPED"
    CANCELLED = "CANCELLED"


class User(Base):
    """User account entity with role and assigned warehouse scope."""
    __tablename__ = "users"

    id = Column(String(50), primary_key=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=True, index=True)
    full_name = Column(String(100), nullable=False)
    password_hash = Column(String(200), nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.NEW_HIRE)
    facility_scope = Column(String(50), nullable=True)  # NULL means all warehouses
    status = Column(String(20), default="ACTIVE")
    created_by = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Warehouse(Base):
    """Warehouse facility location model (Reno, NV and Columbus, OH)."""
    __tablename__ = "warehouses"

    id = Column(String(50), primary_key=True)  # 'RENO' or 'COLUMBUS'
    name = Column(String(100), nullable=False)
    location = Column(String(100), nullable=False)
    address = Column(String(200), nullable=True)


class Seller(Base):
    """Online seller client storing stock at Whitfield Fulfillment."""
    __tablename__ = "sellers"

    id = Column(String(50), primary_key=True)
    name = Column(String(100), nullable=False)
    contact_email = Column(String(100), nullable=False)


class Product(Base):
    """Product SKU catalog item."""
    __tablename__ = "products"

    id = Column(String(50), primary_key=True)
    sku = Column(String(50), unique=True, nullable=False, index=True)
    upc = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    seller_id = Column(String(50), ForeignKey("sellers.id"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Inventory(Base):
    """Stock record per product, warehouse, and seller."""
    __tablename__ = "inventories"

    id = Column(String(50), primary_key=True)
    product_id = Column(String(50), ForeignKey("products.id"), nullable=False, index=True)
    warehouse_id = Column(String(50), ForeignKey("warehouses.id"), nullable=False, index=True)
    seller_id = Column(String(50), ForeignKey("sellers.id"), nullable=False)
    quantity_good = Column(Integer, default=0, nullable=False)
    quantity_damaged = Column(Integer, default=0, nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Shipment(Base):
    """Inbound shipment record."""
    __tablename__ = "shipments"

    id = Column(String(50), primary_key=True)
    tracking_number = Column(String(100), unique=True, nullable=False, index=True)
    ticket_number = Column(String(100), nullable=True)
    warehouse_id = Column(String(50), ForeignKey("warehouses.id"), nullable=False)
    seller_id = Column(String(50), ForeignKey("sellers.id"), nullable=False)
    status = Column(SQLEnum(ShipmentStatus), default=ShipmentStatus.PENDING, nullable=False)
    created_by_user_id = Column(String(50), ForeignKey("users.id"), nullable=False)
    received_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    items = relationship("ShipmentItem", backref="shipment", cascade="all, delete-orphan")


class ShipmentItem(Base):
    """Line item contained within an inbound shipment."""
    __tablename__ = "shipment_items"

    id = Column(String(50), primary_key=True)
    shipment_id = Column(String(50), ForeignKey("shipments.id"), nullable=False)
    product_id = Column(String(50), ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    condition = Column(SQLEnum(ItemCondition), default=ItemCondition.GOOD, nullable=False)
    damage_reason = Column(Text, nullable=True)
    internal_barcode = Column(String(100), unique=True, nullable=True, index=True)


class Order(Base):
    """Outbound customer order record."""
    __tablename__ = "orders"

    id = Column(String(50), primary_key=True)
    order_number = Column(String(100), unique=True, nullable=False, index=True)
    warehouse_id = Column(String(50), ForeignKey("warehouses.id"), nullable=False)
    seller_id = Column(String(50), ForeignKey("sellers.id"), nullable=False)
    customer_name = Column(String(100), nullable=True)
    status = Column(SQLEnum(OrderStatus), default=OrderStatus.PENDING, nullable=False)
    created_by_user_id = Column(String(50), ForeignKey("users.id"), nullable=False)
    shipped_at = Column(DateTime, nullable=True)
    weight_lbs = Column(String(20), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    items = relationship("OrderItem", backref="order", cascade="all, delete-orphan")


class OrderItem(Base):
    """Line item contained within an outbound order."""
    __tablename__ = "order_items"

    id = Column(String(50), primary_key=True)
    order_id = Column(String(50), ForeignKey("orders.id"), nullable=False)
    product_id = Column(String(50), ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)


class AuditLog(Base):
    """Immutable audit trail log entry capturing every system write."""
    __tablename__ = "audit_logs"

    id = Column(String(50), primary_key=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    user_id = Column(String(50), nullable=False)
    user_name = Column(String(100), nullable=False)
    role = Column(String(50), nullable=False)
    warehouse_id = Column(String(50), nullable=True)
    action = Column(String(50), nullable=False, index=True)  # e.g., RECEIVE_SHIPMENT, SHIP_ORDER, RECONCILE_DATA
    entity_type = Column(String(50), nullable=False)       # e.g., Inventory, Shipment, Order
    entity_id = Column(String(100), nullable=False)
    old_value = Column(JSON, nullable=True)
    new_value = Column(JSON, nullable=True)
    details = Column(Text, nullable=True)


class LegacySpreadsheetIssue(Base):
    """Record of legacy Excel data anomalies needing manual/assisted reconciliation."""
    __tablename__ = "legacy_spreadsheet_issues"

    id = Column(String(50), primary_key=True)
    issue_type = Column(String(50), nullable=False) # e.g. DOUBLE_LOGGED_SHIPMENT, OVERALLOCATED_ORDER
    description = Column(Text, nullable=False)
    warehouse_id = Column(String(50), nullable=False)
    seller_name = Column(String(100), nullable=False)
    product_sku = Column(String(50), nullable=False)
    excel_quantity = Column(Integer, nullable=False)
    actual_physical_quantity = Column(Integer, nullable=True)
    status = Column(String(30), default="UNRESOLVED") # UNRESOLVED, RECONCILED
    resolved_by_user_id = Column(String(50), nullable=True)
    resolved_at = Column(DateTime, nullable=True)
