from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.auth.schemas import (
    LoginRequest, RegisterRequest, TokenResponse, UserResponse,
    ForgotPasswordRequest, VerifyOTPRequest, ResetPasswordRequest
)
from app.auth.service import AuthService
from app.database.session import get_db
from sqlalchemy import delete, select
from app.documents.models import DocumentMetadata
from app.storage.supabase_storage import SupabaseStorageService

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
    service = AuthService(db)
    user = await service.register(data)
    return UserResponse.model_validate(user)

@auth_router.post("/login", response_model=TokenResponse)
async def login(db: AsyncSession = Depends(get_db),form_data: OAuth2PasswordRequestForm  = Depends()):
    data = LoginRequest(email=form_data.username,password=form_data.password)
    service = AuthService(db)
    return await service.login(data)

@auth_router.get("/me", response_model=UserResponse)
async def me(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)

@auth_router.post("/forgot-password")
async def forgot_password(
    data: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    service = AuthService(db)
    await service.forgot_password(data.email)
    return {"status": "success", "message": "If that email matches an account, we've sent an OTP."}

@auth_router.post("/verify-otp")
async def verify_otp(
    data: VerifyOTPRequest,
    db: AsyncSession = Depends(get_db)
):
    service = AuthService(db)
    await service.verify_otp(data.email, data.otp)
    return {"status": "success", "message": "OTP is valid."}

@auth_router.post("/reset-password")
async def reset_password(
    data: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    service = AuthService(db)
    await service.reset_password(data.email, data.otp, data.new_password)
    return {"status": "success", "message": "Password successfully reset."}

@auth_router.delete("/me")
async def delete_account(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Deletes the current user's account and all associated documents, chunks, and embeddings entirely.
    """
    # 1. Fetch all user documents to wipe physical files off the remote bucket
    result = await db.execute(select(DocumentMetadata).where(DocumentMetadata.email == current_user.email))
    docs = result.scalars().all()
    storage = SupabaseStorageService()
    
    for doc in docs:
        try:
            storage.delete(doc.storage_location)
        except Exception as e:
            print(f"Failed to delete physical remote file {doc.storage_location}: {e}")
                
    # 2. Database Cascade Deletion
    # PostgreSQL handles the cascading hierarchy natively!
    # Deleting the user triggers deletion of documents_metadata -> documents_chunks -> document_embeddings
    await db.execute(delete(User).where(User.email == current_user.email))
    await db.commit()
    
    return {"status": "success", "message": "Account and all associated documents deleted successfully."}