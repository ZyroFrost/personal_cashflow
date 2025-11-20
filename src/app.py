import streamlit as st
import os
from datetime import datetime
from pathlib import Path
from core import config
from models.category_models import CategoryModel
from models.transaction_models import TransactionModel
from views import dashboard_view, transaction_view
from streamlit_extras.stylable_container import stylable_container # thư viện mở rộng của streamlit để add container với css
from streamlit_option_menu import option_menu # thư viện mở rộng của streamlit để add icon với css

# ======== CONFIG =========
APP_NAME = config.APP_NAME

# Lần sau rerun → Streamlit không tạo lại DatabaseManager Nó lấy resource đã cache và dùng lại → để tối ưu tốc độ, giảm lag
@st.cache_resource 
def init_category_models():
    return CategoryModel()

@st.cache_resource # tạo trước def để chỉ tạo 1 lần (lần sau gọi trong cache)
def init_transaction_models():
    return TransactionModel()

def show_dashboard():
    return dashboard_view.show_dashboard()

def load_css(file_name):
    css_path = Path(__file__).parent.parent / "assets" /file_name # truy từ folder root xuống
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def set_page(page_name):
    st.session_state["current_page"] = page_name # cập nhập trạng thái hiện tại khi nút được bấm

if 'current_page' not in st.session_state:
    st.session_state['current_page'] = 'Dashboard' # Mặc định hiển thị Dashboarddef set_page(page_name):

cate = init_category_models()
trans = init_transaction_models()
user = None

# ======== MAIN PAGE =========
# Set page config phải đặt đầu tiên, nếu nằm sau st nào khác thì sẽ báo lỗi
st.set_page_config(
    page_title=APP_NAME,
    layout="wide",
    page_icon="assets/icon.png",
)

# Chỉnh màu cho cục bộ toàn app (màu xám)
st.markdown("""<style>.stApp {background-color: #DCDCDC;}</style>""", unsafe_allow_html=True)
load_css("style.css")

# tùy chỉnh cho phần menu
menu_style = """
    {
        background-color: white;
        border-radius: 12px;
        padding: 15px 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        min-height: 80vh !important;
        align-items: center; /* Canh giữa dọc */
    }"""

# tùy chỉnh cho phần header
header_style = """
    {
        background-color: white;
        border-radius: 12px;
        padding: 15px 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        min-height: 8vh !important;
        align-items: center; /* Canh giữa dọc */
    }"""

# tùy chỉnh cho phần main
body_style = """
    {
        background-color: white;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        min-height: 70.5vh !important;
        overflow-y: auto; /* Nếu nội dung dài thì cuộn bên trong khung */
    }"""

# Tùy chỉnh cho option_menu
custom_styles = {
        "container": {"padding": "0!important", "background-color": "#FFFFFF", "border-radius": "15px"},
    }

# = TOP =
# User info
left, right = st.columns([1, 5], gap="small", vertical_alignment="center")
with left:
    with stylable_container(key="header_user", css_styles=menu_style):
        user_left, user_right = st.columns([1, 3], gap="small", vertical_alignment="center")
        with user_left:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            user_img_path = os.path.join(current_dir, '..', 'assets', 'user.png')
            st.image(user_img_path, width=40)
        with user_right:
            user_name = "User name"
            st.markdown(f"""
            <div style="line-height: 1.1;margin: 0; padding: 0; display: flex; flex-direction: column; justify-content: center; transform: translateY(-2px);">
                <span style="color: gray; font-size: 12px; margin: 0; padding: 0; line-height: 1.1;">Welcome,</span>
                <span style="font-weight: bold; font-size: 16px; margin: 0; padding: 0; line-height: 1.1;">{user_name}</span>
            </div>""", unsafe_allow_html=True)
        st.divider()

        # Menu
        st.session_state['current_page'] = option_menu(
            menu_title="Menu",  # tiêu đề menu
            options=["Dashboard", "Transactions", "Goals", "---", "Settings", "About", "---", "Register"],
            icons=["bar-chart", "arrow-left-right", "flag", "---", "gear", "info-circle", "---", "person"],  # Tên icon từ Bootstrap Icons
            menu_icon="cast",  # Icon cho menu (nếu có tiêu đề)
            default_index=0,
            orientation="vertical",  # hoặc "vertical", set kiểu để menu
            styles=custom_styles,
    )   

# Functions field
with right:
    with stylable_container(key="filter_box", css_styles=header_style):
        header_left, header_right = st.columns([1, 3], gap="small", vertical_alignment="center")
        current_page = st.session_state['current_page']

        # Display main name
        with header_left:
            if current_page == "Dashboard":
                st.subheader("Dashboard")
            if current_page == "Transactions":
                st.subheader("Transactions")
            if current_page == "Goals":
                st.subheader("Goals")
            if current_page == "Register":
                st.subheader("Register")
            if current_page == "Settings":
                st.subheader("Settings")
            if current_page == "About":
                st.subheader("About")
        
        # Functions field (search, filter, sort, add new)
        with header_right:
            cFilter, cSort, cSearch, col4 = st.columns(4, gap="small")
            with cFilter:
                st.button("Filter", use_container_width=True)
            with cSort:
                with st.popover("Sort", use_container_width=True): 
                    st.selectbox("Sort by", ["Date", "Amount", "Category"])
            with cSearch:
                with st.popover("Search", use_container_width=True):
                    st.text_input("Intput search", placeholder="Search")
            with col4:
                with st.popover("Add transaction", icon="➕", use_container_width=True):   
                    select_type = st.selectbox("Type", config.TRANSACTION_TYPES)
                    name = st.text_input("Name your transaction")

                    add_transaction = trans.add_transaction({"type": select_type, "name": name, "created_at": datetime.now(), "last_modified": datetime.now()})
                    st.button("Comfirm", icon="✔️", use_container_width=True, on_click=add_transaction)
        
    # Main display
    with stylable_container(key="main_box", css_styles=body_style):
        current_page = st.session_state['current_page']

        if current_page == "Dashboard":
            dashboard_view.show_dashboard()

        if current_page == "Transactions":
            st.subheader("Transactions")

        if current_page == "Goals":
            st.subheader("Goals")