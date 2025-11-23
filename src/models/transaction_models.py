from core import config
from core.database_manager import DatabaseManager
from bson import ObjectId
from datetime import datetime

collection_name = config.COLLECTIONS['transaction'] # Lấy collection transaction từ config

class TransactionModel:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.collection = self.db_manager.get_collection(collection_name=collection_name)
         # 1 self (instance) có t hể chứa nhiều thuộc tính, ở đây là self.collection và self.db_manager
         # mỗi thuộc tính dùng được cho nhiều mục đích khác nhau
    
    # Hàm định nghĩa cấu trúc của TransactionModel
    @staticmethod # hàm tĩnh ko nhận tham số self của class
    def format_and_validate_data(transaction_data: dict): # Hàm này nhận data thô và chuyển đổi nó  
        formatted_data = {
            "type": transaction_data.get("type"), 
            "category": transaction_data.get("category"),
            "name": transaction_data.get("name"),
            "currency": transaction_data.get("currency"),
            "amount": float(transaction_data["amount"]),
            "description": transaction_data.get("description", ""),
            "created_at": datetime.now(),        
            "last_modified": datetime.now(),
        }
        return formatted_data

    # Hàm thêm transaction
    def add_transaction(self, transaction_data: dict):
        try:
            result = self.collection.insert_one(transaction_data) # self.collection để gọi thuộc tính collection trong class (từ self)
            print("Added transaction successfully", transaction_data)
            return result
        except Exception as e:
            print(f"Error: {e}")
    
    # Hàm xóa transaction theo id
    def delete_transaction(self, transaction_id: str):
        print("Deleted transaction successfully", transaction_id)
        return self.collection.delete_one({"_id": ObjectId(transaction_id)})
    # _id là hệ thống của MongoDB tự tạo khi add_transaction ở trên
    # _id KHÔNG phải string, _id là kiểu: ObjectId("xxxxxxxxxx")
    # Vì MongoDB lưu _id dưới dạng ObjectId, không phải string. Nên muốn tìm đúng document, phải chuyển: về ObjectId,
    # Nếu không chuyển → MongoDB không tìm ra → update / delete thất bại
    
    # Hàm update transaction theo id
    def update_transaction(self, transaction_id: str, transaction_data: dict):
        result = self.collection.update_one(
            {"_id": ObjectId(transaction_id)}, 
            {"$set": transaction_data}) # $set là toán tử của update dữ liệu, set dữ liệu mới cần đổi
        return result  
    # Với {"$set": transaction_data} Chỉ những field bạn đưa vào transaction_data mới được thay đổi
    # Các field bạn KHÔNG đưa vào giữ nguyên, không bị xóa
    
    # Hàm tìm transaction theo id
    def get_transaction_by_id(self, transaction_id: str):
        result = self.collection.find_one({"_id": ObjectId(transaction_id)}) # Dùng find_one, vì id chỉ tìm đúng 1 document
        return result

    # Hàm tìm tât câ transaction
    def get_all_transactions(self):
        result = self.collection.find({})
        return result

    # Hàm tìm transaction theo type
    def get_transaction_by_type(self, type: str):
        result = self.collection.find({"type": type}) # dùng find vì tìm theo type sẽ có thể trả về nhiều kq
        return result
    
    # Hàm tìm transaction theo category
    def get_transactions_by_category(self, category: str):
        result = self.collection.find({"category": category}) # dùng find vì tìm theo category sẽ có thể trả về nhiều kq
        return result
    
    # Hàm tìm transaction theo date
    def get_transactions_by_date(self, date):
        result = self.collection.find({"date": date})
        return result

'''
if __name__== "__main__":
    print("Init transaction collection")
    transaction = TransactionModel()
''' 