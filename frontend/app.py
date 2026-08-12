import streamlit as st

from auth.views import AuthView
from config.session import SessionManager
from core.container import Container


# ---------------------------------------------------------
# Streamlit Configuration
# ---------------------------------------------------------

st.set_page_config(
    page_title="AI Support",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------------------------------------------------------
# Dependency Container
# ---------------------------------------------------------

@st.cache_resource
def get_container() -> Container:
    return Container()


# ---------------------------------------------------------
# Application Initialization
# ---------------------------------------------------------

container = get_container()

session_manager = container.session_manager
session_manager.initialize()

auth_view = AuthView(
    auth_service=container.auth_service
)


# ---------------------------------------------------------
# Authentication Routing
# ---------------------------------------------------------

if not session_manager.is_authenticated():

    if "auth_page" not in st.session_state:
        st.session_state["auth_page"] = "login"

    if st.session_state["auth_page"] == "signup":
        auth_view.signup()

    else:
        auth_view.login()


# ---------------------------------------------------------
# Authenticated Application
# ---------------------------------------------------------

else:

    user = session_manager.get_user()

    st.title("AI Support")

    if user:
        st.write(
            f"Welcome, {user.name}!"
        )
    else:
        st.write("Welcome!")

    st.success(
        "You are successfully authenticated."
    )

    if st.button("Logout"):
        container.auth_service.logout()
        st.session_state["auth_page"] = "login"
        st.rerun()