from requests import HTTPError

from auth.api import AuthAPI
from auth.schemas import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from config.session import SessionManager


class AuthService:

    def __init__(
        self,
        api: AuthAPI,
        session_manager: SessionManager,
    ):
        self.api = api
        self.session_manager = session_manager

    def login(self, request: LoginRequest) -> TokenResponse:
        """
        Authenticate the user and store the returned access token.
        """

        token_response = self.api.login(request)

        self.session_manager.login(
            access_token=token_response.access_token
        )

        return token_response

    def register(self, request: RegisterRequest) -> UserResponse:
        """
        Register a new user.
        """

        return self.api.register(request)

    def get_current_user(self) -> UserResponse:
        """
        Fetch the currently authenticated user and
        store it in the session.
        """

        user_response = self.api.get_current_user()

        self.session_manager.set_user(user_response)

        return user_response

    def logout(self) -> None:
        """
        Clear the user's authentication session.
        """

        self.session_manager.logout()