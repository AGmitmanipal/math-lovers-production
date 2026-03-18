"""
SQLAlchemy User model for the database.
Represents a user in the Math Lovers community platform.
"""
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()


class User(Base):
    """
    User database model.
    
    Attributes:
        id: Unique identifier (primary key)
        username: Unique username for the platform
        email: Unique email address
        hashed_password: Bcrypt-hashed password (never store plaintext)
        created_at: Timestamp when the user was created
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
