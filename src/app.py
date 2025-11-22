import streamlit as st
import os
from pathlib import Path
from core import config
from models.category_models import CategoryModel
from models.transaction_models import TransactionModel
from views.dashboard_view import show_dashboard
from views.transactions_view import show_transactions
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

def load_css(file_name):
    css_path = Path(__file__).parent.parent / "assets" /file_name # truy từ folder root xuống
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# set trang hiện tại
def set_page(page_name):
    page_name = st.session_state["current_page"] 
    return page_name # cập nhập trạng thái hiện tại khi nút được bấm

if 'current_page' not in st.session_state:
    st.session_state['current_page'] = 'Dashboard' # Mặc định hiển thị Dashboarddef set_page(page_name):

cate = init_category_models()
trans = init_transaction_models()
user = None

# ======== STREAMLIT SETUP =========
# Set page config phải đặt đầu tiên, nếu nằm sau st nào khác thì sẽ báo lỗi
st.set_page_config(
    page_title=APP_NAME,
    layout="wide",
    page_icon="assets/icon.png",
)

# Chỉnh màu cho cục bộ toàn app (màu xám)
st.markdown("""<style>.stApp {background-color: #DCDCDC;}</style>""", unsafe_allow_html=True)
st.markdown("""
<style>
[data-testid="stAppViewContainer"] > .main {{
background-image: url("https://images.unsplash.com/photo-1501426026826-31c667bdf23d");
background-size: 180%;
background-position: top left;
background-repeat: no-repeat;
background-attachment: local;
}}

[data-testid="stSidebar"] > div:first-child {{
background-image: url("data:image/png;base64,{img}");
background-position: center; 
background-repeat: no-repeat;
background-attachment: fixed;
}}

[data-testid="stHeader"] {{
background: rgba(0,0,0,0);
}}

[data-testid="stToolbar"] {{
right: 2rem;
}}
</style>
""", unsafe_allow_html=True)

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

# Tùy chỉnh cho option_menu
custom_styles = {
        "container": {"padding": "0!important", "background-color": "#FFFFFF", "border-radius": "15px"},
    }

# ======== STREAMLIT SHOW =========
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
    current_page = st.session_state['current_page']
    if current_page == "Dashboard":
        show_dashboard()
        #st.write("Dashboard")
    if current_page == "Transactions":
        show_transactions()
        #st.write("Transactions")