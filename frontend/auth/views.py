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
                
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Forgot Password?", use_container_width=True):
                    st.session_state["auth_page"] = "forgot_password"
                    st.session_state["reset_stage"] = "email"
                    st.rerun()

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

    def forgot_password(self) -> None:
        from auth.schemas import ForgotPasswordRequest, VerifyOTPRequest, ResetPasswordRequest
        _, col, _ = st.columns([1, 1.2, 1])
        with col:
            st.markdown("## 🤖 AI Support")
            st.markdown("#### Reset Password")
            st.divider()

            if "reset_stage" not in st.session_state:
                st.session_state.reset_stage = "email"

            if st.session_state.reset_stage == "email":
                with st.form("forgot_email_form"):
                    email = st.text_input("Enter your email address")
                    submitted = st.form_submit_button("Send OTP", use_container_width=True, type="primary")

                if submitted:
                    if not email:
                        st.error("Please enter an email address.")
                    else:
                        st.session_state.reset_email = email
                        try:
                            self.auth_service.forgot_password(ForgotPasswordRequest(email=email))
                            st.session_state.reset_stage = "otp"
                            st.rerun()
                        except Exception as e:
                            self._handle_generic_error(e)

            elif st.session_state.reset_stage == "otp":
                st.info(f"An OTP was sent to **{st.session_state.reset_email}** (valid for 7 minutes).")
                with st.form("forgot_otp_form"):
                    otp = st.text_input("Enter 6-digit OTP", max_chars=6)
                    submitted = st.form_submit_button("Verify OTP", use_container_width=True, type="primary")

                if submitted:
                    if not otp:
                        st.error("Please enter the OTP.")
                    else:
                        st.session_state.reset_otp = otp
                        try:
                            self.auth_service.verify_otp(VerifyOTPRequest(email=st.session_state.reset_email, otp=otp))
                            st.session_state.reset_stage = "new_password"
                            st.rerun()
                        except Exception as e:
                            self._handle_generic_error(e)

            elif st.session_state.reset_stage == "new_password":
                st.success("OTP Verified! You may now set a new password.")
                with st.form("forgot_new_pw_form"):
                    new_pw = st.text_input("New Password", type="password")
                    confirm_pw = st.text_input("Confirm New Password", type="password")
                    submitted = st.form_submit_button("Reset Password", use_container_width=True, type="primary")
                
                if submitted:
                    if new_pw != confirm_pw:
                        st.error("Passwords do not match!")
                    elif not new_pw:
                        st.error("Password cannot be empty.")
                    else:
                        try:
                            req = ResetPasswordRequest(
                                email=st.session_state.reset_email, 
                                otp=st.session_state.reset_otp, 
                                new_password=new_pw
                            )
                            self.auth_service.reset_password(req)
                            st.success("Password reset successfully! Please sign in.")
                            st.session_state["auth_page"] = "login"
                            st.session_state.reset_stage = "email"
                            st.rerun()
                        except Exception as e:
                            self._handle_generic_error(e)

            st.divider()
            if st.button("Back to Sign In →", use_container_width=True):
                st.session_state["auth_page"] = "login"
                st.session_state.reset_stage = "email"
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
        
        # Try to parse FastAPI detail string if present
        try:
            detail = r.json().get("detail")
            if detail:
                st.error(detail)
                return
        except:
            pass

        messages = {
            401: "Invalid email or password.",
            409: "An account with this email already exists.",
            422: "Please check the information you entered.",
        }
        st.error(messages.get(r.status_code, "Request failed. Please try again." if r.status_code < 500 else "Server error. Please try again later."))

    def _handle_generic_error(self, e: Exception) -> None:
        if isinstance(e, HTTPError):
            self._show_http_error(e)
        elif isinstance(e, ValidationError):
            self._show_validation_error(e)
        else:
            st.error("Something went wrong. Please try again.")