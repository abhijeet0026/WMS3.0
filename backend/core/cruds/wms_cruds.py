"""
CRUD persistence classes for Whitfield Fulfillment WMS.

Handles isolated database queries, atomic transactional inventory updates,
idempotent shipment receiving, concurrency-safe order shipping, and audit log generation.
"""

from datetime import datetime, timezone
import json
import uuid
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from commons.logger import logger
from core.database.database import session
from core.models.wms_models import (
    User, UserRole, Warehouse, Seller, Product, Inventory,
    Shipment, ShipmentItem, Order, OrderItem, AuditLog,
    ShipmentStatus, OrderStatus, ItemCondition, LegacySpreadsheetIssue
)

logging = logger(__name__)


def generate_uuid() -> str:
    """Utility to create a short unique string identifier."""
    return str(uuid.uuid4())[:8]


class CRUDWMS:
    """Main database CRUD handler for WMS resources."""

    # -------------------------------------------------------------------------
    # USER & AUTH CRUD
    # -------------------------------------------------------------------------
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Fetch a user by unique username or email.

        Args:
            username (str): Target username or email string.

        Returns:
            Optional[Dict[str, Any]]: User object dict or None.
        """
        logging.info("Executing CRUDWMS.get_user_by_username")
        try:
            with session() as db:
                user = db.query(User).filter(or_(User.username == username, User.email == username)).first()
                if not user:
                    return None
                return {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "full_name": user.full_name,
                    "password_hash": user.password_hash,
                    "role": user.role.value if hasattr(user.role, "value") else str(user.role),
                    "facility_scope": user.facility_scope,
                    "status": user.status,
                }
        except Exception as error:
            logging.error(f"Error in CRUDWMS.get_user_by_username: {error}")
            raise error

    def get_all_users(self) -> List[Dict[str, Any]]:
        """
        Retrieve all registered user accounts.

        Returns:
            List[Dict[str, Any]]: List of user dictionaries.
        """
        logging.info("Executing CRUDWMS.get_all_users")
        try:
            with session() as db:
                users = db.query(User).all()
                return [
                    {
                        "id": u.id,
                        "username": u.username,
                        "email": u.email,
                        "full_name": u.full_name,
                        "role": u.role.value if hasattr(u.role, "value") else str(u.role),
                        "facility_scope": u.facility_scope,
                        "status": u.status,
                    }
                    for u in users
                ]
        except Exception as error:
            logging.error(f"Error in CRUDWMS.get_all_users: {error}")
            raise error
    def create_user(
        self,
        username: str,
        email: str,
        full_name: str,
        password: str,
        role: str,
        facility_scope: Optional[str],
        creator_user_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a new user account and log audit action.
        """
        logging.info(f"Executing CRUDWMS.create_user for username={username}")
        try:
            with session() as db:
                # Check uniqueness
                existing = db.query(User).filter(or_(User.username == username, User.email == email)).first()
                if existing:
                    raise Exception("User with this username or email already exists")

                new_id = f"USR-{generate_uuid()}"
                user = User(
                    id=new_id,
                    username=username,
                    email=email,
                    full_name=full_name,
                    password_hash=f"hashed_{password}",
                    role=UserRole(role) if hasattr(UserRole, role) else role,
                    facility_scope=facility_scope,
                    status="ACTIVE"
                )
                db.add(user)

                # Log audit entry
                audit = AuditLog(
                    id=f"AUD-{generate_uuid()}",
                    timestamp=datetime.now(timezone.utc),
                    user_id=creator_user_info.get("id", "SYSTEM"),
                    user_name=creator_user_info.get("full_name", creator_user_info.get("username", "System")),
                    role=creator_user_info.get("role", "OWNER"),
                    warehouse_id=creator_user_info.get("facility_scope"),
                    action="CREATE_USER",
                    entity_type="User",
                    entity_id=new_id,
                    old_value=None,
                    new_value=f"Username: {username}, Role: {role}, Scope: {facility_scope or 'ALL'}",
                    details=f"Created user '{full_name}' ({email}) assigned to warehouse scope '{facility_scope or 'ALL'}'"
                )
                db.add(audit)
                db.commit()

                return {
                    "id": new_id,
                    "username": username,
                    "email": email,
                    "full_name": full_name,
                    "role": role,
                    "facility_scope": facility_scope,
                    "status": "ACTIVE"
                }
        except Exception as error:
            logging.error(f"Error in CRUDWMS.create_user: {error}")
            raise error

    def update_user_status(self, target_user_id: str, new_status: str, modifier_user_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update user account status (ACTIVE/INACTIVE) with audit logging.
        """
        logging.info(f"Executing CRUDWMS.update_user_status for user_id={target_user_id}")
        try:
            with session() as db:
                user = db.query(User).filter(User.id == target_user_id).first()
                if not user:
                    raise Exception("User not found")

                old_status = user.status
                user.status = new_status

                audit = AuditLog(
                    id=f"AUD-{generate_uuid()}",
                    timestamp=datetime.now(timezone.utc),
                    user_id=modifier_user_info.get("id", "SYSTEM"),
                    user_name=modifier_user_info.get("full_name", modifier_user_info.get("username", "System")),
                    role=modifier_user_info.get("role", "OWNER"),
                    warehouse_id=modifier_user_info.get("facility_scope"),
                    action="UPDATE_USER_STATUS",
                    entity_type="User",
                    entity_id=user.id,
                    old_value=f"status: {old_status}",
                    new_value=f"status: {new_status}",
                    details=f"Updated status for user '{user.username}' from {old_status} to {new_status}"
                )
                db.add(audit)
                db.commit()

                return {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "full_name": user.full_name,
                    "role": user.role.value if hasattr(user.role, "value") else str(user.role),
                    "facility_scope": user.facility_scope,
                    "status": user.status
                }
        except Exception as error:
            logging.error(f"Error in CRUDWMS.update_user_status: {error}")
            raise error

    def reset_user_password(self, target_user_id: str, new_password: str, modifier_user_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Reset user password with audit logging.
        """
        logging.info(f"Executing CRUDWMS.reset_user_password for user_id={target_user_id}")
        try:
            with session() as db:
                user = db.query(User).filter(User.id == target_user_id).first()
                if not user:
                    raise Exception("User not found")

                user.password_hash = f"hashed_{new_password}"

                audit = AuditLog(
                    id=f"AUD-{generate_uuid()}",
                    timestamp=datetime.now(timezone.utc),
                    user_id=modifier_user_info.get("id", "SYSTEM"),
                    user_name=modifier_user_info.get("full_name", modifier_user_info.get("username", "System")),
                    role=modifier_user_info.get("role", "OWNER"),
                    warehouse_id=modifier_user_info.get("facility_scope"),
                    action="RESET_USER_PASSWORD",
                    entity_type="User",
                    entity_id=user.id,
                    old_value="password_hash: [PROTECTED]",
                    new_value="password_hash: UPDATED",
                    details=f"Reset password for user account '{user.username}' ({user.email})"
                )
                db.add(audit)
                db.commit()

                return {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "full_name": user.full_name,
                    "role": user.role.value if hasattr(user.role, "value") else str(user.role),
                    "facility_scope": user.facility_scope,
                    "status": user.status
                }
        except Exception as error:
            logging.error(f"Error in CRUDWMS.reset_user_password: {error}")
            raise error

    # -------------------------------------------------------------------------
    # INVENTORY & CATALOG CRUD
    # -------------------------------------------------------------------------
    def get_inventory_summary(self, warehouse_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Fetch aggregated inventory levels per SKU, seller, and warehouse location.

        Args:
            warehouse_id (Optional[str]): Warehouse filter ('RENO' / 'COLUMBUS').

        Returns:
            List[Dict[str, Any]]: Array of inventory item dicts with product details.
        """
        logging.info("Executing CRUDWMS.get_inventory_summary")
        try:
            with session() as db:
                query = db.query(Inventory, Product, Seller, Warehouse).join(
                    Product, Inventory.product_id == Product.id
                ).join(
                    Seller, Inventory.seller_id == Seller.id
                ).join(
                    Warehouse, Inventory.warehouse_id == Warehouse.id
                )

                if warehouse_id:
                    query = query.filter(Inventory.warehouse_id == warehouse_id)

                results = query.all()
                output = []
                for inv, prod, sel, wh in results:
                    output.append({
                        "id": inv.id,
                        "product_id": prod.id,
                        "product_sku": prod.sku,
                        "product_upc": prod.upc,
                        "product_name": prod.name,
                        "warehouse_id": wh.id,
                        "warehouse_name": wh.name,
                        "seller_id": sel.id,
                        "seller_name": sel.name,
                        "quantity_good": inv.quantity_good,
                        "quantity_damaged": inv.quantity_damaged,
                        "updated_at": inv.updated_at,
                    })
                return output
        except Exception as error:
            logging.error(f"Error in CRUDWMS.get_inventory_summary: {error}")
            raise error

    def get_products(self) -> List[Dict[str, Any]]:
        """Fetch all product catalog items."""
        logging.info("Executing CRUDWMS.get_products")
        try:
            with session() as db:
                products = db.query(Product).all()
                return [
                    {
                        "id": p.id,
                        "sku": p.sku,
                        "upc": p.upc,
                        "name": p.name,
                        "description": p.description,
                        "seller_id": p.seller_id,
                    }
                    for p in products
                ]
        except Exception as error:
            logging.error(f"Error in CRUDWMS.get_products: {error}")
            raise error

    # -------------------------------------------------------------------------
    # RECEIVING ATOMIC TRANSACTION & IDEMPOTENCY
    # -------------------------------------------------------------------------
    def receive_shipment_atomic(
        self,
        tracking_number: str,
        warehouse_id: str,
        seller_id: str,
        user_info: Dict[str, Any],
        items_data: List[Dict[str, Any]],
    ) -> Tuple[Dict[str, Any], bool]:
        """
        Atomically process an inbound shipment receiving event.

        Idempotency rule: If the tracking number has already been received, returns the
        existing record without applying double stock increments.

        Args:
            tracking_number (str): Unique carrier tracking or drop-off ticket number.
            warehouse_id (str): Destination warehouse ID.
            seller_id (str): Seller owner ID.
            user_info (Dict[str, Any]): Acting user claim details.
            items_data (List[Dict[str, Any]]): Array of items received (product_id/upc, quantity, condition).

        Returns:
            Tuple[Dict[str, Any], bool]: (Shipment object dictionary, is_duplicate_flag).
        """
        logging.info(f"Executing CRUDWMS.receive_shipment_atomic for tracking #{tracking_number}")
        with session() as db:
            existing_shipment = db.query(Shipment).filter(Shipment.tracking_number == tracking_number).first()
            if existing_shipment:
                logging.warning(f"Duplicate tracking number re-submitted: {tracking_number}. Returning existing shipment.")
                return {
                    "id": existing_shipment.id,
                    "tracking_number": existing_shipment.tracking_number,
                    "ticket_number": existing_shipment.ticket_number,
                    "warehouse_id": existing_shipment.warehouse_id,
                    "seller_id": existing_shipment.seller_id,
                    "status": existing_shipment.status.value,
                    "created_by_user_id": existing_shipment.created_by_user_id,
                    "received_at": existing_shipment.received_at,
                    "created_at": existing_shipment.created_at,
                    "is_duplicate_attempt": True,
                }, True

            # Create new shipment record
            shipment_id = f"SHIP-{generate_uuid()}"
            now = datetime.now(timezone.utc)

            shipment = Shipment(
                id=shipment_id,
                tracking_number=tracking_number,
                ticket_number=f"TICKET-{generate_uuid()}",
                warehouse_id=warehouse_id,
                seller_id=seller_id,
                status=ShipmentStatus.RECEIVED,
                created_by_user_id=user_info["id"],
                received_at=now,
                created_at=now,
            )
            db.add(shipment)

            added_lines_summary = []

            for item in items_data:
                prod_identifier = item["product_id"]
                # Match product by ID, SKU, or UPC
                product = db.query(Product).filter(
                    or_(Product.id == prod_identifier, Product.sku == prod_identifier, Product.upc == prod_identifier)
                ).first()

                if not product:
                    logging.warning(f"Product not found for identifier: {prod_identifier}. Auto-registering product catalog.")
                    product = Product(
                        id=f"PROD-{generate_uuid()}",
                        sku=f"SKU-{prod_identifier[-6:]}",
                        upc=prod_identifier,
                        name=f"Received Item {prod_identifier}",
                        description="Auto-registered during receiving scan",
                        seller_id=seller_id,
                    )
                    db.add(product)
                    db.flush()

                condition = ItemCondition(item.get("condition", "GOOD"))
                quantity = int(item["quantity"])

                internal_barcode = f"LBL-{generate_uuid().upper()}"
                
                shipment_item = ShipmentItem(
                    id=f"SITEM-{generate_uuid()}",
                    shipment_id=shipment_id,
                    product_id=product.id,
                    quantity=quantity,
                    condition=condition,
                    damage_reason=item.get("damage_reason"),
                    internal_barcode=internal_barcode,
                )
                db.add(shipment_item)

                # Upsert Inventory
                inv = db.query(Inventory).filter(
                    Inventory.product_id == product.id,
                    Inventory.warehouse_id == warehouse_id,
                    Inventory.seller_id == seller_id
                ).first()

                old_good = inv.quantity_good if inv else 0
                old_damaged = inv.quantity_damaged if inv else 0

                if not inv:
                    inv = Inventory(
                        id=f"INV-{generate_uuid()}",
                        product_id=product.id,
                        warehouse_id=warehouse_id,
                        seller_id=seller_id,
                        quantity_good=0,
                        quantity_damaged=0,
                        updated_at=now
                    )
                    db.add(inv)

                if condition == ItemCondition.GOOD:
                    inv.quantity_good += quantity
                else:
                    inv.quantity_damaged += quantity
                inv.updated_at = now

                added_lines_summary.append({
                    "sku": product.sku,
                    "product_name": product.name,
                    "quantity": quantity,
                    "condition": condition.value,
                    "old_stock": f"good:{old_good}, damaged:{old_damaged}",
                    "new_stock": f"good:{inv.quantity_good}, damaged:{inv.quantity_damaged}",
                })

            # Record Audit Log within same atomic transaction
            audit_log = AuditLog(
                id=f"AUD-{generate_uuid()}",
                timestamp=now,
                user_id=user_info["id"],
                user_name=user_info.get("full_name", user_info["username"]),
                role=user_info["role"],
                warehouse_id=warehouse_id,
                action="RECEIVE_SHIPMENT",
                entity_type="Shipment",
                entity_id=shipment_id,
                old_value="NEW_SHIPMENT",
                new_value=f"STATUS: RECEIVED (Tracking: {tracking_number})",
                details=json.dumps(added_lines_summary),
            )
            db.add(audit_log)

            db.commit()
            db.refresh(shipment)

            logging.info(f"Shipment {shipment_id} received atomically with {len(added_lines_summary)} item lines.")

            return {
                "id": shipment.id,
                "tracking_number": shipment.tracking_number,
                "ticket_number": shipment.ticket_number,
                "warehouse_id": shipment.warehouse_id,
                "seller_id": shipment.seller_id,
                "status": shipment.status.value,
                "created_by_user_id": shipment.created_by_user_id,
                "received_at": shipment.received_at,
                "created_at": shipment.created_at,
                "is_duplicate_attempt": False,
            }, False

    # -------------------------------------------------------------------------
    # SHIPPING ATOMIC TRANSACTION & OVERSELLING PREVENTION
    # -------------------------------------------------------------------------
    def ship_order_atomic(
        self,
        order_id: str,
        user_info: Dict[str, Any],
        weight_lbs: Optional[str] = "1.5 lbs",
    ) -> Dict[str, Any]:
        """
        Atomically process an outbound order shipping operation.

        Prevents overselling: Validates that adequate GOOD physical inventory exists for every line item
        under lock. If stock is insufficient, rolls back and raises ValueError.

        Args:
            order_id (str): Target pending order ID.
            user_info (Dict[str, Any]): Acting user details.
            weight_lbs (Optional[str]): Package weight.

        Returns:
            Dict[str, Any]: Updated order object details.

        Raises:
            ValueError: If order not found, already shipped, or insufficient inventory.
        """
        logging.info(f"Executing CRUDWMS.ship_order_atomic for order #{order_id}")
        with session() as db:
            order = db.query(Order).filter(Order.id == order_id).first()
            if not order:
                logging.warning(f"Order not found: {order_id}")
                raise ValueError("Order not found")

            if order.status == OrderStatus.SHIPPED:
                logging.warning(f"Order {order_id} is already shipped")
                raise ValueError(f"Order {order.order_number} has already been shipped")

            order_items = db.query(OrderItem).filter(OrderItem.order_id == order_id).all()
            if not order_items:
                raise ValueError("Order contains no line items")

            inventory_updates = []

            # Concurrency check & stock validation
            for item in order_items:
                product = db.query(Product).filter(Product.id == item.product_id).first()
                sku_name = product.sku if product else item.product_id

                inv = db.query(Inventory).filter(
                    Inventory.product_id == item.product_id,
                    Inventory.warehouse_id == order.warehouse_id,
                    Inventory.seller_id == order.seller_id
                ).with_for_update().first()

                available_good = inv.quantity_good if inv else 0
                if available_good < item.quantity:
                    err_msg = (
                        f"Insufficient stock for SKU '{sku_name}' in warehouse '{order.warehouse_id}'. "
                        f"Requested: {item.quantity}, Available: {available_good} units."
                    )
                    logging.warning(err_msg)
                    raise ValueError(err_msg)

                inventory_updates.append((inv, item.quantity, sku_name, available_good))

            # Perform atomic decrements
            now = datetime.now(timezone.utc)
            decrement_details = []

            for inv, qty, sku_name, old_qty in inventory_updates:
                inv.quantity_good -= qty
                inv.updated_at = now
                decrement_details.append({
                    "sku": sku_name,
                    "quantity_shipped": qty,
                    "stock_before": old_qty,
                    "stock_after": inv.quantity_good
                })

            order.status = OrderStatus.SHIPPED
            order.shipped_at = now
            order.weight_lbs = weight_lbs

            # Log audit trail
            audit_log = AuditLog(
                id=f"AUD-{generate_uuid()}",
                timestamp=now,
                user_id=user_info["id"],
                user_name=user_info.get("full_name", user_info["username"]),
                role=user_info["role"],
                warehouse_id=order.warehouse_id,
                action="SHIP_ORDER",
                entity_type="Order",
                entity_id=order.id,
                old_value="STATUS: PENDING",
                new_value=f"STATUS: SHIPPED (Order #: {order.order_number})",
                details=json.dumps(decrement_details),
            )
            db.add(audit_log)

            db.commit()
            db.refresh(order)

            logging.info(f"Order {order.order_number} shipped successfully and stock decremented.")

            return {
                "id": order.id,
                "order_number": order.order_number,
                "warehouse_id": order.warehouse_id,
                "seller_id": order.seller_id,
                "customer_name": order.customer_name,
                "status": order.status.value,
                "created_by_user_id": order.created_by_user_id,
                "shipped_at": order.shipped_at,
                "weight_lbs": order.weight_lbs,
                "created_at": order.created_at,
            }

    # -------------------------------------------------------------------------
    # ORDERS LISTING & CREATION
    # -------------------------------------------------------------------------
    def create_pending_order(
        self,
        order_number: str,
        warehouse_id: str,
        seller_id: str,
        customer_name: str,
        user_info: Dict[str, Any],
        items_data: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Create a pending customer order ready for picking and shipping."""
        logging.info("Executing CRUDWMS.create_pending_order")
        with session() as db:
            existing = db.query(Order).filter(Order.order_number == order_number).first()
            if existing:
                raise ValueError(f"Order number '{order_number}' already exists")

            order_id = f"ORD-{generate_uuid()}"
            now = datetime.now(timezone.utc)
            order = Order(
                id=order_id,
                order_number=order_number,
                warehouse_id=warehouse_id,
                seller_id=seller_id,
                customer_name=customer_name,
                status=OrderStatus.PENDING,
                created_by_user_id=user_info["id"],
                created_at=now,
            )
            db.add(order)

            for item in items_data:
                prod = db.query(Product).filter(
                    or_(Product.id == item["product_id"], Product.sku == item["product_id"])
                ).first()
                if not prod:
                    raise ValueError(f"Product '{item['product_id']}' not found in catalog")

                order_item = OrderItem(
                    id=f"OITEM-{generate_uuid()}",
                    order_id=order_id,
                    product_id=prod.id,
                    quantity=int(item["quantity"]),
                )
                db.add(order_item)

            db.commit()
            db.refresh(order)
            return {
                "id": order.id,
                "order_number": order.order_number,
                "warehouse_id": order.warehouse_id,
                "seller_id": order.seller_id,
                "customer_name": order.customer_name,
                "status": order.status.value,
                "created_by_user_id": order.created_by_user_id,
                "created_at": order.created_at,
            }

    def get_orders(self, warehouse_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch order queue filtered optionally by warehouse."""
        logging.info("Executing CRUDWMS.get_orders")
        with session() as db:
            query = db.query(Order)
            if warehouse_id:
                query = query.filter(Order.warehouse_id == warehouse_id)
            orders = query.order_by(Order.created_at.desc()).all()
            result = []
            for o in orders:
                items = db.query(OrderItem, Product).join(
                    Product, OrderItem.product_id == Product.id
                ).filter(OrderItem.order_id == o.id).all()

                item_list = [
                    {
                        "product_sku": p.sku,
                        "product_name": p.name,
                        "quantity": oi.quantity,
                    }
                    for oi, p in items
                ]
                result.append({
                    "id": o.id,
                    "order_number": o.order_number,
                    "warehouse_id": o.warehouse_id,
                    "seller_id": o.seller_id,
                    "customer_name": o.customer_name,
                    "status": o.status.value,
                    "created_by_user_id": o.created_by_user_id,
                    "shipped_at": o.shipped_at,
                    "weight_lbs": o.weight_lbs,
                    "created_at": o.created_at,
                    "items": item_list,
                })
            return result

    def get_shipments(self, warehouse_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch list of inbound shipments."""
        logging.info("Executing CRUDWMS.get_shipments")
        with session() as db:
            query = db.query(Shipment)
            if warehouse_id:
                query = query.filter(Shipment.warehouse_id == warehouse_id)
            shipments = query.order_by(Shipment.created_at.desc()).all()
            result = []
            for s in shipments:
                items = db.query(ShipmentItem, Product).join(
                    Product, ShipmentItem.product_id == Product.id
                ).filter(ShipmentItem.shipment_id == s.id).all()

                item_list = [
                    {
                        "product_sku": p.sku,
                        "product_name": p.name,
                        "quantity": si.quantity,
                        "condition": si.condition.value,
                        "damage_reason": si.damage_reason,
                    }
                    for si, p in items
                ]

                result.append({
                    "id": s.id,
                    "tracking_number": s.tracking_number,
                    "ticket_number": s.ticket_number,
                    "warehouse_id": s.warehouse_id,
                    "seller_id": s.seller_id,
                    "status": s.status.value,
                    "created_by_user_id": s.created_by_user_id,
                    "received_at": s.received_at,
                    "created_at": s.created_at,
                    "items": item_list,
                })
            return result

    # -------------------------------------------------------------------------
    # AUDIT LOG SEARCH & FILTERING
    # -------------------------------------------------------------------------
    def get_audit_logs(
        self,
        warehouse_id: Optional[str] = None,
        search_query: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Fetch searchable audit trail logs.

        Args:
            warehouse_id (Optional[str]): Warehouse filter.
            search_query (Optional[str]): Search keyword across action, user, entity.
            limit (int): Max records.

        Returns:
            List[Dict[str, Any]]: Audit log dictionaries sorted newest first.
        """
        logging.info("Executing CRUDWMS.get_audit_logs")
        with session() as db:
            query = db.query(AuditLog)
            if warehouse_id:
                query = query.filter(AuditLog.warehouse_id == warehouse_id)

            if search_query:
                term = f"%{search_query}%"
                query = query.filter(
                    or_(
                        AuditLog.user_name.like(term),
                        AuditLog.action.like(term),
                        AuditLog.entity_type.like(term),
                        AuditLog.entity_id.like(term),
                        AuditLog.details.like(term),
                    )
                )

            logs = query.order_by(AuditLog.timestamp.desc()).limit(limit).all()
            return [
                {
                    "id": l.id,
                    "timestamp": l.timestamp,
                    "user_id": l.user_id,
                    "user_name": l.user_name,
                    "role": l.role,
                    "warehouse_id": l.warehouse_id,
                    "action": l.action,
                    "entity_type": l.entity_type,
                    "entity_id": l.entity_id,
                    "old_value": l.old_value,
                    "new_value": l.new_value,
                    "details": l.details,
                }
                for l in logs
            ]

    # -------------------------------------------------------------------------
    # LEGACY EXCEL DATA RECONCILIATION
    # -------------------------------------------------------------------------
    def get_legacy_issues(self) -> List[Dict[str, Any]]:
        """Fetch unresolved and resolved legacy spreadsheet issues."""
        logging.info("Executing CRUDWMS.get_legacy_issues")
        with session() as db:
            issues = db.query(LegacySpreadsheetIssue).all()
            return [
                {
                    "id": i.id,
                    "issue_type": i.issue_type,
                    "description": i.description,
                    "warehouse_id": i.warehouse_id,
                    "seller_name": i.seller_name,
                    "product_sku": i.product_sku,
                    "excel_quantity": i.excel_quantity,
                    "actual_physical_quantity": i.actual_physical_quantity,
                    "status": i.status,
                }
                for i in issues
            ]

    def reconcile_legacy_issue(
        self,
        issue_id: str,
        actual_quantity: int,
        user_info: Dict[str, Any],
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Reconcile a legacy spreadsheet error with physical verified count."""
        logging.info(f"Executing CRUDWMS.reconcile_legacy_issue for issue {issue_id}")
        with session() as db:
            issue = db.query(LegacySpreadsheetIssue).filter(LegacySpreadsheetIssue.id == issue_id).first()
            if not issue:
                raise ValueError("Legacy issue not found")

            # RBAC Validation for warehouse scope
            if user_info.get("facility_scope") and user_info["facility_scope"] != issue.warehouse_id:
                from fastapi import HTTPException
                raise HTTPException(status_code=403, detail="Manager cannot reconcile issues for a different facility")

            now = datetime.now(timezone.utc)
            old_qty = issue.excel_quantity
            issue.actual_physical_quantity = actual_quantity
            issue.status = "RECONCILED"
            issue.resolved_by_user_id = user_info["id"]
            issue.resolved_at = now

            # Find matching product and update inventory directly
            prod = db.query(Product).filter(Product.sku == issue.product_sku).first()
            if prod:
                inv = db.query(Inventory).filter(
                    Inventory.product_id == prod.id,
                    Inventory.warehouse_id == issue.warehouse_id
                ).first()
                if inv:
                    inv.quantity_good = actual_quantity
                    inv.updated_at = now

            # Audit log entry
            audit_log = AuditLog(
                id=f"AUD-{generate_uuid()}",
                timestamp=now,
                user_id=user_info["id"],
                user_name=user_info.get("full_name", user_info["username"]),
                role=user_info["role"],
                warehouse_id=issue.warehouse_id,
                action="RECONCILE_DATA",
                entity_type="LegacySpreadsheetIssue",
                entity_id=issue.id,
                old_value=f"Excel Qty: {old_qty}",
                new_value=f"Reconciled Physical Qty: {actual_quantity}",
                details=f"Reconciled by {user_info['username']}. Notes: {notes or 'Manual verification'}",
            )
            db.add(audit_log)

            db.commit()
            db.refresh(issue)
            return {
                "id": issue.id,
                "issue_type": issue.issue_type,
                "description": issue.description,
                "warehouse_id": issue.warehouse_id,
                "seller_name": issue.seller_name,
                "product_sku": issue.product_sku,
                "excel_quantity": issue.excel_quantity,
                "actual_physical_quantity": issue.actual_physical_quantity,
                "status": issue.status,
            }
