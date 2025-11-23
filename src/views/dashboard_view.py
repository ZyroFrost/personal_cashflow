from core import config
from models.category_models import CategoryModel
from models.transaction_models import TransactionModel  
from streamlit_extras.stylable_container import stylable_container # thư viện mở rộng của streamlit để add container với css
import streamlit as st
import pandas as pd
import numpy as np

# ======== CONFIG =========
@st.cache_resource 
def init_category_models():
    return CategoryModel()

def refresh_page():
    return st.rerun()

# Get list from db
type_list = ["All"] + config.TRANSACTION_TYPES.copy()
cate_income = ["All"] + [c["name"] for c in init_category_models().get_category_by_type("Income")] 
cate_expense = ["All"] +  [c["name"] for c in init_category_models().get_category_by_type("Expense")]
cate_full_list = (["All"] + [c["name"] for c in init_category_models().get_category_by_type("Income")] + 
                            [c["name"] for c in init_category_models().get_category_by_type("Expense")])
currency_list = ["All"] + list(config.CURRENCIES.keys())

def _render_sample_line_chart():
    st.markdown("**Trending**")
    
    dates = pd.date_range("2025-01-01", periods=10) # Tạo chuỗi ngày (Date)
    
    # Tạo dữ liệu chi tiêu (Amount) ngẫu nhiên
    data = {
        'Date': dates,
        # Sử dụng cumsum (tích lũy) để tạo xu hướng tăng/giảm cho chi tiêu
        'Daily_Expense': np.random.randint(10, 50, size=10),
        'Daily_Income': np.random.randint(40, 70, size=10)
    }
    
    df = pd.DataFrame(data)
    df = df.set_index('Date') # Đặt cột 'Date' làm index (tốt cho biểu đồ đường)

    #st.subheader("Dữ liệu 10 ngày gần nhất:")
    #st.dataframe(df)

    # 2. VẼ BIỂU ĐỒ (Sử dụng hàm st.line_chart())
    #st.markdown("---")
    st.caption("Biểu đồ thể hiện sự thay đổi giữa Thu nhập và Chi tiêu theo thời gian.")
    
    # Vẽ biểu đồ đường, Streamlit sẽ tự động dùng Index (Date) làm trục X
    st.line_chart(df) 
    
    # HOẶC bạn có thể chỉ định rõ ràng cột Y muốn vẽ:
    # st.line_chart(df['Daily_Expense'])

# ======== RENDER DASHBOARD ==========
def _render_dashboard_func_panel():
    _, cFilter = st.columns([1, 1])

    # Filter popover
    with cFilter:
        with st.popover("Filter", icon="🔎", use_container_width=True):    
            # Select type
            st.selectbox("↔️ Transaction Type", type_list, key="select_type1")

            # Select category
            if st.session_state.select_type1 == "Income":
                st.selectbox("📦 Category Name", cate_income, key="select_category1")         
            elif st.session_state.select_type1 == "Expense":     
                st.selectbox("📦 Category Name", cate_expense, key="select_category1")
            elif st.session_state.select_type1 == "All":
                st.selectbox("📦 Category Name", cate_full_list, key="select_category1")
            
            # Select date range
            st.select_slider("📅 Date Range Option", options=config.DEFAULT_TIME_FILTERS, key="date_range1")

            # Select currency
            st.selectbox("💰 Currency", currency_list, key="currency1")

            # Select amount
            min, max = st.columns(2)
            with min:
                st.number_input("🔽 Minimum Amount", min_value=0, value=0, key="min_amount1")
            with max:
                st.number_input("🔼 Maximum Amount", min_value=0, value=0, key="max_amount1")

def _render_dashboard():
    # Header

    _render_sample_line_chart()
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Income", "Rp 1,000,000", "Rp 500,000")
    with col2:
        st.metric("Total Expense", "Rp 1,000,000", "Rp 500,000")
    with col3:
        st.metric("Balance", "Rp 1,000,000", "Rp 500,000")