import streamlit as st

from auth.views import AuthView
from chat.views import ChatView
from config.session import SessionManager
from core.container import Container


# ── Page config ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="AI Support",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Hide Streamlit defaults
hide_streamlit_style = """
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


# ── Bootstrap (cached singleton) ──────────────────────────────────────────────

@st.cache_resource
def get_container() -> Container:
    return Container()


container = get_container()
session_manager = container.session_manager
session_manager.initialize()

auth_view = AuthView(auth_service=container.auth_service)


# ── Routing ───────────────────────────────────────────────────────────────────

if not session_manager.is_authenticated():
    if "auth_page" not in st.session_state:
        st.session_state["auth_page"] = "login"

    if st.session_state["auth_page"] == "signup":
        auth_view.signup()
    elif st.session_state["auth_page"] == "forgot_password":
        auth_view.forgot_password()
    else:
        auth_view.login()

else:
    user = session_manager.get_user()
    # On a hard page refresh the cookie restores the token but user is lost from memory.
    # Silently re-fetch the user from the backend so the chat page renders correctly.
    if user is None:
        try:
            user = container.auth_service.get_current_user()
        except Exception:
            # Token is expired or invalid — force logout and back to login page.
            session_manager.logout()
            st.rerun()

    chat_view = ChatView(chat_service=container.chat_service, auth_service=container.auth_service, user=user)
    chat_view.render()