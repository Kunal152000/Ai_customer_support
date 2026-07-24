from app.auth.jwt import create_access_token
from app.auth.repository import UserRepository
from app.auth.schemas import LoginRequest, RegisterRequest, TokenResponse
from app.auth.security import hash_password, verify_password
from sqlalchemy.ext.asyncio import AsyncSession

class AuthService:
    def __init__(self,db:AsyncSession):
        self.repository = UserRepository(db)

    async def register(self, data: RegisterRequest):
        if await self.repository.get_by_email(data.email):
            raise ValueError("Email already exists")

        return await self.repository.create(
            name=data.name,
            email=data.email,
            password=hash_password(data.password),
        )

    async def login(self, data: LoginRequest):
        user = await self.repository.get_by_email(data.email)

        if not user or not verify_password(data.password, user.password):
            raise ValueError("Invalid email or password")

        return TokenResponse(access_token=create_access_token(str(user.id)))
        