import streamlit as st
from core import config
from models.category_models import CategoryModel
from streamlit_extras.stylable_container import stylable_container # thư viện mở rộng của streamlit để add container với css
from datetime import datetime, time

# ======== CONFIG =========
@st.cache_resource 
def init_category_models():
    return CategoryModel()

# Confirm delete dialog, biến ngoài để biến gọi tên của cate, và type
def delete_category_dialog():
    name = st.session_state.confirm_delete
    type = st.session_state.confirm_delete_type

    # Tạo dialog xác nhận xóa categoty
    @st.dialog(f"Confirm delete category '{name}'")
    def _dialog(): 

        cCancel, cConfirm = st.columns(2)

        # CANCEL
        if cCancel.button("❌ Cancel", use_container_width=True):
            # Tắt dialog confirm
            st.session_state.confirm_delete = None
            st.session_state.confirm_delete_type = None
            st.rerun()

        # CONFIRM
        if cConfirm.button("✅ Confirm", use_container_width=True):

            result = init_category_models().delete_category(type, name)

            # Tắt dialog confirm
            st.session_state.confirm_delete = None
            st.session_state.confirm_delete_type = None

            # Mở dialog message
            if result: # nếu xóa thanh cong
                st.session_state.delete_success = name # gán trạng thái xóa thanh cong thành = name (delete_success = confirm_delete)
            else:
                st.session_state.delete_failed = name
                
            st.rerun()
    _dialog()

# List from db
type_list = config.TRANSACTION_TYPES.copy()
cate_income = [c["name"] for c in init_category_models().get_category_by_type("Income")] 
cate_expense = [c["name"] for c in init_category_models().get_category_by_type("Expense")]

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

def _render_category_func_panel():
    _, cAdd_Category = st.columns([1, 1])
    # Add new category
    with cAdd_Category:
        with st.popover("Add New Category", icon="➕", use_container_width=True):
            if st.session_state.get("category_added"):
                st.success("Category added successfully!")
                # reset flag để không hiện lại lần sau
                st.session_state["category_added"] = False

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
                        st.rerun()

def _render_category_list(category_model, category_type: str):
    with stylable_container(key=f"category_list_{category_type}", css_styles=body_style):
        st.subheader(f"{category_type} Categories")
        expense_lst = category_model.get_category_by_type(type = category_type)

        if expense_lst: # Check list is not empty
            st.write(f"Total: {len(expense_lst)} categories")

            cols = st.columns(3)
            for idx, item in enumerate(expense_lst):
                col_idx = idx % 3 # remaining fraction, mỗi vòng lặp là lấy id giá trị đó chia lấy dư với 3, để tạo 3 columns, 
                # ví dụ items 1 2 3 sẽ năm trong cột 0, 1, 2 (vì 0%3 = 0, 1%3 = 1, 2%3 = 2),
                # nhưng qua item thứ 4 (3%3 = 0) thì sẽ quay trở lại colum thứ 1 (đầu tiên)

                with cols[col_idx]:
                    with stylable_container(key=f"category_item_{item['_id']}", css_styles=detail_style):
                        cContent, cEdit, cDelete = st.columns([6, 1, 1.1])

                        with cContent:
                            cleft, cright = st.columns([1.2, 1.5])
                            with cleft:
                                st.write(f"📌 {item.get("name")}")         
                            with cright:
                                st.caption(f"Created at: {item.get("created_at").strftime("%d-%m-%Y")}")
                                st.caption(f"Last modified: {item.get('last_modified').strftime('%d-%m-%Y')}")
                                
                        with cEdit:
                            # Check if category is not default in config
                            if (item.get("name") not in config.DEFAULT_CATEGORIES_EXPENSE) and item.get("name") not in config.DEFAULT_CATEGORIES_INCOME:
                                with st.popover("✏️"):
                                    
                                    # Set default type by current item's type
                                    key_type = f"edit_type_{item['_id']}"              
                                    key_new_name = f"new_name_{item['_id']}"                              
                                    if key_type not in st.session_state: # Nếu chưa có trong session thì set default = type hiện tại
                                        st.session_state[key_type] = item["type"]
                                        
                                    # Render edit form
                                    edit_type = st.selectbox("Change type", type_list, key=f"edit_type_{item['_id']}")
                                    edit_name = st.text_input("Change category name", item.get("name"), key=key_new_name)                          
                                    cate_date = {
                                        "type": edit_type,
                                        "name": edit_name,
                                        "last_modified": datetime.now()} 
                                    
                                    # lưu tên cũ
                                    key_old_name = f"old_name_{item['_id']}"      
                                    old_name = item.get("name")                                           
                                    if key_old_name not in st.session_state:
                                        st.session_state[key_old_name] = old_name

                                    # Message after update                     
                                    if st.session_state.get(f"edit_cate_success_{item['_id']}") == True: # Set thêm key cho vòng lặp
                                        st.success(f"Category '{st.session_state[key_old_name]}' updated to '{edit_name}' successfully!")
                                        st.session_state[f"edit_cate_success_{item['_id']}"] = False # Reset session state  

                                    # Cancel and save button
                                    _, cSave = st.columns([1,1])                 
                                    if cSave.button("✅ Save", use_container_width=True, key=f"save_{item['_id']}"):
                                        # Kiểm tra tên có tồn tại trong cate ko
                                        if (edit_name in cate_income and edit_type == "Income") or \
                                            (edit_name in cate_expense and edit_type == "Expense"): 
                                            st.error("Category name already exists")
                                        else:                                    
                                            category_model.update_category(item['_id'], cate_date)
                                            st.session_state[f"edit_cate_success_{item['_id']}"] = True         
                                            st.rerun()                                                             
                                    
                            else:
                                st.button("✏️", key = f"edit_{item['_id']}", disabled=True) # Disable default
            
                        with cDelete:
                            if (item.get("name") not in config.DEFAULT_CATEGORIES_EXPENSE) and item.get("name") not in config.DEFAULT_CATEGORIES_INCOME:              
                                if st.button("🗑️", key= f"delete_{item['_id']}"):
                                    st.session_state.confirm_delete = item.get("name") # Save session state = name
                                    st.session_state.confirm_delete_type = item.get("type") # Save session state = type
                                    st.rerun()
                            else:
                                st.button("🗑️", key= f"delete_{item['_id']}", disabled=True) # Disable default cate
        else:
            st.write("No categories found")
                        
def _render_categories():
    tExpense, tIncome = st.tabs(["Expense", "Income"])
    with tExpense:
        _render_category_list(CategoryModel(), "Expense")
    with tIncome:
        _render_category_list(CategoryModel(), "Income")  

def _render_dialog():
    # Success dialog
    if st.session_state.get("delete_success"): # nếu state nhận dc delete_success
        name = st.session_state.delete_success # gán name = trạng thái đã xóa

        @st.dialog("Success") # Tạo dialog success
        def _success():
            st.success(f"Category '{name}' deleted successfully!") # Trong dialog success hiển thị thông báo xóa thanh cong

            _, cClose = st.columns([5, 1]) # đẩy nút close qua bên phải dialog
            with cClose:
                if st.button("Close", use_container_width=True):
                    st.session_state.delete_success = None
                    st.rerun()
        _success()

    # Failed dialog
    if st.session_state.get("delete_failed"): # nếu state nhận dc delete_failed
        name = st.session_state.delete_failed

        @st.dialog("Error")
        def _failed():
            st.error(f"Failed to delete category '{name}'!")
            
            _, cClose = st.columns([5, 1]) # đẩy nút close qua bên phải dialog
            with cClose:
                if st.button("Close"):
                    st.session_state.delete_failed = None
                    st.rerun()
        _failed()

    # Confirm delete call
    if st.session_state.get("confirm_delete"):
        delete_category_dialog()