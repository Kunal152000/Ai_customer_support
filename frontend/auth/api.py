from auth.schemas import LoginRequest, RegisterRequest,TokenResponse,UserResponse
from utils.api_client import APIClient


class AuthAPI:
    """
    Responsible only for communicating with the backend
    Authentication APIs.
    """

    def __init__(self, client: APIClient):
        self.client = client

    def login(self, request: LoginRequest) -> TokenResponse:
        response = self.client.post(
            "/auth/login",
            json=request.model_dump()
        )

        return TokenResponse.model_validate(response)

    def register(self, request: RegisterRequest) -> UserResponse:
        response = self.client.post(
            "/auth/register",
            json=request.model_dump()
        )

        return UserResponse.model_validate(response)

    def get_current_user(self) -> dict:
        """
        Fetch the currently authenticated user.
        """

        return self.client.get(
            endpoint="/auth/me"
        )

    def logout(self) -> None:
        """
        Placeholder.

        Backend logout generally isn't required for JWT based
        authentication since logout is handled by deleting the
        token from the client.
        """

        return