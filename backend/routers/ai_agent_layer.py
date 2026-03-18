"""
AI Agent integration routes.
Protected endpoints for AI agent functionality to be integrated later.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.database import get_db
from core.security import get_current_user
from schemas.user import UserResponse

router = APIRouter(
    prefix="/api/ai",
    tags=["ai-agent"],
    responses={401: {"description": "Unauthorized"}},
)

# AI agent endpoints to be implemented

