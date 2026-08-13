import streamlit as st
from pydantic import ValidationError
from requests import HTTPError

from auth.schemas import LoginRequest, RegisterRequest
from auth.service import AuthService


class AuthView:

    def __init__(self, auth_service: AuthService):
        self.auth_service = auth_service

    # ── Public pages ──────────────────────────────────────────────────────────

    def login(self) -> None:
        _, col, _ = st.columns([1, 1.2, 1])
        with col:
            st.markdown("## 🤖 AI Support")
            st.markdown("#### Welcome back — sign in to continue.")
            st.divider()

            with st.form("login_form"):
                email = st.text_input("Email", placeholder="you@example.com")
                password = st.text_input("Password", type="password", placeholder="••••••••")
                submitted = st.form_submit_button("Sign In", use_container_width=True, type="primary")

            if submitted:
                self._handle_login(email, password)

            st.divider()
            st.markdown("Don't have an account?")
            if st.button("Create Account →", use_container_width=True):
                st.session_state["auth_page"] = "signup"
                st.rerun()

    def signup(self) -> None:
        _, col, _ = st.columns([1, 1.2, 1])
        with col:
            st.markdown("## 🤖 AI Support")
            st.markdown("#### Create your account.")
            st.divider()

            with st.form("signup_form"):
                name = st.text_input("Full Name", placeholder="John Doe")
                email = st.text_input("Email", placeholder="you@example.com")
                password = st.text_input("Password", type="password", placeholder="••••••••")
                confirm = st.text_input("Confirm Password", type="password", placeholder="••••••••")
                submitted = st.form_submit_button("Create Account", use_container_width=True, type="primary")

            if submitted:
                self._handle_signup(name, email, password, confirm)

            st.divider()
            st.markdown("Already have an account?")
            if st.button("Back to Sign In →", use_container_width=True):
                st.session_state["auth_page"] = "login"
                st.rerun()

    # ── Handlers ──────────────────────────────────────────────────────────────

    def _handle_login(self, email: str, password: str) -> None:
        try:
            self.auth_service.login(LoginRequest(email=email, password=password))
            self.auth_service.get_current_user()
            st.session_state["auth_page"] = "dashboard"
            st.rerun()
        except ValidationError as e:
            self._show_validation_error(e)
        except HTTPError as e:
            self._show_http_error(e)
        except Exception:
            st.error("Something went wrong. Please try again.")

    def _handle_signup(self, name: str, email: str, password: str, confirm: str) -> None:
        if password != confirm:
            st.error("Passwords do not match.")
            return
        try:
            self.auth_service.register(RegisterRequest(name=name, email=email, password=password))
            st.success("✅ Account created! Please sign in.")
            st.session_state["auth_page"] = "login"
            st.rerun()
        except ValidationError as e:
            self._show_validation_error(e)
        except HTTPError as e:
            self._show_http_error(e)
        except Exception:
            st.error("Something went wrong. Please try again.")

    # ── Error helpers ─────────────────────────────────────────────────────────

    @staticmethod
    def _show_validation_error(error: ValidationError) -> None:
        for e in error.errors():
            st.error(e.get("msg", "Invalid input."))

    @staticmethod
    def _show_http_error(error: HTTPError) -> None:
        r = error.response
        if r is None:
            st.error("Unable to connect to the server.")
            return
        messages = {
            401: "Invalid email or password.",
            409: "An account with this email already exists.",
            422: "Please check the information you entered.",
        }
        st.error(messages.get(r.status_code, "Request failed. Please try again." if r.status_code < 500 else "Server error. Please try again later."))