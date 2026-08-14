"""
Controller layer for Whitfield Fulfillment WMS business logic and RBAC validation.
"""

from typing import Dict, Any, List, Optional
from fastapi import HTTPException, status
from commons.logger import logger
from core.cruds.wms_cruds import CRUDWMS
from core.services.assistant_service import AssistantService

logging = logger(__name__)


class WMSController:
    """Controller orchestrating domain access and role security rules."""

    def __init__(self):
        """Initialize controller with CRUD and Assistant services."""
        logging.info("Executing WMSController.__init__")
        self.crud = CRUDWMS()
        self.assistant = AssistantService()

    # -------------------------------------------------------------------------
    # AUTHENTICATION & USERS
    # -------------------------------------------------------------------------
    def login_user(self, username: str, password: str) -> Dict[str, Any]:
        """
        Authenticate user and return account information + access token.

        Args:
            username (str): User login username.
            password (str): User password.

        Returns:
            Dict[str, Any]: Authenticated user object with token payload.

        Raises:
            HTTPException 401: Invalid credentials.
        """
        logging.info("Executing WMSController.login_user")
        user = self.crud.get_user_by_username(username)
        if not user or (user["password_hash"] != f"hashed_{password}" and user["password_hash"] != password):
            logging.warning(f"Failed login attempt for username: {username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if user.get("status") != "ACTIVE":
            logging.warning(f"Login attempt for inactive user: {username}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive",
            )
        from commons.auth import create_access_token
        token_payload = {
            "sub": user["username"],
            "username": user["username"],
            "id": user["id"],
            "email": user.get("email"),
            "role": user["role"],
            "facility_scope": user["facility_scope"],
            "full_name": user["full_name"],
        }
        access_token = create_access_token(data=token_payload)

        return {
            "id": user["id"],
            "username": user["username"],
            "email": user.get("email"),
            "full_name": user["full_name"],
            "role": user["role"],
            "facility_scope": user["facility_scope"],
            "access_token": access_token,
        }

    # -------------------------------------------------------------------------
    # RBAC VALIDATION HELPER
    # -------------------------------------------------------------------------
    def _validate_role_and_warehouse(
        self,
        user_info: Dict[str, Any],
        allowed_roles: List[str],
        target_warehouse_id: Optional[str] = None
    ):
        """
        Validate role level permissions and optional warehouse scoping.

        Raises:
            HTTPException 403: If role is insufficient or warehouse access denied.
        """
        user_role = user_info.get("role")
        if user_role not in allowed_roles:
            logging.warning(f"Role '{user_role}' denied access. Required: {allowed_roles}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{user_role}' does not have permission to execute this operation",
            )

        assigned_wh = user_info.get("facility_scope")
        if assigned_wh and target_warehouse_id and assigned_wh != target_warehouse_id and user_role != "OWNER":
            logging.warning(f"User restricted to warehouse '{assigned_wh}' attempted access to '{target_warehouse_id}'")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Account is restricted to warehouse '{assigned_wh}' and cannot perform actions in '{target_warehouse_id}'",
            )

    def _filter_sensitive_data(self, records: List[Dict[str, Any]], user_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Filter out seller identity and cost data for restricted roles."""
        role = user_info.get("role")
        if role in ["OWNER", "MANAGER"]:
            return records
            
        for record in records:
            if "seller_id" in record:
                del record["seller_id"]
            if "seller_name" in record:
                del record["seller_name"]
        return records

    # -------------------------------------------------------------------------
    # USER ACCOUNT MANAGEMENT (OWNER & FACILITY-SCOPED MANAGER)
    # -------------------------------------------------------------------------
    def get_users(self, user_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Fetch registered user accounts.
        Owners see all users; Managers see users assigned to their warehouse facility.
        """
        self._validate_role_and_warehouse(user_info, allowed_roles=["OWNER", "MANAGER"])
        all_users = self.crud.get_all_users()
        user_role = user_info.get("role")
        assigned_wh = user_info.get("facility_scope")

        if user_role == "OWNER" or not assigned_wh:
            return all_users
        return [u for u in all_users if u.get("facility_scope") == assigned_wh]

    def create_user_account(
        self,
        user_info: Dict[str, Any],
        username: str,
        email: str,
        full_name: str,
        password: str,
        role: str,
        facility_scope: Optional[str]
    ) -> Dict[str, Any]:
        """
        Create a new user account with RBAC validation:
        - OWNER: can create any role and any warehouse scope.
        - MANAGER: can create ONLY 'TRUSTED_STAFF' or 'NEW_HIRE' within their own warehouse scope.
        """
        self._validate_role_and_warehouse(user_info, allowed_roles=["OWNER", "MANAGER"])
        creator_role = user_info.get("role")
        creator_wh = user_info.get("facility_scope")

        if creator_role == "MANAGER":
            if role not in ["TRUSTED_STAFF", "NEW_HIRE"]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Facility Managers can only onboard Trusted Staff and New Hire accounts",
                )
            if facility_scope != creator_wh:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Facility Managers can only onboard staff within their assigned warehouse '{creator_wh}'",
                )

        return self.crud.create_user(
            username=username,
            email=email,
            full_name=full_name,
            password=password,
            role=role,
            facility_scope=facility_scope,
            creator_user_info=user_info
        )

    def update_user_status(self, user_info: Dict[str, Any], target_user_id: str, new_status: str) -> Dict[str, Any]:
        """
        Update user account status (ACTIVE/INACTIVE).
        """
        self._validate_role_and_warehouse(user_info, allowed_roles=["OWNER", "MANAGER"])
        return self.crud.update_user_status(
            target_user_id=target_user_id,
            new_status=new_status,
            modifier_user_info=user_info
        )

    def reset_user_password(self, user_info: Dict[str, Any], target_user_id: str, new_password: str) -> Dict[str, Any]:
        """
        Reset user password.
        """
        self._validate_role_and_warehouse(user_info, allowed_roles=["OWNER", "MANAGER"])
        return self.crud.reset_user_password(
            target_user_id=target_user_id,
            new_password=new_password,
            modifier_user_info=user_info
        )

    # -------------------------------------------------------------------------
    # INVENTORY & CATALOG CONTROLLERS
    # -------------------------------------------------------------------------
    def get_inventory(self, user_info: Dict[str, Any], warehouse_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch live inventory levels with RBAC warehouse scoping."""
        logging.info("Executing WMSController.get_inventory")
        target_wh = warehouse_id or user_info.get("facility_scope")
        self._validate_role_and_warehouse(
            user_info=user_info,
            allowed_roles=["OWNER", "MANAGER", "TRUSTED_STAFF", "NEW_HIRE"],
            target_warehouse_id=target_wh
        )
        records = self.crud.get_inventory_summary(warehouse_id=target_wh)
        return self._filter_sensitive_data(records, user_info)

    def get_products(self, user_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Fetch catalog products."""
        logging.info("Executing WMSController.get_products")
        records = self.crud.get_products()
        return self._filter_sensitive_data(records, user_info)

    # -------------------------------------------------------------------------
    # RECEIVING CONTROLLER
    # -------------------------------------------------------------------------
    def receive_shipment(self, user_info: Dict[str, Any], request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process inbound shipment receiving with RBAC check.

        Allowed Roles: OWNER, MANAGER, TRUSTED_STAFF.
        """
        logging.info("Executing WMSController.receive_shipment")
        target_wh = request_data.get("warehouse_id")
        self._validate_role_and_warehouse(
            user_info=user_info,
            allowed_roles=["OWNER", "MANAGER", "TRUSTED_STAFF"],
            target_warehouse_id=target_wh,
        )

        shipment, is_dup = self.crud.receive_shipment_atomic(
            tracking_number=request_data["tracking_number"],
            warehouse_id=target_wh,
            seller_id=request_data["seller_id"],
            user_info=user_info,
            items_data=request_data["items"],
        )
        return shipment, is_dup

    # -------------------------------------------------------------------------
    # SHIPPING CONTROLLER
    # -------------------------------------------------------------------------
    def ship_order(self, user_info: Dict[str, Any], request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process outbound order shipping with RBAC check and stock atomic validation.

        Allowed Roles: OWNER, MANAGER, TRUSTED_STAFF.
        """
        logging.info("Executing WMSController.ship_order")
        order_id = request_data["order_id"]
        # Fetch order first to inspect warehouse
        orders = self.crud.get_orders()
        target_order = next((o for o in orders if o["id"] == order_id), None)
        if not target_order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

        self._validate_role_and_warehouse(
            user_info=user_info,
            allowed_roles=["OWNER", "MANAGER", "TRUSTED_STAFF"],
            target_warehouse_id=target_order["warehouse_id"],
        )

        try:
            return self.crud.ship_order_atomic(
                order_id=order_id,
                user_info=user_info,
                weight_lbs=request_data.get("weight_lbs", "1.5 lbs"),
            )
        except ValueError as err:
            logging.warning(f"Shipping validation failed: {err}")
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(err))

    def create_order(self, user_info: Dict[str, Any], request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create pending order with RBAC authorization."""
        logging.info("Executing WMSController.create_order")
        target_wh = request_data["warehouse_id"]
        self._validate_role_and_warehouse(
            user_info=user_info,
            allowed_roles=["OWNER", "MANAGER", "TRUSTED_STAFF"],
            target_warehouse_id=target_wh,
        )

        try:
            return self.crud.create_pending_order(
                order_number=request_data["order_number"],
                warehouse_id=target_wh,
                seller_id=request_data["seller_id"],
                customer_name=request_data["customer_name"],
                user_info=user_info,
                items_data=request_data["items"],
            )
        except ValueError as err:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))

    def get_orders(self, user_info: Dict[str, Any], warehouse_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch order queue with warehouse scoping."""
        logging.info("Executing WMSController.get_orders")
        target_wh = warehouse_id or user_info.get("facility_scope")
        self._validate_role_and_warehouse(
            user_info=user_info,
            allowed_roles=["OWNER", "MANAGER", "TRUSTED_STAFF", "NEW_HIRE"],
            target_warehouse_id=target_wh
        )
        records = self.crud.get_orders(warehouse_id=target_wh)
        return self._filter_sensitive_data(records, user_info)

    def get_shipments(self, user_info: Dict[str, Any], warehouse_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch shipment list with warehouse scoping."""
        logging.info("Executing WMSController.get_shipments")
        target_wh = warehouse_id or user_info.get("facility_scope")
        self._validate_role_and_warehouse(
            user_info=user_info,
            allowed_roles=["OWNER", "MANAGER", "TRUSTED_STAFF", "NEW_HIRE"],
            target_warehouse_id=target_wh
        )
        records = self.crud.get_shipments(warehouse_id=target_wh)
        return self._filter_sensitive_data(records, user_info)

    # -------------------------------------------------------------------------
    # AUDIT LOG CONTROLLER
    # -------------------------------------------------------------------------
    def get_audit_logs(
        self,
        user_info: Dict[str, Any],
        warehouse_id: Optional[str] = None,
        search_query: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Fetch audit trail logs. Available to MANAGER and OWNER."""
        logging.info("Executing WMSController.get_audit_logs")
        target_wh = warehouse_id or user_info.get("facility_scope")
        self._validate_role_and_warehouse(
            user_info=user_info,
            allowed_roles=["OWNER", "MANAGER"],
            target_warehouse_id=target_wh
        )
        return self.crud.get_audit_logs(warehouse_id=target_wh, search_query=search_query)

    # -------------------------------------------------------------------------
    # ASSISTANT CONTROLLER
    # -------------------------------------------------------------------------
    def query_assistant(self, user_info: Dict[str, Any], user_query: str, warehouse_id: Optional[str]) -> Dict[str, Any]:
        """Route assistant query to AssistantService."""
        logging.info("Executing WMSController.query_assistant")
        target_wh = warehouse_id or user_info.get("facility_scope")
        if target_wh == "ALL":
            target_wh = None

        # Check if query requests a specific warehouse (e.g. Columbus) while user is restricted
        wh_match = target_wh
        if "columbus" in user_query.lower():
            wh_match = "COLUMBUS"
        elif "reno" in user_query.lower():
            wh_match = "RENO"

        if wh_match:
            self._validate_role_and_warehouse(
                user_info=user_info,
                allowed_roles=["OWNER", "MANAGER", "TRUSTED_STAFF", "NEW_HIRE"],
                target_warehouse_id=wh_match
            )

        return self.assistant.process_query(
            query=user_query,
            user_info=user_info,
            warehouse_context=wh_match,
        )

    # -------------------------------------------------------------------------
    # LEGACY RECONCILIATION CONTROLLER
    # -------------------------------------------------------------------------
    def get_legacy_issues(self, user_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Fetch legacy spreadsheet errors for manager audit."""
        logging.info("Executing WMSController.get_legacy_issues")
        self._validate_role_and_warehouse(
            user_info=user_info,
            allowed_roles=["OWNER", "MANAGER"],
        )
        return self.crud.get_legacy_issues()

    def reconcile_issue(self, user_info: Dict[str, Any], request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Reconcile bad data issue. Allowed Roles: OWNER, MANAGER."""
        logging.info("Executing WMSController.reconcile_issue")
        self._validate_role_and_warehouse(
            user_info=user_info,
            allowed_roles=["OWNER", "MANAGER"],
        )
        try:
            return self.crud.reconcile_legacy_issue(
                issue_id=request_data["issue_id"],
                actual_quantity=int(request_data["actual_physical_quantity"]),
                user_info=user_info,
                notes=request_data.get("notes"),
            )
        except ValueError as err:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(err))
