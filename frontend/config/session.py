import streamlit as st

class SessionManager:

    ACCESS_TOKEN = "access_token"
    USER = "user"
    AUTHENTICATED = "authenticated"

    def initialize(self) -> None:
        defaults = {
            self.ACCESS_TOKEN: None,
            self.USER: None,
            self.AUTHENTICATED: False,
        }

        for key, value in defaults.items():
            st.session_state.setdefault(key, value)

    def login(self, access_token: str) -> None:
        st.session_state[self.ACCESS_TOKEN] = access_token
        st.session_state[self.AUTHENTICATED] = True

    def set_user(self, user) -> None:
        st.session_state[self.USER] = user

    def logout(self) -> None:
        st.session_state[self.ACCESS_TOKEN] = None
        st.session_state[self.USER] = None
        st.session_state[self.AUTHENTICATED] = False

    def is_authenticated(self) -> bool:
        return st.session_state[self.AUTHENTICATED]

    def get_token(self) -> str | None:
        return st.session_state[self.ACCESS_TOKEN]

    def get_user(self) -> dict | None:
        return st.session_state[self.USER]