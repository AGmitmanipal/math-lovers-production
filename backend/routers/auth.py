"""
Authentication routes for user registration and login.
Handles user signup with email/password and login with JWT token generation.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from database.database import get_db
from models.user import User
from schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse
from core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
)
from core.config import settings

router = APIRouter(
    prefix="/api/auth",
    tags=["authentication"],
    responses={400: {"description": "Bad request"}, 409: {"description": "Conflict"}},
)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.
    
    - **username**: Must be 3-50 characters, unique
    - **email**: Valid email address, unique
    - **password**: Minimum 8 characters (will be hashed with bcrypt)
    
    Returns the created user without the password field.
    
    Raises:
        409 Conflict: If username or email already exists
    """
    # Check if user already exists by email
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )
    
    # Check if username is already taken
    existing_username = db.query(User).filter(User.username == user_data.username).first()
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already taken",
        )
    
    # Hash the password securely
    hashed_password = hash_password(user_data.password)
    
    # Create new user in database
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user


@router.post("/login", response_model=TokenResponse)
async def login(user_data: UserLogin, response: Response, db: Session = Depends(get_db)):
    """
    Login user and return tokens.
    
    - **email**: Registered user email
    - **password**: User's password (will be verified against bcrypt hash)
    
    Returns:
        - **access_token**: Short-lived JWT (15 minutes by default)
        - **refresh_token**: Long-lived JWT (7 days by default) set in HttpOnly cookie
        - **token_type**: "bearer"
    
    The refresh token is also set as an HttpOnly secure cookie for enhanced security.
    
    Raises:
        401 Unauthorized: If credentials are invalid
    """
    # Query user by email
    db_user = db.query(User).filter(User.email == user_data.email).first()
    
    if not db_user or not verify_password(user_data.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create JWT tokens
    access_token = create_access_token(data={"sub": db_user.email})
    refresh_token = create_refresh_token(data={"sub": db_user.email})
    
    # Set refresh token in HttpOnly secure cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        max_age=7 * 24 * 60 * 60,  # 7 days in seconds
        secure=settings.COOKIE_SECURE,
        httponly=settings.COOKIE_HTTPONLY,
        samesite=settings.COOKIE_SAMESITE,
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }
