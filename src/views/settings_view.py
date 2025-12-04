import streamlit as st
from models.user_model import UserModel
from utils import get_currencies_list
from assets.styles import container_page_css
from streamlit_extras.stylable_container import stylable_container

# Confirm deactivate account dialog
@st.dialog("Are you sure you want to deactivate your account?")
def confirm_deactivate_account_dialog(user_model):
    st.write("When account is deactivated, you only can login again after contacting support!")

    cCancel, cConfirm = st.columns([1, 1])
    if cCancel.button("❌ Cancel", use_container_width=True):
        st.rerun()

    if cConfirm.button("✅ Confirm", use_container_width=True):
        result = deactivate_user_account(user_model)
        return result

# Deactivate user account function
def deactivate_user_account(user_model: UserModel):
    try:
        mongo_user_id = user_model.login(st.user.email)
        user_model.deactivate(mongo_user_id)
        st.success("Your account has been deactivated.")
        st.logout()
    except Exception as e:
        st.error(f"Error during account deactivation: {e}")

# ======== STREAMLIT RENDER =========
def render_settings():
    models = st.session_state["models"]   # Lấy model từ App.py
    user_model = models["user"]

    with stylable_container(key="menu_box", css_styles=container_page_css()):

        # Header
        cHeader, _ = st.columns([1, 2], vertical_alignment="center")
        with cHeader:
            st.header("Settings")

        # Line
        st.markdown("""<hr style="margin: 10px 0; border: none; border-top: 2px solid #333; opacity: 0.3;">""", unsafe_allow_html=True)

        # Deactivate account
        st.subheader("Deactivate Account")
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write("Deactivating your account will remove all your data from our system. This action is irreversible.")
        with col2:
            if st.button("Deactivate Account", key="deactivate_account_button"):
                confirm_deactivate_account_dialog(user_model)
        st.divider()

        # Change currency
        col1, col2 = st.columns([1, 2])
        with col1:
            st.subheader("Change Currency")
        with col2:
            st.selectbox("Choose your currency", get_currencies_list(), key="choose_currency")
        st.divider()