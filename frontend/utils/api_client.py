import requests

from config.settings import Settings
from config.session import SessionManager


class APIClient:

    def __init__( self,   settings: Settings,
        session_manager: SessionManager,):
        self.settings = settings
        self.session_manager = session_manager
        self.client = requests.Session()

    def _headers(self) -> dict:
        headers = {
            "Content-Type": "application/json"
        }

        token = self.session_manager.get_token()

        if token:
            headers["Authorization"] = f"Bearer {token}"

        return headers

    def get(self, endpoint: str, params=None):
        response = self.client.get(
            url=f"{self.settings.BACKEND_URL}{endpoint}",
            headers=self._headers(),
            params=params,
            timeout=self.settings.REQUEST_TIMEOUT,
        )

        response.raise_for_status()
        return response.json()

    def post(self, endpoint: str, json=None):
        response = self.client.post(
            url=f"{self.settings.BACKEND_URL}{endpoint}",
            headers=self._headers(),
            json=json,
            timeout=self.settings.REQUEST_TIMEOUT,
        )

        response.raise_for_status()
        return response.json()

    def put(self, endpoint: str, json=None):
        response = self.client.put(
            url=f"{self.settings.BACKEND_URL}{endpoint}",
            headers=self._headers(),
            json=json,
            timeout=self.settings.REQUEST_TIMEOUT,
        )

        response.raise_for_status()
        return response.json()

    def delete(self, endpoint: str):
        response = self.client.delete(
            url=f"{self.settings.BACKEND_URL}{endpoint}",
            headers=self._headers(),
            timeout=self.settings.REQUEST_TIMEOUT,
        )

        response.raise_for_status()
        return response.json()