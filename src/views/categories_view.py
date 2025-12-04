from utils import is_default_category, get_type_list
from assets.styles import container_page_css, container_main_css, container_detail_category_css

from streamlit_extras.stylable_container import stylable_container # thư viện mở rộng của streamlit để add container với css
from datetime import datetime
import streamlit as st

# ======== DiALOGS =========

# Confirm delete dialog, 2 levels, outer def for get info, models. Inner dialog for show dialog with info
def delete_category_dialog(category_model, transaction_model):
    name = st.session_state.confirm_delete
    type = st.session_state.confirm_delete_type
    cate_id = st.session_state.confirm_delete_id
    count_transactions = len(transaction_model.get_transactions(advanced_filters={"category_id": f"{cate_id}"})) # Hàm đếm tổng số trans đang có của cate, để hỏi

    # Dialog comfirm delete
    @st.dialog(f"Category '{name}' has {count_transactions} transactions. Are you sure you want to delete?")
    def _dialog(): 
        cCancel, cConfirm = st.columns(2)

        # CANCEL
        if cCancel.button("❌ Cancel", use_container_width=True):
            # Tắt dialog confirm
            st.session_state.confirm_delete = None # Set none để tắt dialog
            st.session_state.confirm_delete_type = None
            st.rerun()

        # CONFIRM
        if cConfirm.button("✅ Confirm", use_container_width=True):

            result = category_model.delete_category(type, name)

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

# ======== MAIN RENDER =========

# Render category function panel
def render_category_func_panel(category_model):
    _, cAdd_Category = st.columns([1, 1])
    # Add new category
    with cAdd_Category:
        with st.popover("➕ Add New Category", use_container_width=True):
            if st.session_state.get("category_added"):
                st.success("Category added successfully!")
                st.session_state["category_added"] = False                 # reset flag để không hiện lại lần sau

            type = st.selectbox("Select Type", get_type_list(), key="select_type_add_cate")      
            cate_list = category_model.get_category_by_type(type)
            existing_names = {c["name"] for c in cate_list}      

            name = st.text_input("Category Name")
            if st.button("Confirm", icon="✅", key="add_category", use_container_width=True):
                if not name or name.strip() == "":
                    st.error("Category name is required!")
                elif name in existing_names:
                    st.error("Category name already exists!")
                else:
                    category_model.upsert_category(type, name)
                    st.session_state["category_added"] = True # set flag thông báo đã thêm (rồi thông báo bên ngoài sau khi đã refresh)
                    st.rerun()

# Render category list
def render_category_list(category_model, category_type: str):
    
    with stylable_container(key=f"{category_type}", css_styles=container_main_css()):
        cate_list = category_model.get_category_by_type(category_type) # cái này trả về dict full field

        if cate_list: # Check list is not empty
            st.write(f"Total: {len(cate_list)} categories")
            st.write("")

            cols = st.columns(2)
            for idx, item in enumerate(cate_list):
                col_idx = idx % 2 # remaining fraction, mỗi vòng lặp là lấy id giá trị đó chia lấy dư với 2, để tạo 2 columns, 
                # ví dụ 3 cột, items 1 2 3 sẽ năm trong cột 0, 1, 2 (vì 0%3 = 0, 1%3 = 1, 2%3 = 2),
                # nhưng qua item thứ 4 (3%3 = 0) thì sẽ quay trở lại colum thứ 1 (đầu tiên)

                with cols[col_idx]:
                    with stylable_container(key=f"category_item_{item['_id']}", css_styles=container_detail_category_css()):
                        cContent, cButton = st.columns([4, 1])

                        with cContent:
                            cleft, cright = st.columns([1, 1])
                            with cleft:
                                st.write(f"📌 {item.get("name")}")         
                                st.caption(f"Type: {item.get('type')}")
                            with cright:
                                st.write(f"Created at: {item.get("created_at").strftime("%d-%m-%Y")}")
                                st.caption(f"Last modified: {item.get('last_modified').strftime('%d-%m-%Y')}")
                                
                        with cButton:
                            #st.write("") # Đẩy nút xuống
                            cEdit, cDelete = st.columns([1, 1])
                            with cEdit:
                            # Check if category is not default in config
                                if not is_default_category(category_name=item['name'], category_type=item['type']):
                                    with st.popover("✏️"):
                                        
                                        # Set default type by current item's type
                                        key_type = f"edit_type_{item['_id']}"                                                                            
                                        if key_type not in st.session_state: # Nếu chưa có trong session thì set default = type hiện tại
                                            st.session_state[key_type] = item["type"]
                                        edit_type = st.selectbox("Change type", get_type_list(), key=key_type)
                                            
                                        # Set default name by current item's name
                                        key_new_name = f"new_name_{item['_id']}" 
                                        edit_name = st.text_input("Change category name", item.get("name"), key=key_new_name)                                 
                                        
                                        # lưu tên cũ để hiện thông báo
                                        key_old_name = f"old_name_{item['_id']}"      
                                        old_name = item.get("name")                                           
                                        if key_old_name not in st.session_state:
                                            st.session_state[key_old_name] = old_name

                                        # Message after update                     
                                        if st.session_state.get(f"edit_cate_success_{item['_id']}") == True: # Set thêm key cho vòng lặp
                                            st.success(f"Category '{st.session_state[key_old_name]}' updated to '{edit_name}' successfully!")
                                            st.session_state[f"edit_cate_success_{item['_id']}"] = False # Reset session state  

                                        # Set input data
                                        cate_data = {
                                            "type": edit_type,
                                            "name": edit_name,
                                            "last_modified": datetime.now()}
                                        
                                        # Cancel and save button
                                        _, cSave = st.columns([1,1]) # đẩy nút save qua bên phải                 
                                        if cSave.button("✅ Save", use_container_width=True, key=f"save_{item['_id']}"):

                                            # Kiểm tra tên chưa nhập mới và có tồn tại trong cate ko
                                            existing_names = {c["name"] for c in cate_list}
                                            if edit_name == item["name"]:
                                                st.error("Category name not changed!")
                                            elif edit_name in existing_names:
                                                st.error("Category name already exists")
                                            else:                                    
                                                category_model.update_category(item['_id'], cate_data)
                                                st.session_state[f"edit_cate_success_{item['_id']}"] = True         
                                                st.rerun()                                                                                             
                                else:
                                    st.popover("✏️", disabled=True) # Disable default
                
                            with cDelete:
                                if not is_default_category(category_name=item['name'], category_type=item['type']):          
                                    if st.button("🗑️", key= f"delete_{item['_id']}"):                                   
                                        st.session_state.confirm_delete = item.get("name") # Save session state = name (dùng để hiển thị name khi hỏi lên box)
                                        st.session_state.confirm_delete_id = item.get("_id") # Save session state = id
                                        st.session_state.confirm_delete_type = item.get("type") # Save session state = type
                                        st.rerun()
                                else:
                                    st.button("🗑️", key= f"delete_{item['_id']}", disabled=True) # Disable default cate
        else:
            st.subheader("No categories found")

# Main Render, call all render            
def render_categories():
    models = st.session_state["models"]   # Lấy model từ App.py
    category_model = models["category"]
    transaction_model = models["transaction"]
    
    with stylable_container(key="menu_box", css_styles=container_page_css()):

        # Header
        cHeader, cFunc = st.columns([1, 2], vertical_alignment="center")
        with cHeader:
            st.header("Categories Management")
        with cFunc:
            render_category_func_panel(category_model)

        # Line
        st.markdown("""<hr style="margin: 10px 0; border: none; border-top: 2px solid #333; opacity: 0.3;">""", unsafe_allow_html=True)
            
        # Main
        tExpense, tIncome = st.tabs(["Expense", "Income"])
        with tExpense:
            render_category_list(category_model, "Expense")
        with tIncome:
            render_category_list(category_model, "Income")

        # Dialog
        render_dialog(category_model, transaction_model)

# Render Dialog
def render_dialog(category_model, transaction_model):
    # Confirm delete call
    if st.session_state.get("confirm_delete"):
        delete_category_dialog(category_model, transaction_model)

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