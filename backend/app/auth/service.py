from app.auth.jwt import create_access_token
from app.auth.repository import UserRepository
from app.auth.schemas import LoginRequest, RegisterRequest, TokenResponse
from app.auth.security import hash_password, verify_password
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
import random
from datetime import datetime, timedelta, timezone
from app.auth.email_service import EmailService

class AuthService:
    def __init__(self,db:AsyncSession):
        self.repository = UserRepository(db)

    async def register(self, data: RegisterRequest):
        if await self.repository.get_by_email(data.email):
            raise HTTPException(status_code=409, detail="Email already exists")

        return await self.repository.create(
            name=data.name,
            email=data.email,
            password=hash_password(data.password),
        )

    async def login(self, data: LoginRequest):
        user = await self.repository.get_by_email(data.email)

        if not user or not verify_password(data.password, user.password):
            raise HTTPException(status_code=401, detail="Invalid email or password")

        return TokenResponse(access_token=create_access_token(str(user.id)))
        
    async def forgot_password(self, email: str):
        user = await self.repository.get_by_email(email)
        if not user:
            # Silently return so malicious actors cannot scrape valid emails!
            return

        # Generate 6 digit OTP and 7-minute expiration
        otp = str(random.randint(100000, 999999))
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=7)

        # Persist to database
        await self.repository.update(user, reset_otp=otp, reset_otp_expires_at=expires_at)

        # Push Email
        EmailService().send_otp(email, otp)

    async def verify_otp(self, email: str, otp: str):
        user = await self.repository.get_by_email(email)
        
        if not user or user.reset_otp != otp:
             raise HTTPException(status_code=400, detail="Invalid OTP provided.")
        
        # Verify timestamps inside UTC to strictly avoid timezone overlap bugs
        if not user.reset_otp_expires_at or user.reset_otp_expires_at < datetime.now(timezone.utc):
             raise HTTPException(status_code=400, detail="OTP has expired. Please request a new one.")
        
        return True

    async def reset_password(self, email: str, otp: str, new_password: str):
        # Strict dual verification pipeline (Re-verify the OTP before applying!)
        await self.verify_otp(email, otp)
        
        user = await self.repository.get_by_email(email)
        
        # Atomically apply new password hash and completely wipe the OTP metadata
        await self.repository.update(
            user, 
            password=hash_password(new_password),
            reset_otp=None,
            reset_otp_expires_at=None
        )