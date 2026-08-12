import streamlit as st
from pydantic import ValidationError
from requests import HTTPError

from auth.schemas import LoginRequest, RegisterRequest
from auth.service import AuthService


class AuthView:

    def __init__(self, auth_service: AuthService):
        self.auth_service = auth_service

    def login(self) -> None:
        st.title("Welcome Back")

        st.write("Sign in to your AI Support account.")

        with st.form("login_form"):

            email = st.text_input(
                "Email",
                placeholder="Enter your email",
            )

            password = st.text_input(
                "Password",
                type="password",
                placeholder="Enter your password",
            )

            submitted = st.form_submit_button(
                "Login",
                use_container_width=True,
            )

        if submitted:
            self._handle_login(
                email=email,
                password=password,
            )

        st.divider()

        st.write("Don't have an account?")

        if st.button(
            "Create Account",
            use_container_width=True,
        ):
            st.session_state["auth_page"] = "signup"
            st.rerun()

    def signup(self) -> None:
        st.title("Create Account")

        st.write("Create your AI Support account.")

        with st.form("signup_form"):

            name = st.text_input(
                "Name",
                placeholder="Enter your name",
            )

            email = st.text_input(
                "Email",
                placeholder="Enter your email",
            )

            password = st.text_input(
                "Password",
                type="password",
                placeholder="Enter your password",
            )

            confirm_password = st.text_input(
                "Confirm Password",
                type="password",
                placeholder="Re-enter your password",
            )

            submitted = st.form_submit_button(
                "Create Account",
                use_container_width=True,
            )

        if submitted:
            self._handle_signup(
                name=name,
                email=email,
                password=password,
                confirm_password=confirm_password,
            )

        st.divider()

        st.write("Already have an account?")

        if st.button(
            "Back to Login",
            use_container_width=True,
        ):
            st.session_state["auth_page"] = "login"
            st.rerun()

    def _handle_login(
        self,
        email: str,
        password: str,
    ) -> None:

        try:
            login_request = LoginRequest(
                email=email,
                password=password,
            )

            self.auth_service.login(login_request)

            # Fetch and store the authenticated user
            self.auth_service.get_current_user()

            st.success("Login successful!")

            st.session_state["auth_page"] = "dashboard"

            st.rerun()

        except ValidationError as exc:
            self._display_validation_error(exc)

        except HTTPError as exc:
            self._display_api_error(exc)

        except Exception:
            st.error(
                "Something went wrong. Please try again."
            )

    def _handle_signup(
        self,
        name: str,
        email: str,
        password: str,
        confirm_password: str,
    ) -> None:

        if password != confirm_password:
            st.error("Passwords do not match.")
            return

        try:
            register_request = RegisterRequest(
                name=name,
                email=email,
                password=password,
            )

            self.auth_service.register(register_request)

            st.success(
                "Account created successfully. "
                "Please login."
            )

            st.session_state["auth_page"] = "login"

            st.rerun()

        except ValidationError as exc:
            self._display_validation_error(exc)

        except HTTPError as exc:
            self._display_api_error(exc)

        except Exception:
            st.error(
                "Something went wrong. Please try again."
            )

    @staticmethod
    def _display_validation_error(
        error: ValidationError,
    ) -> None:

        for validation_error in error.errors():
            message = validation_error.get(
                "msg",
                "Invalid input.",
            )

            st.error(message)

    @staticmethod
    def _display_api_error(
        error: HTTPError,
    ) -> None:

        response = error.response

        if response is None:
            st.error(
                "Unable to connect to the backend."
            )
            return

        if response.status_code == 401:
            st.error(
                "Invalid email or password."
            )

        elif response.status_code == 409:
            st.error(
                "An account with this email already exists."
            )

        elif response.status_code == 422:
            st.error(
                "Please check the information you entered."
            )

        elif response.status_code >= 500:
            st.error(
                "The server encountered an error. "
                "Please try again later."
            )

        else:
            st.error(
                "Request failed. Please try again."
            )