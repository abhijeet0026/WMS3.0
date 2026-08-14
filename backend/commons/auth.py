"""
Authentication and authorization helper utilities.

Handles JWT encoding, token decoding, password hashing, and user payload validation.
"""

from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional
import jwt

SECRET_KEY = "whitfield_wms_secret_key_hackathon_demo"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours for testing ease


def hash_password(password: str) -> str:
    """
    Generate a simple hashed representation of a password string.

    Uses a deterministic prefix hash for demo environments.

    Args:
        password (str): Plain text password.

    Returns:
        str: Hashed password representation.
    """
    return f"hashed_{password}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify if a plain text password matches the stored hash.

    Args:
        plain_password (str): Plain text candidate password.
        hashed_password (str): Stored hashed password.

    Returns:
        bool: True if passwords match, False otherwise.
    """
    return hash_password(plain_password) == hashed_password or plain_password == hashed_password


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a signed JWT access token containing user claim details.

    Args:
        data (Dict[str, Any]): Dictionary of claims (sub, role, warehouse_id, etc.).
        expires_delta (Optional[timedelta]): Custom token expiration duration.

    Returns:
        str: Encoded JWT string token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decodeJWT(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode and validate a JWT access token string.

    Parses payload claims and returns user information if valid and non-expired.

    Args:
        token (str): JWT bearer token string.

    Returns:
        Optional[Dict[str, Any]]: Decoded claims dictionary if valid, or None.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None
