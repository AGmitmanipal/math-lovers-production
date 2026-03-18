"""
Database configuration and session management.
Provides SQLAlchemy engine and session factory for database operations.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from core.config import settings

# Create database engine
# For production, consider using a connection pool with echo=False
engine = create_engine(
    settings.DATABASE_URL,
    echo=False,  # Set to True for SQL debugging in development
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a database session.
    Each request gets a fresh session, automatically closed after the request.
    
    Usage:
        @app.get("/users")
        async def read_users(db: Session = Depends(get_db)):
            return db.query(User).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables. Call this once at startup."""
    from models.user import Base
    Base.metadata.create_all(bind=engine)
    """
    FastAPI dependency that provides a database session.
    Each request gets a fresh session, automatically closed after the request.
    
    Usage:
        @app.get("/users")
        async def read_users(db: Session = Depends(get_db)):
            return db.query(User).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables. Call this once at startup."""
    from models.user import Base
    Base.metadata.create_all(bind=engine)
