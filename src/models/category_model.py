# MỤC ĐÍCH CỦA category_models.py: Xử lý toàn bộ CRUD (Create, Read, Update, Delete) cho Category
# backend cho các nút: Add Category, Get Category, Delete Category, Update Category trên App
from core.database_manager import DatabaseManager
from core import config
from bson import ObjectId
from typing import Optional # hàm Optional để khai báo biến có thể là None hoặc kiểu khác
from datetime import datetime

# Class xử lý CRUD cho CategoryModel
class CategoryModel:

    # Tạo instance DatabaseManager (singleton → 1 kết nối duy nhất)
    def __init__(self, user_id: Optional[str] = None):
        self.db_manager = DatabaseManager() # tạo instance DatabaseManager (instance = 1 đối tượng của Class)
        self.collection = self.db_manager.get_collection(config.COLLECTIONS['category']) # lấy collection từ DatabaseManager
        self.user_id = user_id # lấy tham số user_id từ google auth truyền vào

    def set_user_id(self, user_id: str): # → Dùng sau khi user đăng nhập, để cập nhật user_id
        self.user_id = ObjectId(user_id) if user_id is not None else None

    # Khoi tao category mac dinh
    def __initialize_default_categories__(self):

        # Check if there is user_id, exist earlier
        if not self.user_id:
            return
        
        # EXPENSE
        for cate in config.DEFAULT_CATEGORIES_EXPENSE: # Lặp từng Key trong Expense (Shopping, Transportation, ...)
            self.upsert_category(category_type = "Expense", category_name= cate)

        # INCOME
        for cate in config.DEFAULT_CATEGORIES_INCOME:
            self.upsert_category(category_type = "Income", category_name= cate)

    # Nút thêm category
    def upsert_category(self, category_type: str, category_name: str):

        # define filter, filter = điều kiện tìm document, dùng cho: find(), update_one(), delete_one(), find_one()
        filter_ = {
            "type": category_type,
            "name": category_name,
            "user_id": self.user_id
        } 

        # define update_doc
        update_doc = {
            "$set": {"last_modified": datetime.now()},
            "$setOnInsert": {"created_at": datetime.now()} 
        }

        result = self.collection.update_one(
            filter_,
            update_doc,
            upsert=True
        )
        return result

    # Hàm xóa category
    def delete_category(self, category_type: str, category_name: str):
        result = self.collection.delete_one({"type": category_type, "name": category_name, "user_id": self.user_id}) # add user_id condition
        return result.deleted_count  # trả về số document đã xóa (0 hoặc 1) để check nút xóa có thành công không

    # Hàm cập nhập category
    def update_category(self, category_id: str, category_data: dict):
        result = self.collection.update_one(
            {"_id": ObjectId(category_id), "user_id": self.user_id}, # cập nhập thêm điều kiện user_id để tránh người dùng khác cập nhập category của người khác
            {"$set": category_data}) # $set là toán tử của update dữ liệu, set dữ liệu mới cần đổi
        return result.modified_count > 0 # trả về true false cập nhập (0 hoặc 1), nếu 1 là thành công thì mới return dữ liệu

    # Hàm tìm category theo type, có thể tìm All
    def get_category_by_type(self, category_type: str) -> list:
        query = {"user_id": self.user_id} # tạo query chung cho 2 trường hợp (All và Expense/Income)
        if category_type in ["Expense", "Income"]: # nếu truyền vào Expense hoặc Income, tìm theo type
            query["type"] = category_type # nếu có type thì thêm điều kiện type vào query
        return list(self.collection.find(query).sort("created_at", -1))  # -1 = giảm dần (descending)
    
    # Hàm lấy tên category từ ID (dùng cho transaction vì transaction chỉ lưu category_id)
    def get_category_name_by_id(self, category_id: ObjectId) -> str:
        doc = self.collection.find_one({
            "_id": ObjectId(category_id),
            "user_id": self.user_id
        })
        return doc["name"] if doc else None # Kiểm tra None trong trường hợp đặc biệt nếu user xóa category rồi mà transaction vẫn còn tham chiếu đến category đó, 
        # hoặc user đổi tài khoản vẫn lưu category_id cũ từ user khác

    # This function returns the category ID based on the category name, trasfer category name to id before saving to a new transaction
    def get_category_id_by_name(self, category_name: str) -> ObjectId:
        doc = self.collection.find_one({
            "name": category_name,
            "user_id": self.user_id
        })
        return doc["_id"] if doc else None

    # This function returns a dictionary where the keys are the category names and the values are the category IDs, use to put in selectbox
    def get_category_name_by_type(self, category_type: str) -> dict:
        categories = self.get_category_by_type(category_type)
        return {c["name"]: str(c["_id"]) for c in categories}
    
'''
if __name__== "__main__":
    print("Init category collection")
    cate = CategoryModel() 
    #cate.get_category_by_type(type="Income")
    #cate.get_category_name_by_id("69226b9f5bc8d2cb663e25bc") # test get name
    # gán cate chỉ dùng khi test file 1 mình, cate là 1 object (instance) của class CategoryModel, để xem class có lỗi hay không
    # gán cate để dễ debug (có thể mở Python REPL hay debug và kiểm tra) -> ví dụ lấy cate print(cate.collection) để kiểm tra
    print(cate.get_category_by_type("All")[0]["name"], "\n")
#'''