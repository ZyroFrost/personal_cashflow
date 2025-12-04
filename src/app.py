import streamlit as st
import io, base64, time # chuyển đổi Image to base64 bỏ vào Icon button
from PIL import Image # đọc image từa folder assets
from streamlit_option_menu import option_menu # thư viện mở rộng của streamlit để add icon với css

from models.category_model import CategoryModel
from models.transaction_model import TransactionModel
from models.user_model import UserModel
from analytics.analyzer import FinanceAnalyzer
from analytics.visualizer import FinanceVisualizer

from assets.styles import set_global_css, google_icon_css, option_menu_css, transaction_expander_css
from views.dashboard_view import render_dashboard
from views.categories_view import render_categories
from views.transactions_view import render_transactions
from views.settings_view import render_settings

# ======== CONFIG =========
@st.cache_resource 
def init_models():
    return {
        "category": CategoryModel(),
        "transaction": TransactionModel(),
        "user": UserModel(),
        "visualizer": FinanceVisualizer(),
    }

# init models
if "models" not in st.session_state or st.session_state['models'] is None:
    # initialize models
    st.session_state['models'] = init_models()
models = st.session_state['models']

# check models init second time
if not all(key in models for key in ['category', 'transaction', 'user']):
    st.session_state['models'] = init_models()
    models = st.session_state['models']

# current page
def set_page(page_name):
    page_name = st.session_state["current_page"] 
    return page_name

# ======== STYLES SETUP =========
set_global_css()
transaction_expander_css() # phải dùng cục bộ 1 lần, ko dùng bên view

# ========= DIALOGS & USER =========
# Login screen
@st.dialog(" ", dismissible=False, width = "small") # dismissible=False ẩn nút x đóng dialog
def login_screen():
    img = Image.open("src/assets/google_logo.png")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    btn_b64 = base64.b64encode(buf.getvalue()).decode()

    # load css cho icon
    google_icon_css()

    with st.container(horizontal_alignment="center"):
        st.image("src/assets/logo.png", width=300)
        st.markdown("<h2 style='text-align: center;'>Login to your account</h2>", unsafe_allow_html=True)
        st.button(f'![icon](data:image/png;base64,{btn_b64})  Log in with Google', on_click=st.login, use_container_width=True)

# Confirm deactivated account dialog
@st.dialog("Account Deactivated", width="small")
def deactivated_account_dialog():
    st.write("This account has been deactivated. Please contact Customer Support to reactivate your account.")
    st.write("Email: zyrofrost@gmail.com")
    st.button("Log out", on_click=st.logout, use_container_width=True)

# Creating account progress dialog
@st.dialog("First time login, we are creating your account", dismissible=False, width="small")
def creating_account_dialog():
    with st.spinner("Creating your account..."):
        time.sleep(4)
        user_model.create_user(st.user.email)
        st.rerun()
    
# ======== USER AUTH =========
if not st.user.is_logged_in:
    login_screen()
    st.stop() # do not render while not logged in

# After login, check user in database
user_model: UserModel = models['user']
user = user_model.get_user_by_email(st.user.email) # get user document to check is_activate field
user_id = user.get("_id")

# Get user_id for all models
models['category'].set_user_id(user_id)
models['transaction'].set_user_id(user_id)

# If user not exist, show creating account spinner dialog and create account
if user is None:
    creating_account_dialog()
    st.stop()

# If user is deactivated, show dialog and stop rendering
if user.get("is_activate") is False:
    deactivated_account_dialog()
    st.stop()

# ======== SIDEBAR =========
with st.sidebar:
    with st.container(horizontal=True, horizontal_alignment="center", vertical_alignment="top"):
        
        # User info
        st.image(f"{st.user.picture}", width=120)
        st.markdown(
            f"""
            <div style="text-align:center;">
                <h4>Welcome {st.user.name}</h4>
                <p>Email: {st.user.email}</p>
                <!-- <p>ID: {user.get("_id")}</p> freeze this, use for debug-->
            </div>
            """,
            unsafe_allow_html=True
        )

        # Menu
        st.session_state['current_page'] = option_menu(
            menu_title="MENU",  # tiêu đề menu
            options=["Dashboard", "Categories", "Transactions", "Budgets", "Goals", "---", "Settings", "Log out"],  # tên các trang
            icons=["bar-chart", "list-check", "arrow-left-right", "wallet", "flag", "---", "gear", "box-arrow-right"],  # Tên icon từ Bootstrap Icons
            menu_icon="cast",  # Icon cho menu (nếu có tiêu đề)
            default_index=0,
            orientation="vertical",  # horizontal hoặc "vertical", set kiểu để menu
            styles=option_menu_css()
            )

# ======== RENDER PAGE =========
if st.session_state['current_page'] == "Dashboard":
    analyzer_model = FinanceAnalyzer(models['transaction'])
    render_dashboard(analyzer_model=analyzer_model, transaction_model=models['transaction'], visualizer_model=models['visualizer'])
elif st.session_state['current_page'] == "Categories":
    render_categories()
elif st.session_state['current_page'] == "Transactions":
    render_transactions()
elif st.session_state['current_page'] == "Settings":
    render_settings()
elif st.session_state['current_page'] == "Log out":
    st.logout()