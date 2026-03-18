"""
Math Lovers Community Platform - Backend API
FastAPI application with JWT authentication and protected routes.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database.database import init_db
from routers import auth, challenges

# Initialize FastAPI app
app = FastAPI(
    title="Math Lovers API",
    description="Community platform for math enthusiasts",
    version="1.0.0",
)

# CORS middleware configuration
# Allows frontend to communicate with this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080"],  # Update for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Initialize database tables on startup
@app.on_event("startup")
async def startup_event():
    """Create database tables if they don't exist."""
    init_db()


# Include routers for modular endpoint organization
app.include_router(auth.router)
app.include_router(challenges.router)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"message": "Math Lovers API is running!", "version": "1.0.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
