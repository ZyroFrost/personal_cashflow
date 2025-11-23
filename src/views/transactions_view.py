from core import config
from models.category_models import CategoryModel
from models.transaction_models import TransactionModel
from datetime import datetime, time  
from streamlit_extras.stylable_container import stylable_container # thư viện mở rộng của streamlit để add container với css
import streamlit as st       

# ======== CONFIG =========
@st.cache_resource 
def init_category_models():
    return CategoryModel()

@st.cache_resource # tạo trước def để chỉ tạo 1 lần (lần sau gọi trong cache)
def init_transaction_models():
    return TransactionModel()

def refresh_page():
    return st.rerun()

def arrow(transaction_type):
    if transaction_type == "Income":
        return "▲"
    elif transaction_type == "Expense":
        return "▼"

# Get list from db
type_list = config.TRANSACTION_TYPES.copy()
cate_income = [c["name"] for c in init_category_models().get_category_by_type("Income")] 
cate_expense = [c["name"] for c in init_category_models().get_category_by_type("Expense")]
currency_list = list(config.CURRENCIES.keys())

body_style = """
    {
        background-color: white;
        border-radius: 12px;
        padding: 18px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        min-height: 60vh !important;
        max-height: 60vh !important;
        overflow-y: auto; /* Nếu nội dung dài thì cuộn bên trong khung */
    }"""

detail_style = """
    {
        background-color: #EEEEEE;
        border-radius: 12px;
        border: 1px solid rgba(255,255,155,1);
        padding: 18px;
        box-shadow: 0 0 8px rgba(0,0,0,0.2);
        min-height: 10vh !important;
        max-height: 10vh !important;
        overflow-y: auto; /* Nếu nội dung dài thì cuộn bên trong khung */
    }"""

# ======== RENDER TRANSACTION =========
def _render_trans_func_panel():
    cAddTrans, cFilter = st.columns([1, 1])

    with cAddTrans:
        # Add new transaction
        with st.popover("Add Transaction", icon="➕", use_container_width=True):
            st.selectbox("Select Type", type_list, key="select_type_add_trans")

            # Select category
            current_type_new = st.session_state.get("select_type_add_trans") 
            if current_type_new == "Income":
                current_type_new = cate_income
            elif current_type_new == "Expense":
                current_type_new = cate_expense       
            cate_new = st.selectbox("Select Category", current_type_new, key="new_trans_category")

            # add box       
            name = st.text_input("Transaction Name", key="new_trans_name")
            currencies = st.selectbox("Currency", config.CURRENCIES, key="new_trans_currency")

            # currencies của VN ko xài phân số (float) nhưng USD thì có, nên nếu set thông số trực tiếp sẽ bị lỗi ko đồng bộ 2 loại dữ liệu,
            # nên phải xét riêng, VND (step=500, format="%d", min_value=0) 3 cái này chung là int, còn 3 cái của USD chung là float
            currencies = st.session_state.get("new_trans_currency")
            if currencies == "VND":
                currencies_step = 500
                currencies_format = "%.0d"
                min_value = 200
            else:
                currencies_step = 0.1
                currencies_format = "%.2f"
                min_value = 0.0 
            amount = st.number_input("Amount", key="amount", step=currencies_step, min_value=min_value, format=currencies_format) # amout, base on currencies

            # Vì json lưu dạng ngày + time, nhưng hàm date_input chỉ nhận ngày, nên phải thêm giờ tự động 0:00
            date = st.date_input("Date", key="new_trans_date")
            date_time = datetime.combine(date, time.min) #

            description = st.text_input("Description", key="new_trans_description")

            if st.session_state.get("transaction_added") == True:
                st.success("Transaction added successfully!")
                st.session_state["transaction_added"] = False

            transaction_data = {
                "type": st.session_state.get("select_type_add_trans") ,
                "category": cate_new,
                "name": name,
                "currency": currencies,
                "amount": amount,
                "description": description,
                "created_at": date_time,
                "last_modified": date_time,
            }

            if st.button("Comfirm", icon="✔️", use_container_width=True):
                if not name:
                    st.error("Transaction name is required!")
                elif not date:
                    st.error("Date is required!")
                elif amount <= min_value:
                    st.error("Amount is required!")
                else:
                    init_transaction_models().add_transaction(transaction_data)
                    st.session_state["transaction_added"] = True
                    refresh_page()

    # Filter popover
    with cFilter:
        with st.popover("Filter", icon="🔎", use_container_width=True):    
            # Select type
            st.selectbox("↔️ Transaction Type", type_list, key="select_type2")

            # Select category
            if st.session_state.select_type2 == "Income":
                st.selectbox("📦 Category Name", cate_income, key="select_category2")         
            elif st.session_state.select_type2 == "Expense":     
                st.selectbox("📦 Category Name", cate_expense, key="select_category2")
            
            # Select date range
            st.select_slider("📅 Date Range Option", options=config.DEFAULT_TIME_FILTERS, key="date_range2")

            # Select currency
            st.selectbox("💰 Currency", currency_list, key="currency2")

            # Select amount
            min, max = st.columns(2)
            with min:
                st.number_input("🔽 Minimum Amount", min_value=0, value=0, key="min_amount2")
            with max:
                st.number_input("🔼 Maximum Amount", min_value=0, value=0, key="max_amount2")

def _render_trans_details(transaction_model, category_type):
    with stylable_container(key="trans_details_box", css_styles=body_style):
        st.write("Transaction Details")

def _render_transactions():
    tAll, tExpense, tIncome = st.tabs(["All", "Income", "Expense"])
    with tAll:
        st.write("Transactions")
    with tExpense:
        _render_trans_details("Expense")
    with tIncome:
        st.write("Income")

    # Header
    #if current_page == "Transactions":
 
    # Main display