from auth.api import AuthAPI
from auth.service import AuthService
from config.session import SessionManager
from config.settings import settings
from utils.api_client import APIClient


class Container:

    def __init__(self):
        self.session_manager = SessionManager()

        self.api_client = APIClient(
            settings=settings,
            session_manager=self.session_manager,
        )

        self.auth_api = AuthAPI(
            client=self.api_client,
        )

        self.auth_service = AuthService(
            api=self.auth_api,
            session_manager=self.session_manager,
        )