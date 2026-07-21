from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.repository import UserRepository
from app.auth.schemas import LoginRequest, RegisterRequest, TokenResponse, UserResponse
from app.auth.service import AuthService
from app.database.session import get_db

health_rotuer = APIRouter(prefix="/health", tags=["Health Check"])
@health_rotuer.get("/")
async def health_check():
    return {
        "status": "healthy",
        "service": "AI Support Backend"
    }

@health_rotuer.get("/ready")
async def ready_check(
    db: AsyncSession = Depends(get_db),
):
    try:
        # Simply acquire a connection from the session
        await db.connection()

        return {
            "status": "ready",
            "database": "connected"
        }

    except Exception as e:
        return {
            "status": "not_ready",
            "database": "disconnected",
            "error": str(e)
        }

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])

@auth_router.post("/register", response_model=UserResponse)
async def register(
    data: RegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(UserRepository(db))
    user = await service.register(data)
    return UserResponse.model_validate(user)

@auth_router.post("/login", response_model=TokenResponse)
async def login(
    data: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(UserRepository(db))
    return await service.login(data)