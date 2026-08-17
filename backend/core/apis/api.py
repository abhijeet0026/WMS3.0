"""
FastAPI application aggregator for Whitfield Fulfillment WMS.

Configures database table creation, pre-seeding initial environment data,
registering API route surfaces, and applying CORS middleware.
"""

from contextlib import asynccontextmanager
from datetime import datetime, timezone
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import or_

from commons.auth import hash_password
from commons.logger import logger
from core.database.database import Base, engine, session
from core.models.wms_models import (
    User, UserRole, Warehouse, Seller, Product, Inventory,
    Shipment, Order, OrderItem, AuditLog, LegacySpreadsheetIssue, ShipmentStatus, OrderStatus
)

# Route imports
from core.apis.routes.auth_routes import auth_router
from core.apis.routes.inventory_routes import inventory_router
from core.apis.routes.receiving_routes import receiving_router
from core.apis.routes.shipping_routes import shipping_router
from core.apis.routes.audit_routes import audit_router
from core.apis.routes.assistant_routes import assistant_router
from core.apis.routes.migration_routes import migration_router

logging = logger(__name__)


def seed_initial_data():
    """Seed sample warehouses, users, sellers, products, stock, and legacy issues."""
    logging.info("Executing seed_initial_data")
    Base.metadata.create_all(bind=engine)

    with session() as db:
        demo_password = "password123"
        existing_users = db.query(User).all()
        if existing_users:
            legacy_hashes = {"hashed_admin123", "admin123", "hashed_password123"}
            needs_update = False
            canonical_demo_users = {
                "dan_owner": "dan.whitfield@whitfieldfulfillment.com",
                "manager_reno": "manager.reno@whitfieldfulfillment.com",
                "manager_columbus": "manager.columbus@whitfieldfulfillment.com",
                "staff_reno": "staff.reno@whitfieldfulfillment.com",
                "staff_columbus": "staff.columbus@whitfieldfulfillment.com",
                "newhire_reno": "newhire.reno@whitfieldfulfillment.com",
                "newhire_columbus": "newhire.columbus@whitfieldfulfillment.com",
            }

            for username, email in canonical_demo_users.items():
                user = db.query(User).filter(or_(User.username == username, User.email == email, User.username == "owner", User.email == "owner@whitfieldfulfillment.com")).first()
                if user:
                    if user.username != username or user.email != email:
                        user.username = username
                        user.email = email
                        user.full_name = user.full_name or username
                        needs_update = True
                    if user.password_hash != hash_password(demo_password):
                        user.password_hash = hash_password(demo_password)
                        needs_update = True
                    if user.role != "OWNER" and username == "dan_owner":
                        user.role = UserRole.OWNER
                        needs_update = True
                    if user.facility_scope is not None and username == "dan_owner":
                        user.facility_scope = None
                        needs_update = True

            legacy_owner = db.query(User).filter(User.username == "owner").first()
            if legacy_owner and legacy_owner.username != "dan_owner":
                legacy_owner.username = "dan_owner"
                legacy_owner.email = "dan.whitfield@whitfieldfulfillment.com"
                legacy_owner.full_name = "Dan Whitfield (Business Owner)"
                legacy_owner.role = UserRole.OWNER
                legacy_owner.facility_scope = None
                legacy_owner.password_hash = hash_password(demo_password)
                needs_update = True

            if needs_update:
                db.commit()
            logging.info("Database already seeded. Validated demo account credentials for the standard WMS login flow.")
            return

        now = datetime.now(timezone.utc)

        # 1. Warehouses
        wh_reno = Warehouse(id="RENO", name="Reno NV Warehouse", location="Reno, NV", address="100 Sierra Way, Reno, NV")
        wh_columbus = Warehouse(id="COLUMBUS", name="Columbus OH Warehouse", location="Columbus, OH", address="500 Buckeye Blvd, Columbus, OH")
        db.add_all([wh_reno, wh_columbus])

        # 2. Users with Roles (1 Owner + 3 Reno Facility Roles + 3 Columbus Facility Roles)
        user_owner = User(
            id="USR-001", username="dan_owner", email="dan.whitfield@whitfieldfulfillment.com", full_name="Dan Whitfield (Business Owner)",
            password_hash=hash_password(demo_password), role=UserRole.OWNER, facility_scope=None
        )
        user_mgr_reno = User(
            id="USR-002", username="manager_reno", email="manager.reno@whitfieldfulfillment.com", full_name="Reno Facility Manager",
            password_hash=hash_password(demo_password), role=UserRole.MANAGER, facility_scope="RENO"
        )
        user_staff_reno = User(
            id="USR-003", username="staff_reno", email="staff.reno@whitfieldfulfillment.com", full_name="Reno Trusted Staff",
            password_hash=hash_password(demo_password), role=UserRole.TRUSTED_STAFF, facility_scope="RENO"
        )
        user_hire_reno = User(
            id="USR-005", username="newhire_reno", email="newhire.reno@whitfieldfulfillment.com", full_name="Reno New Hire Staff",
            password_hash=hash_password(demo_password), role=UserRole.NEW_HIRE, facility_scope="RENO"
        )
        user_mgr_col = User(
            id="USR-006", username="manager_columbus", email="manager.columbus@whitfieldfulfillment.com", full_name="Columbus Facility Manager",
            password_hash=hash_password(demo_password), role=UserRole.MANAGER, facility_scope="COLUMBUS"
        )
        user_staff_col = User(
            id="USR-007", username="staff_columbus", email="staff.columbus@whitfieldfulfillment.com", full_name="Columbus Trusted Staff",
            password_hash=hash_password(demo_password), role=UserRole.TRUSTED_STAFF, facility_scope="COLUMBUS"
        )
        user_hire_col = User(
            id="USR-004", username="newhire_columbus", email="newhire.columbus@whitfieldfulfillment.com", full_name="Columbus New Hire Staff",
            password_hash=hash_password(demo_password), role=UserRole.NEW_HIRE, facility_scope="COLUMBUS"
        )
        db.add_all([user_owner, user_mgr_reno, user_staff_reno, user_hire_reno, user_mgr_col, user_staff_col, user_hire_col])

        # 3. Sellers
        seller_apex = Seller(id="SEL-001", name="Apex Electronics", contact_email="logistics@apexelectronics.com")
        seller_lumi = Seller(id="SEL-002", name="Lumi Home Goods", contact_email="orders@lumihome.com")
        db.add_all([seller_apex, seller_lumi])

        # 4. Products
        p1 = Product(id="PROD-101", sku="SKU-101", upc="850011223344", name="Wireless Noise-Canceling Headphones", description="Premium Bluetooth Over-Ear Headphones", seller_id="SEL-001")
        p2 = Product(id="PROD-102", sku="SKU-102", upc="850011223355", name="Ergonomic Desk Lamp", description="Dimmable LED Touch Desk Lamp", seller_id="SEL-002")
        p3 = Product(id="PROD-103", sku="SKU-103", upc="850011223366", name="Organic Bamboo Pillow", description="Hypoallergenic Memory Foam Pillow", seller_id="SEL-002")
        p4 = Product(id="PROD-104", sku="SKU-104", upc="850011223377", name="Gaming Mechanical Keyboard", description="RGB Backlit Tactile Keyboard", seller_id="SEL-001")
        db.add_all([p1, p2, p3, p4])

        # 5. Inventory
        inv1 = Inventory(id="INV-001", product_id="PROD-101", warehouse_id="RENO", seller_id="SEL-001", quantity_good=45, quantity_damaged=2, updated_at=now)
        inv2 = Inventory(id="INV-002", product_id="PROD-102", warehouse_id="RENO", seller_id="SEL-002", quantity_good=120, quantity_damaged=5, updated_at=now)
        inv3 = Inventory(id="INV-003", product_id="PROD-103", warehouse_id="COLUMBUS", seller_id="SEL-002", quantity_good=80, quantity_damaged=0, updated_at=now)
        inv4 = Inventory(id="INV-004", product_id="PROD-104", warehouse_id="COLUMBUS", seller_id="SEL-001", quantity_good=15, quantity_damaged=1, updated_at=now)
        db.add_all([inv1, inv2, inv3, inv4])

        # 6. Legacy Spreadsheet Issues (from problem statement: phantom doubled stock, oversold 9 units)
        iss1 = LegacySpreadsheetIssue(
            id="ISS-001", issue_type="DOUBLE_LOGGED_SHIPMENT",
            description="Laptop froze mid-entry during Excel logging; shipment logged twice phantom-doubling stock on Wireless Headphones.",
            warehouse_id="RENO", seller_name="Apex Electronics", product_sku="SKU-101",
            excel_quantity=90, actual_physical_quantity=None, status="UNRESOLVED"
        )
        iss2 = LegacySpreadsheetIssue(
            id="ISS-002", issue_type="OVERALLOCATED_ORDER",
            description="Two sellers both got order confirmations for the same 9 units due to concurrent un-synced Excel edits.",
            warehouse_id="COLUMBUS", seller_name="Lumi Home Goods", product_sku="SKU-103",
            excel_quantity=89, actual_physical_quantity=None, status="UNRESOLVED"
        )
        db.add_all([iss1, iss2])

        # Pending Order for Reno with at least one valid line item so shipping works in the live app
        ord1 = Order(
            id="ORD-001", order_number="ORD-1001", warehouse_id="RENO", seller_id="SEL-001",
            customer_name="Test Customer", status=OrderStatus.PENDING, created_by_user_id="USR-002",
            shipped_at=None, weight_lbs=None, created_at=now
        )
        db.add(ord1)

        order_item = OrderItem(
            id="OITEM-001",
            order_id="ORD-001",
            product_id="PROD-101",
            quantity=5,
        )
        db.add(order_item)

        # 7. Initial Audit Log Entry
        audit = AuditLog(
            id="AUD-000",
            timestamp=now,
            user_id="USR-001",
            user_name="System Initialization",
            role="SYSTEM",
            warehouse_id=None,
            action="SYSTEM_INIT",
            entity_type="Database",
            entity_id="wms.db",
            old_value=None,
            new_value="INITIALIZED",
            details="System database initialized with Reno NV and Columbus OH warehouses, product catalog, and legacy issue tracker.",
        )
        db.add(audit)

        db.commit()
        logging.info("Initial data seeded successfully.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for application startup and shutdown."""
    logging.info("Starting up Whitfield Fulfillment WMS API server")
    seed_initial_data()
    yield
    logging.info("Shutting down Whitfield Fulfillment WMS API server")


def create_app() -> FastAPI:
    """FastAPI application factory."""
    app = FastAPI(
        title="Whitfield Fulfillment WMS API",
        description="Transactional Warehouse Management System for Whitfield Fulfillment (Reno NV & Columbus OH)",
        version="1.0.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register Routers
    app.include_router(auth_router, tags=["Authentication"])
    app.include_router(inventory_router, tags=["Inventory & Catalog"])
    app.include_router(receiving_router, tags=["Receiving Operations"])
    app.include_router(shipping_router, tags=["Shipping Operations"])
    app.include_router(audit_router, tags=["Audit Trail"])
    app.include_router(assistant_router, tags=["Voice & Chat Assistant"])
    app.include_router(migration_router, tags=["Data Migration Reconciliation"])

    return app
