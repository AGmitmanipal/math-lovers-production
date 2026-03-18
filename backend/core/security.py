"""
Security utilities for password hashing and JWT token management.
Handles bcrypt hashing and JWT token creation/verification for authentication.
"""
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from core.config import settings
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from database.database import get_db
from sqlalchemy.orm import Session

load_dotenv()

# Password hashing context using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT configuration
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM

# HTTP Bearer token scheme for extracting tokens from Authorization header
security = HTTPBearer()


def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plaintext password against its bcrypt hash."""
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict) -> str:
    """
    Create a short-lived access token.
    
    Args:
        data: Dictionary with claims to encode (e.g., {"sub": "user@example.com"})
    
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """
    Create a long-lived refresh token.
    
    Args:
        data: Dictionary with claims to encode (e.g., {"sub": "user@example.com"})
    
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    credentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    FastAPI dependency to verify JWT token and return current user.
    
    This dependency:
    1. Extracts the token from the Authorization header (Bearer scheme)
    2. Verifies the JWT signature and expiration
    3. Retrieves the user from the database
    4. Raises 401 Unauthorized if token is missing, invalid, or expired
    
    Usage in routes:
        @router.get("/protected")
        async def protected_route(current_user = Depends(get_current_user)):
            return {"message": f"Hello {current_user.username}"}
    
    Args:
        credentials: Extracted Authorization header credentials
        db: Database session dependency
    
    Returns:
        User object from database
    
    Raises:
        HTTPException: 401 status if token is invalid or user not found
    """
    from models.user import User
    
    token = credentials.credentials
    
    try:
        # Decode token and extract payload
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing subject claim",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Query database for the user
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user
