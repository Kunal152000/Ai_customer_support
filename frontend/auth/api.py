from auth.schemas import (
    LoginRequest, RegisterRequest, TokenResponse, UserResponse,
    ForgotPasswordRequest, VerifyOTPRequest, ResetPasswordRequest
)
from utils.api_client import APIClient


class AuthAPI:
    def __init__(self, client: APIClient):
        self.client = client

    def login(self, request: LoginRequest) -> TokenResponse:
        # Backend uses OAuth2PasswordRequestForm — needs form-data with 'username' field
        response = self.client.form_post(
            "/auth/login",
            data={"username": request.email, "password": request.password},
        )
        return TokenResponse.model_validate(response)

    def register(self, request: RegisterRequest) -> UserResponse:
        response = self.client.post("/auth/register", json=request.model_dump())
        return UserResponse.model_validate(response)
        
    def forgot_password(self, request: ForgotPasswordRequest) -> None:
        self.client.post("/auth/forgot-password", json=request.model_dump())

    def verify_otp(self, request: VerifyOTPRequest) -> None:
        self.client.post("/auth/verify-otp", json=request.model_dump())

    def reset_password(self, request: ResetPasswordRequest) -> None:
        self.client.post("/auth/reset-password", json=request.model_dump())

    def get_current_user(self) -> UserResponse:
        response = self.client.get("/auth/me")
        return UserResponse.model_validate(response)

    def delete_account(self) -> None:
        self.client.delete("/auth/me")

    def logout(self) -> None:
        return  # JWT logout is client-side only