import requests

from config.settings import Settings
from config.session import SessionManager


class APIClient:

    def __init__(self, settings: Settings, session_manager: SessionManager):
        self.settings = settings
        self.session_manager = session_manager
        self.client = requests.Session()

    def _auth_header(self) -> dict:
        token = self.session_manager.get_token()
        return {"Authorization": f"Bearer {token}"} if token else {}

    def _headers(self) -> dict:
        return {"Content-Type": "application/json", **self._auth_header()}

    def get(self, endpoint: str, params=None):
        r = self.client.get(f"{self.settings.BACKEND_URL}{endpoint}", headers=self._headers(), params=params, timeout=self.settings.REQUEST_TIMEOUT)
        r.raise_for_status()
        return r.json()

    def post(self, endpoint: str, json=None):
        r = self.client.post(f"{self.settings.BACKEND_URL}{endpoint}", headers=self._headers(), json=json, timeout=self.settings.REQUEST_TIMEOUT)
        r.raise_for_status()
        return r.json()

    def put(self, endpoint: str, json=None):
        r = self.client.put(f"{self.settings.BACKEND_URL}{endpoint}", headers=self._headers(), json=json, timeout=self.settings.REQUEST_TIMEOUT)
        r.raise_for_status()
        return r.json()

    def delete(self, endpoint: str):
        r = self.client.delete(f"{self.settings.BACKEND_URL}{endpoint}", headers=self._headers(), timeout=self.settings.REQUEST_TIMEOUT)
        r.raise_for_status()
        return r.json()

    def form_post(self, endpoint: str, data: dict):
        """Send application/x-www-form-urlencoded (required for OAuth2 login)."""
        r = self.client.post(
            f"{self.settings.BACKEND_URL}{endpoint}",
            headers=self._auth_header(),
            data=data,
            timeout=self.settings.REQUEST_TIMEOUT,
        )
        r.raise_for_status()
        return r.json()

    def upload_file(self, endpoint: str, file_bytes: bytes, filename: str, extra_params: dict = None):
        """Send multipart/form-data — do NOT set Content-Type so requests adds the boundary."""
        r = self.client.post(
            url=f"{self.settings.BACKEND_URL}{endpoint}",
            headers=self._auth_header(),
            files={"file": (filename, file_bytes)},
            params=extra_params,
            timeout=self.settings.REQUEST_TIMEOUT,
        )
        r.raise_for_status()
        return r.json()