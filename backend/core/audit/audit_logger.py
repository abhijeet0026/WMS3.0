"""
Audit logging utility for Whitfield Fulfillment WMS.
"""
import uuid
import json
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from core.models.wms_models import AuditLog
from commons.logger import logger

logging = logger(__name__)

class AuditLogger:
    @staticmethod
    def log_action(
        db: Session,
        user_info: dict,
        action: str,
        entity_type: str,
        entity_id: str,
        old_value: dict = None,
        new_value: dict = None,
        details: str = None
    ):
        """
        Record a structured diff audit log entry.
        """
        try:
            log_entry = AuditLog(
                id=f"AUD-{uuid.uuid4().hex[:8].upper()}",
                timestamp=datetime.now(timezone.utc),
                user_id=user_info.get("id", "SYSTEM"),
                user_name=user_info.get("username", "SYSTEM"),
                role=user_info.get("role", "SYSTEM"),
                warehouse_id=user_info.get("facility_scope"),
                action=action,
                entity_type=entity_type,
                entity_id=entity_id,
                old_value=old_value,
                new_value=new_value,
                details=details
            )
            db.add(log_entry)
            db.commit()
            logging.info(f"Audit log recorded: {action} on {entity_type} {entity_id} by {user_info.get('username')}")
        except Exception as e:
            logging.error(f"Failed to write audit log: {str(e)}")
            db.rollback()
