"""
Pydantic schemas for User CRUD operations.
These schemas are used for request validation and response serialization.
"""
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


class UserCreate(BaseModel):
    """Schema for user registration request."""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    """Schema for user login request."""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Schema for user response (no password included)."""
    id: int
    username: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True  # Support ORM model conversion


class TokenResponse(BaseModel):
    """Schema for token response after successful login."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for JWT token payload data."""
    sub: str  # subject (typically user email or ID)
    exp: int  # expiration time