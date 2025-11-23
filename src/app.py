import streamlit as st
import os
from core import config
from models.category_models import CategoryModel
from models.transaction_models import TransactionModel
from views.dashboard_view import _render_dashboard, _render_dashboard_func_panel
from views.categories_view import _render_categories, _render_dialog, _render_category_func_panel
from views.transactions_view import _render_transactions, _render_trans_func_panel
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

# set trang hiện tại
def set_page(page_name):
    page_name = st.session_state["current_page"] 
    return page_name # cập nhập trạng thái hiện tại khi nút được bấm

if 'current_page' not in st.session_state:
    st.session_state['current_page'] = 'Dashboard' # Mặc định hiển thị Dashboarddef set_page(page_name):

# ======== STREAMLIT SETUP =========
# Set page config phải đặt đầu tiên, nếu nằm sau st nào khác thì sẽ báo lỗi
st.set_page_config(
    page_title=APP_NAME,
    layout="wide",
    page_icon="assets/icon.png")

# Chỉnh màu cho cục bộ toàn app (màu xám)
st.markdown("""<style>.stApp {background-color: #EEEEEE;}</style>""", unsafe_allow_html=True)

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
        "container": {"padding": "5 !important", "background-color": "#FFFFFF", "border-radius": "15px"},
    }

# ======== STREAMLIT RENDER =========
with stylable_container(key="menu_box", css_styles=menu_style):
    top_left, top_mid, top_right = st.columns([0.05, 0.8, 0.6])

    # Menu
    with top_left:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        logo_img_path = os.path.join(current_dir, '..', 'assets', 'logo.png')
        st.image(logo_img_path, width=45)

    with top_mid:
        st.session_state['current_page'] = option_menu(
            menu_title="",  # tiêu đề menu
            options=["Dashboard", "Categories", "Transactions", "Goals"],
            icons=["bar-chart", "list-check", "arrow-left-right", "flag"],  # Tên icon từ Bootstrap Icons
            menu_icon="cast",  # Icon cho menu (nếu có tiêu đề)
            default_index=0,
            orientation="horizontal",  # horizontal hoặc "vertical", set kiểu để menu
            styles=custom_styles,
            )   

    # Functions field
    with top_right:
        if st.session_state['current_page'] == "Dashboard":
            _render_dashboard_func_panel()
        elif st.session_state['current_page'] == "Categories":
            _render_category_func_panel()  
        elif st.session_state['current_page'] == "Transactions":
            _render_trans_func_panel()
    
    st.markdown("""<hr style="margin: 0px 0; border: none; border-top: 1px solid #333; opacity: 0.3;">""", unsafe_allow_html=True)

    if st.session_state['current_page'] == "Dashboard":
        _render_dashboard()
    elif st.session_state['current_page'] == "Categories":
        _render_categories() # trong đây chứa dialog confirm delete
        _render_dialog() # dialog chứa success và failed, chạy sau dialog confirm delete
    elif st.session_state['current_page'] == "Transactions":
        _render_transactions()