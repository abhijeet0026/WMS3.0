"""
Seed script to initialize the 7-account roster per the Master Build Prompt.
"""
from core.database.database import SessionLocal, engine, Base
from core.models.wms_models import User, UserRole
from commons.auth import hash_password
import uuid

def seed_users():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    roster = [
        {
            "username": "owner",
            "email": "owner@whitfieldfulfillment.com",
            "full_name": "Dan Whitfield (Owner)",
            "role": UserRole.OWNER,
            "facility_scope": None
        },
        {
            "username": "manager.reno",
            "email": "manager.reno@whitfieldfulfillment.com",
            "full_name": "Manager (Reno)",
            "role": UserRole.MANAGER,
            "facility_scope": "RENO"
        },
        {
            "username": "manager.columbus",
            "email": "manager.columbus@whitfieldfulfillment.com",
            "full_name": "Manager (Columbus)",
            "role": UserRole.MANAGER,
            "facility_scope": "COLUMBUS"
        },
        {
            "username": "staff.reno",
            "email": "staff.reno@whitfieldfulfillment.com",
            "full_name": "Staff (Reno)",
            "role": UserRole.TRUSTED_STAFF,
            "facility_scope": "RENO"
        },
        {
            "username": "staff.columbus",
            "email": "staff.columbus@whitfieldfulfillment.com",
            "full_name": "Staff (Columbus)",
            "role": UserRole.TRUSTED_STAFF,
            "facility_scope": "COLUMBUS"
        },
        {
            "username": "newhire.reno",
            "email": "newhire.reno@whitfieldfulfillment.com",
            "full_name": "New Hire (Reno)",
            "role": UserRole.NEW_HIRE,
            "facility_scope": "RENO"
        },
        {
            "username": "newhire.columbus",
            "email": "newhire.columbus@whitfieldfulfillment.com",
            "full_name": "New Hire (Columbus)",
            "role": UserRole.NEW_HIRE,
            "facility_scope": "COLUMBUS"
        }
    ]

    try:
        # Clear existing users
        db.query(User).delete()
        
        for u in roster:
            user_record = User(
                id=f"USR-{uuid.uuid4().hex[:8].upper()}",
                username=u["username"],
                email=u["email"],
                full_name=u["full_name"],
                password_hash=hash_password("password123"),
                role=u["role"],
                facility_scope=u["facility_scope"],
                created_by="SYSTEM"
            )
            db.add(user_record)
        
        db.commit()
        print("Database seeded with 7-account roster successfully.")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_users()
