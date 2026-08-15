import streamlit as st
from streamlit_cookies_controller import CookieController

_COOKIE_KEY = "ai_support_token"
_MAX_AGE = 60 * 60 * 24 * 7  # 7 days in seconds


class SessionManager:

    ACCESS_TOKEN = "access_token"
    USER = "user"
    AUTHENTICATED = "authenticated"

    def __init__(self):
        pass

    @property
    def _cookies(self) -> CookieController:
        return st.session_state["_cookie_ctrl"]

    def initialize(self) -> None:
        """Bootstrap session state; if a cookie exists, restore the token."""
        # MUST be evaluated every single script rerun so the component iframe renders
        # but MUST be stored in session_state to avoid global variable leak!
        st.session_state["_cookie_ctrl"] = CookieController(key="auth_cookie_ctrl")

        defaults = {
            self.ACCESS_TOKEN: None,
            self.USER: None,
            self.AUTHENTICATED: False,
        }
        for key, value in defaults.items():
            st.session_state.setdefault(key, value)

        # Restore from cookie if session state is empty (after a page refresh)
        if not st.session_state[self.AUTHENTICATED]:
            token = self._cookies.get(_COOKIE_KEY)
            if token:
                st.session_state[self.ACCESS_TOKEN] = token
                st.session_state[self.AUTHENTICATED] = True

    def login(self, access_token: str) -> None:
        st.session_state[self.ACCESS_TOKEN] = access_token
        st.session_state[self.AUTHENTICATED] = True
        # Persist token in browser cookie for 7 days
        self._cookies.set(_COOKIE_KEY, access_token, max_age=_MAX_AGE)

    def set_user(self, user) -> None:
        st.session_state[self.USER] = user

    def logout(self) -> None:
        st.session_state[self.ACCESS_TOKEN] = None
        st.session_state[self.USER] = None
        st.session_state[self.AUTHENTICATED] = False
        # Remove the cookie so the user isn't auto-logged back in
        self._cookies.remove(_COOKIE_KEY)

    def is_authenticated(self) -> bool:
        return st.session_state[self.AUTHENTICATED]

    def get_token(self) -> str | None:
        return st.session_state[self.ACCESS_TOKEN]

    def get_user(self) -> dict | None:
        return st.session_state[self.USER]