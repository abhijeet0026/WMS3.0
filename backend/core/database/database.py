"""
Database connection and session lifecycle manager.

Provides SQLite database engine and transactional session context helper.
"""

import os
from contextlib import contextmanager
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from commons.logger import logger

logging = logger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if os.environ.get("VERCEL"):
    DB_PATH = "/tmp/wms.db"
    import shutil
    if not os.path.exists(DB_PATH):
        try:
            shutil.copy2(os.path.join(BASE_DIR, "wms.db"), DB_PATH)
        except Exception as e:
            logging.error(f"Failed to copy DB to /tmp: {e}")
else:
    DB_PATH = os.path.join(BASE_DIR, "wms.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


@contextmanager
def session() -> Generator[Session, None, None]:
    """
    Provide a transactional database session context manager.

    Ensures rollback on exceptions and proper closing of sessions upon block exit.

    Yields:
        Session: SQLAlchemy active session instance.

    Raises:
        Exception: Re-raises any unhandled database transaction error after rollback.
    """
    logging.info("Executing database.session context manager")
    db_session = SessionLocal()
    try:
        yield db_session
    except Exception as error:
        logging.error(f"Rolling back database transaction due to error: {error}")
        db_session.rollback()
        raise error
    finally:
        db_session.close()


def get_db_session() -> Session:
    """
    Get a single database session instance for direct use or dependency injection.

    Returns:
        Session: New SQLAlchemy session instance.
    """
    return SessionLocal()
