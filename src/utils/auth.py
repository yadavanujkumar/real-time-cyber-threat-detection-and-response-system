# src/utils/auth.py

"""
Authentication utilities for the Real-Time Cyber Threat Detection and Response System.

Provides:
- JWT token generation and validation
- Password hashing and verification
- User authentication helpers
"""

import os
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from passlib.context import CryptContext
import logging

logger = logging.getLogger(__name__)

# JWT Configuration
JWT_SECRET = os.getenv("JWT_SECRET", "dev-jwt-secret-CHANGE-IN-PRODUCTION")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRY_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Payload data to encode in the token
        expires_delta: Optional custom expiration time
    
    Returns:
        str: Encoded JWT token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=JWT_EXPIRY_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })
    
    try:
        encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
        logger.info(f"Access token created for user: {data.get('sub', 'unknown')}")
        return encoded_jwt
    except Exception as e:
        logger.error(f"Error creating access token: {str(e)}")
        raise


def verify_token(token: str) -> Dict[str, Any]:
    """
    Verify and decode a JWT token.
    
    Args:
        token: JWT token string
    
    Returns:
        Dict: Decoded token payload
    
    Raises:
        jwt.ExpiredSignatureError: If token has expired
        jwt.InvalidTokenError: If token is invalid
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("Token verification failed: Token expired")
        raise
    except jwt.InvalidTokenError as e:
        logger.warning(f"Token verification failed: {str(e)}")
        raise


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.
    
    Args:
        password: Plain text password
    
    Returns:
        str: Hashed password
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.
    
    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password to compare against
    
    Returns:
        bool: True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def generate_demo_token(username: str = "demo_user", is_admin: bool = False) -> str:
    """
    Generate a demo JWT token for testing purposes.
    
    Args:
        username: Username to include in token
        is_admin: Whether user has admin privileges
    
    Returns:
        str: JWT token
    """
    token_data = {
        "sub": username,
        "admin": is_admin,
        "email": f"{username}@example.com"
    }
    return create_access_token(token_data)


# Example usage and testing
if __name__ == "__main__":
    # Generate a demo token
    print("=== JWT Token Generation Demo ===\n")
    
    # Generate token for regular user
    user_token = generate_demo_token("test_user", is_admin=False)
    print(f"User Token: {user_token}\n")
    
    # Generate token for admin
    admin_token = generate_demo_token("admin_user", is_admin=True)
    print(f"Admin Token: {admin_token}\n")
    
    # Verify token
    try:
        payload = verify_token(user_token)
        print(f"Token verified successfully!")
        print(f"Payload: {payload}\n")
    except Exception as e:
        print(f"Token verification failed: {str(e)}\n")
    
    # Password hashing demo
    print("=== Password Hashing Demo ===\n")
    password = "secure_password_123"
    hashed = hash_password(password)
    print(f"Original: {password}")
    print(f"Hashed: {hashed}")
    print(f"Verification: {verify_password(password, hashed)}\n")
