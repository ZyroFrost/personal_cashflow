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

# tùy chỉnh cho phần header
header_style = """
    {
        background-color: white;
        border-radius: 12px;
        padding: 15px 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        min-height: 8vh !important;
        max-height: 8vh !important;
        align-items: center; /* Canh giữa dọc */
    }"""

# tùy chỉnh cho phần main
body_style = """
    {
        background-color: white;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        min-height: 70.4vh !important;
        max-height: 70.4vh !important;
        overflow-y: auto; /* Nếu nội dung dài thì cuộn bên trong khung */
    }"""

markdown_style = """
    {
        background-color: lightgray;
        border-radius: 5px;
        margin: 5px !important;
        box-shadow: 0 0px 0px rgba(0,0,0,0.05);
        min-height: 10 !important;
        max-height: 10 !important;
        max_width: 100vh !important;
        color: #333;
        font-size: 8px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: 3px !important;
        margin-left: 3px !important;
        padding: 1rem !important;
        padding-top: 5px;
        padding-left: 10px;
        margin-bottom: 10px;
    }"""

# ======== SHOW TRANSACTION =========
def show_transactions():

    # Get list from db
    type_list = config.TRANSACTION_TYPES.copy()
    type_list.remove("Transfer") # Remove transfer because can't add cate to transfer
    type_list_full = config.TRANSACTION_TYPES.copy()
    cate_income = [c["name"] for c in init_category_models().get_category_by_type("Income")] 
    cate_expense = [c["name"] for c in init_category_models().get_category_by_type("Expense")]
    currency_list = list(config.CURRENCIES.keys())

    # Header
    with stylable_container(key="header_box", css_styles=header_style):
        header_left, header_right = st.columns([1, 2], gap="small", vertical_alignment="center")
        
        # Display main name
        with header_left:
            st.subheader("Transactions")

        # Filter panel
        with header_right:
            cToolbar, cFilter, cRefresh = st.columns([1, 1, 0.5], gap="small")
            with cToolbar:
                with st.popover("Toolbar", icon="🛠️", use_container_width=True):

                    with st.popover("Edit Category", icon="📦", use_container_width=True):             
                        # Thông báo khi thêm category (khi refresh trang), vì khi thông báo trực tiếp trong nút add thì refresh sẽ mất dòng thông báo
                        if st.session_state.get("category_added"):
                            st.success("Category added successfully!")
                            # reset flag để không hiện lại lần sau
                            st.session_state["category_added"] = False

                        # Add new category
                        with st.popover("Add New Category", icon="➕", use_container_width=True):
                            type = st.selectbox("Select Type", type_list, key="select_type_add_cate")
                            name = st.text_input("Category Name")
                            if st.button("Confirm", icon="✅", key="add_category", use_container_width=True):
                                if not name:
                                    st.error("Category name is required!")
                                else:
                                    if name in cate_income or name in cate_expense:
                                        st.error("Category name already exists!")
                                    else:
                                        init_category_models().add_category(type, name)
                                        st.session_state["category_added"] = True # set flag thông báo đã thêm (rồi thông báo bên ngoài sau khi đã refresh)
                                        refresh_page()
                        
                        # Thông báo khi xóa category    
                        if st.session_state.get("category_deleted"):
                            st.success("Category deleted successfully!")
                            st.session_state["category_deleted"] = False

                        # Delete category
                        with st.popover("Delete Category", icon="➖", use_container_width=True):
                            type = st.selectbox("Select Type", type_list, key="select_type_delete")
                            name = st.selectbox("Select Category", cate_expense if st.session_state.select_type_delete == "Expense" else cate_income, key="select_category_delete")
                            if st.button("Confirm", icon="✅", key="delete_category", use_container_width=True):
                                init_category_models().delete_category(type, name)
                                st.session_state["category_deleted"] = True
                                refresh_page()

                    # Add new transaction
                    with st.popover("Add New Transaction", icon="➕", use_container_width=True):
                        st.selectbox("Select Type", type_list_full, key="select_type_add_trans")

                        # Select category
                        current_type_new = st.session_state.get("select_type_add_trans") 
                        if current_type_new == "Income":
                            current_type_new = cate_income
                        elif current_type_new == "Expense":
                            current_type_new = cate_expense
                        else: # transfer
                            from_account = config.TRANSFER_CATEGORY[0]
                            to_account = config.TRANSFER_CATEGORY[1]         
                        cate_new = st.selectbox("Select Category", current_type_new, key="new_trans_category")

                        # Create layout by Transfer
                        if current_type_new == "Transfer":     
                            cfrom, cto = st.columns([1, 1], gap="small")     
                            with cfrom:
                                st.selectbox(from_account, "account1", key="account_from")
                            with cto:
                                st.selectbox(to_account, "account2", key="account_to")

                        # add box       
                        name = st.text_input("Transaction Name", key="new_trans_name")
                        currencies = st.selectbox("Currency", config.CURRENCIES, key="new_trans_currency")

                        # currencies của VN ko xài phân số (float) nhưng USD thì có, nên nếu set thông số trực tiếp sẽ bị lỗi ko đồng bộ 2 loại dữ liệu,
                        # nên phải xét riêng, VND (step=500, format="%d", min_value=0) 3 cái này chung là int, còn 3 cái của USD chung là float
                        currencies = st.session_state.get("new_trans_currency")
                        if currencies == "VND":
                            currencies_step = 500
                            currencies_format = "%d"
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
                            "date": date_time,
                            "description": description}
 
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

            with cFilter:    
                with st.popover("Filter", icon="🔎", use_container_width=True):    
                    # Select type
                    st.selectbox("↔️ Transaction Type", type_list, key="select_type2")

                    # Select category
                    if st.session_state.select_type2 == "Income":
                        st.selectbox("📦 Category Name", cate_income, key="select_category2")         
                    elif st.session_state.select_type2 == "Expense":     
                        st.selectbox("📦 Category Name", cate_expense, key="select_category2")
                    else:
                        st.selectbox("📦 Category Name", config.TRANSFER_CATEGORY, key="select_category2")
                    
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

                with cRefresh:
                    st.button("Refresh", icon="🔄", on_click=refresh_page)
                
    # Main display
    with stylable_container(key="main_box", css_styles=body_style):

        # Variable
        all_trans= list(init_transaction_models().get_all_transactions())
        unique_dates = sorted(set([t['date'] for t in all_trans]), reverse=True)

        col1, col2 = st.columns(2)
        with col1:   
            for idd, d in enumerate(unique_dates):
                st.write(f"**{d.strftime('%B %d, %Y')}**") # định dạng ngày
                with stylable_container(key=f"box_{idd}", css_styles=markdown_style): # key=f"box_{date}", vì container nằm trong vòng lặp nên phải tạo key động để ko trùng     
                    dates = list(init_transaction_models().get_transactions_by_date(d))
                    for trans in dates:
                        trans_id = str(trans['_id'])
                        left, right = st.columns([3,1], gap="small")
                        with left:
                            st.markdown(f"*{trans['type'] + ": " + trans['category']}*")
                            st.markdown(f"**{trans["name"]}**")
                        with right:
                            edit_key = f"edit_{trans_id}"
                            st.markdown(f"*{arrow(trans['type']) + " " + str(trans['amount']) + " " + trans['currency']}*")                            
                            with st.popover(f"Edit", icon="✏️", use_container_width=True):
                                st.selectbox("Transaction type", type_list, key=f"edit_type_{edit_key}")
                                
                                # Category edit
                                current_key = st.session_state[f"edit_type_{edit_key}"]                           
                                if current_key == "Income":
                                    category = st.selectbox("Category", cate_income, key=f"edit_cate_{edit_key}")
                                elif current_key == "Expense":
                                    category = st.selectbox("Category", cate_expense, key=f"edit_cate_{edit_key}")
                                
                                # Other edit
                                name = st.text_input("Transaction name", value=trans["name"], key=f"edit_name_{edit_key}")
                                amount = st.number_input("Amount", value=trans["amount"], key=f"edit_amount_{edit_key}")
                                currencies = st.selectbox("Currency", currency_list, key=f"edit_currency_{edit_key}")
                                description = st.text_input("Description", value=trans["description"], key=f"edit_description_{edit_key}")

                                # Edit Success Flag
                                button_edit_key = f"edit_{edit_key}"
                                if st.session_state.get(button_edit_key):
                                    st.success("Transaction updated successfully!")
                                    st.session_state[button_edit_key] = False

                                # button
                                bConfirm, bDelete = st.columns([1, 1.5], gap="small")
                                with bConfirm:
                                    if st.button("Comfirm", icon="✔️", use_container_width=True, key=f"confirm_{edit_key}"):
                                        update_date = {
                                            "type": current_key,
                                            "category": category,
                                            "name": name,
                                            "amount": amount,
                                            "currency": currencies,
                                            "description": description,
                                            "last_modified": datetime.now()
                                        }
                                        try:
                                            init_transaction_models().update_transaction(trans_id, update_date)
                                            st.session_state[button_edit_key] = True
                                            st.rerun()
                                        except Exception as e:
                                            st.error(f"Error updating transaction: {e}")
                                with bDelete:
                                    st.button("Delete Transaction", icon="🗑️", use_container_width=True, key=f"delete_{edit_key}")

                                #st.text_input("Transaction name", value=trans["name"], key=f"edit_name_{trans}_{idd}")
                                #st.button("Delete", icon="🗑️", use_container_width=True, key=f"confirm_{trans}_{idd}")
             
        with col2:
            st.write("You can see your statistics here.")