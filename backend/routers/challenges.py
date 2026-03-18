"""
Protected routes for math challenges and theorems.
Example of using the get_current_user dependency to protect endpoints.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.database import get_db
from core.security import get_current_user
from schemas.user import UserResponse

router = APIRouter(
    prefix="/api/challenges",
    tags=["challenges"],
    responses={401: {"description": "Unauthorized"}},
)


@router.get("/daily-theorem", response_model=dict)
async def get_daily_theorem(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Protected route example: Get today's daily math theorem.
    
    Requires:
        - Valid JWT access token in Authorization header (Bearer scheme)
    
    Returns:
        - theorem: The daily math theorem
        - hint: A helpful hint for solving
        - difficulty: Challenge difficulty level
        - user_info: Information about the authenticated user
    
    Raises:
        401 Unauthorized: If token is missing, invalid, or expired
    """
    return {
        "theorem": "Pythagorean Theorem: a² + b² = c²",
        "hint": "In a right triangle, the square of the hypotenuse equals the sum of squares of the other two sides.",
        "difficulty": "beginner",
        "user_info": {
            "username": current_user.username,
            "email": current_user.email,
            "reputation_score": current_user.reputation_score,
        },
        "message": f"Welcome {current_user.username}! Solve today's theorem to earn points.",
    }


@router.post("/solve/{challenge_id}")
async def submit_solution(
    challenge_id: int,
    solution: dict,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Protected route example: Submit a solution to a challenge.
    
    Requires:
        - Valid JWT access token
    
    Parameters:
        - challenge_id: ID of the challenge
        - solution: JSON containing the solution attempt
    
    Returns:
        - correct: Whether the solution is correct
        - points_earned: Points awarded if correct
        - new_reputation_score: Updated user reputation
    """
    # In a real implementation, validate the solution here
    is_correct = True  # Placeholder
    points = 10 if is_correct else 0
    
    # Update user reputation in database
    current_user.reputation_score += points
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    
    return {
        "correct": is_correct,
        "points_earned": points,
        "new_reputation_score": current_user.reputation_score,
    }
