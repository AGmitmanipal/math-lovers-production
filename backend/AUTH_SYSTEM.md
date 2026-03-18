# Math Lovers Authentication System

## Overview

This is a production-ready JWT-based authentication system for the Math Lovers community platform. The system uses:

- **FastAPI** - Modern async web framework
- **SQLAlchemy** - ORM for database operations
- **Pydantic** - Request/response validation
- **passlib + bcrypt** - Secure password hashing
- **python-jose** - JWT token management

## Architecture

```
├── main.py                 # FastAPI app entry point
├── core/
│   ├── config.py          # Settings from environment variables
│   └── security.py        # Password hashing, JWT, dependencies
├── database/
│   └── database.py        # SQLAlchemy session & engine setup
├── models/
│   └── user.py            # SQLAlchemy User model
├── schemas/
│   └── user.py            # Pydantic validation schemas
├── routers/
│   ├── auth.py            # Authentication endpoints
│   └── ai_agent_layer.py  # AI agent integration endpoints
└── .env                   # Environment configuration
```

## Key Features

### 1. Secure Password Hashing
- Uses bcrypt via `passlib`
- Passwords are hashed before storage
- Uses `verify_password()` for comparison without rehashing

### 2. JWT Tokens
- **Access Token**: Short-lived (15 min default) for API requests
- **Refresh Token**: Long-lived (7 days default) for token refresh
- Structured with claims: `{"sub": "user@email.com", "exp": timestamp}`

### 3. Token Security
- Access token returned in JSON response
- Refresh token set in HttpOnly secure cookie
- HTTP Bearer scheme for Authorization header

### 4. Dependency Injection
- FastAPI's `Depends()` system for clean, reusable security
- `get_current_user` dependency extracts and verifies tokens
- Automatic 401 Unauthorized response for missing/invalid tokens

## API Endpoints

### Authentication

#### POST `/api/auth/register`
Register a new user.

**Request:**
```json
{
  "username": "mathwiz123",
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "username": "mathwiz123",
  "email": "user@example.com",
  "created_at": "2026-03-18T10:30:00"
}
```

---

#### POST `/api/auth/login`
Login and receive tokens.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Note:** `refresh_token` is also set as an HttpOnly cookie for security.

---

### Protected Routes

Protected routes are implemented using the `get_current_user` dependency. Example:

```python
@router.get("/protected-endpoint")
async def protected_route(current_user = Depends(get_current_user)):
    return {"message": f"Hello {current_user.username}"}
```

**Headers:**
```
Authorization: Bearer <access_token>
```

---

## How JWT Authentication Works

### 1. **Token Creation (Login)**
```python
# User enters credentials
POST /api/auth/login
├─ Verify email exists
├─ Verify password (bcrypt comparison)
├─ Create access token: JWT with "sub" = user email, expires in 15 min
├─ Create refresh token: JWT with "sub" = user email, expires in 7 days
└─ Return access token, set refresh token cookie
```

### 2. **Token Verification (Protected Route)**
```python
# Client sends request with token
GET /api/protected-endpoint
Authorization: Bearer <token>
│
├─ HTTPBearer extracts token from Authorization header
├─ get_current_user dependency:
│  ├─ Decode JWT signature (verifies SECRET_KEY + ALGORITHM match)
│  ├─ Check expiration time
│  ├─ Extract "sub" claim (user email)
│  └─ Query database for user
└─ If valid: pass User object to route handler
   If invalid: return 401 Unauthorized
```

### 3. **Dependency Injection in Routes**
```python
@router.get("/protected-endpoint")
async def protected_route(current_user = Depends(get_current_user)):
    # current_user is automatically validated User object
    return {"user": current_user.username}
```

## Configuration (.env)

```env
# JWT Configuration (change SECRET_KEY in production!)
SECRET_KEY=your-secret-key-at-least-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# Database
DATABASE_URL=sqlite:///./mathlovers.db
# For PostgreSQL:
# DATABASE_URL=postgresql://user:password@localhost/mathlovers

# Cookie Security
COOKIE_SECURE=false  # true in production with HTTPS
COOKIE_HTTPONLY=true
COOKIE_SAMESITE=lax
```

## Running the Application

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables
Create `.env` file (see above) and update `SECRET_KEY` for production.

### 3. Run Server
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Test Endpoints
- Interactive docs: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc

## Testing Authentication Flow

### 1. Register User
```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123"
  }'
```

### 2. Login
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

Copy the `access_token` from response.

## Security Best Practices

✅ **Implemented:**
- ✓ Passwords hashed with bcrypt
- ✓ JWT signature verification
- ✓ Token expiration validation
- ✓ HttpOnly cookies for refresh tokens
- ✓ Dependency injection for clean auth logic
- ✓ User queried from database (prevents token spoofing)
- ✓ HTTP Bearer scheme for API tokens

⚠️ **Production Checklist:**
- [ ] Change `SECRET_KEY` to strong random value (32+ characters)
- [ ] Set `DATABASE_URL` to production database (PostgreSQL recommended)
- [ ] Set `COOKIE_SECURE=true` with HTTPS enforced
- [ ] Configure CORS `allow_origins` for production domain
- [ ] Enable HTTPS/TLS on server
- [ ] Set strong database credentials
- [ ] Implement rate limiting on auth endpoints
- [ ] Add password strength validation
- [ ] Consider implementing email verification
- [ ] Monitor token refresh patterns
- [ ] Use environment variables (never commit secrets)

## Database Schema

### users table
```sql
CREATE TABLE users (
  id INTEGER PRIMARY KEY,
  username VARCHAR UNIQUE NOT NULL,
  email VARCHAR UNIQUE NOT NULL,
  hashed_password VARCHAR NOT NULL,
  created_at DATETIME DEFAULT NOW()
);
```

## Error Responses

### Invalid Credentials
```json
{
  "detail": "Invalid email or password"
}
```
Status: **401 Unauthorized**

### User Already Exists
```json
{
  "detail": "Email already registered"
}
```
Status: **409 Conflict**

### Missing/Invalid Token
```json
{
  "detail": "Invalid or expired token"
}
```
Status: **401 Unauthorized**

## Extending the System

### Add More Protected Routes
```python
@router.get("/my-profile")
async def get_profile(current_user = Depends(get_current_user)):
    return current_user
```

### Implement Token Refresh
```python
@router.post("/api/auth/refresh")
async def refresh_tokens(request: Request):
    refresh_token = request.cookies.get("refresh_token")
    # Verify and issue new access token
```

### Add Role-Based Access Control
```python
from enum import Enum

class UserRole(enum.Enum):
    USER = "user"
    ADMIN = "admin"

# Add to User model: role = Column(String, default="user")
# Create dependency: def get_admin_user(user = Depends(get_current_user))
```

## Troubleshooting

**Issue:** "Import could not be resolved"
- Solution: Install dependencies: `pip install -r requirements.txt`

**Issue:** "Invalid token" on protected routes
- Solution: Make sure token is in Authorization header: `Bearer <token>`

**Issue:** Database not initializing
- Solution: Check DATABASE_URL in .env and ensure write permissions

**Issue:** CORS errors from frontend
- Solution: Update `allow_origins` in main.py CORS middleware

## References

- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [JWT.io](https://jwt.io)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/)
- [Pydantic Validation](https://docs.pydantic.dev/)
- [passlib Documentation](https://passlib.readthedocs.io/)
