from auth.api import AuthAPI
from auth.schemas import LoginRequest, RegisterRequest, TokenResponse, UserResponse
from config.session import SessionManager


class AuthService:

    def __init__(self, api: AuthAPI, session_manager: SessionManager):
        self.api = api
        self.session_manager = session_manager

    def login(self, request: LoginRequest) -> TokenResponse:
        token_response = self.api.login(request)
        self.session_manager.login(access_token=token_response.access_token)
        return token_response

    def get_current_user(self) -> UserResponse:
        """Fetch real user from /auth/me (uses JWT already stored in session)."""
        user = self.api.get_current_user()
        self.session_manager.set_user(user)
        return user

    def register(self, request: RegisterRequest) -> UserResponse:
        return self.api.register(request)

    def logout(self) -> None:
        self.session_manager.logout()