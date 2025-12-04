from core.database_manager import DatabaseManager
from core import config
from bson import ObjectId
from datetime import datetime

# Class xử lý CRUD cho UserModel
class UserModel:
    def __init__(self):
        self.db_manager = DatabaseManager() # tạo instance DatabaseManager (instance = 1 đối tượng của Class)
        self.collection = self.db_manager.get_collection(collection_name=config.COLLECTIONS['user']) # lấy collection từ DatabaseManager

    # Hàm thêm user
    def create_user(self, email: str):
        # define user document
        user = {
            "email": email,
            "created_at": datetime.now(),
            "last_modified": datetime.now(),
            "is_activate": True
        }

        result = self.collection.insert_one(user)
        print("Created user successfully", user)
        return str(result.inserted_id)  # inserted_id là thuộc tính (attribute) của object, thêm id tự động cho user

    def login(self, email: str) -> str:
        # check user exist (use find_one)
        user = self.collection.find_one({'email': email})
        
        # case 1: user not exist:
        # create: call create_user(email)
        if not user:
            return self.create_user(email)

        # case 2: user exist but deactivate (user deleted account or locked account)
        # raise Error
        if user.get("is_activate") is not True:
            return {"status": "DEACTIVATED", "data": user}

        # all checking passed
        return str(user.get("_id"))

    def deactivate(self, user_id: str) -> bool:
        # find and update:
        user = self.collection.find_one({
            "_id": ObjectId(user_id),
            "is_activate": True
        })

        # case: not exist user
        if not user:
            raise ValueError("User not found")
        
        # user is validate and ready to deactivate -> update them
        result = self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"is_activate": False}}
        )
        return result.modified_count > 0
    
    def get_user_by_email(self, email: str) -> dict:
        user = self.collection.find_one({'email': email})
        return user