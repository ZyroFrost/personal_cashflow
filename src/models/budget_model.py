from core.database_manager import DatabaseManager
from core import config
from bson import ObjectId
from typing import Optional # hàm Optional để khai báo biến có thể là None hoặc kiểu khác
from datetime import datetime

class BudgetModel:
    def __init__(self, user_id: Optional[str] = None):
        self.db_manager = DatabaseManager()
        self.collection = self.db_manager.get_collection(config.COLLECTIONS['budget'])
        self.user_id = user_id

    def set_user_id(self, user_id: str): # → Dùng sau khi user đăng nhập, để cập nhật user_id
        self.user_id = ObjectId(user_id) if user_id is not None else None

    # Save budget
    def save_budget(self, budget_id: str | None, category_id: str, budget_type: str, currency: str, amount: float, month: int, year: int):
        """
        - nếu budget_id = None → CREATE
        - nếu budget_id != None → UPDATE
        """

        # Check duplicate (ignore self when update)
        query = {
            "user_id": self.user_id,
            "category_id": ObjectId(category_id),
            "month": month,
            "year": year
        }

        if budget_id is not None:
            query["_id"] = {"$ne": ObjectId(budget_id)}

        exists = self.collection.find_one(query)
        if exists:
            print("Budget already exists")
            return False

        # UPDATE
        if budget_id is not None:
            self.collection.update_one(
                {"_id": ObjectId(budget_id), "user_id": self.user_id},
                {
                    "$set": {
                        "category_id": ObjectId(category_id),
                        "budget_type": budget_type,
                        "currency": currency,
                        "amount": amount,
                        "month": month,
                        "year": year,
                        "last_modified": datetime.now()
                    }
                }
            )
            print("Updated budget successfully with ID: ", budget_id)
            return True

        # CREATE
        doc = {
            "user_id": self.user_id,
            "category_id": ObjectId(category_id),
            "budget_type": budget_type,
            "currency": currency,
            "amount": amount,
            "month": month,
            "year": year,
            "created_at": datetime.now(),
            "last_modified": datetime.now()
        }
        
        result = self.collection.insert_one(doc)
        print(f"Created budget successfully with ID: {result.inserted_id}")
        print(doc)
        return True
    
    def delete_budget(self, budget_id: str):
        result = self.collection.delete_one({"_id": ObjectId(budget_id), "user_id": self.user_id})
        return result.deleted_count
    
    def get_budgets(self):
        if not self:
            return []
        return list(self.collection.find({"user_id": self.user_id}).sort("created_at", -1))

    def get_budget_by_budget_type(self, budget_type: str):
        return list(self.collection.find({"user_id": self.user_id, "budget_type": budget_type}).sort("created_at", -1))
    
    def count_budget_by_user(self, user_id: ObjectId) -> int:
        return self.collection.count_documents({"user_id": user_id})
    
    def count_budget_by_category(self, category_id: ObjectId) -> int:
        return self.collection.count_documents({"user_id": self.user_id, "category_id": category_id})
    
    # Hàm tính process bar (lấy từ aggregate bên transaction model)
    def get_budget_progress(self, budget, analyzer_model, transaction_model):
 
        # Get total spent (đã group by currency)
        raw_spent_by_currency = transaction_model.aggregate_spent_for_budget(
            user_id=budget["user_id"],
            category_id=budget["category_id"],
            budget_type=budget["budget_type"],
            month=budget.get("month"),
            year=budget["year"]
        )

        # Convert theo currency 1 lần sau khi đã có tổng
        spent_converted = 0.0
        for row in raw_spent_by_currency:
            amount = row["total_spent"] # tổng tiền
            source_currency = row["_id"] # currency đã groupby

            # Convert to budget currency
            converted = analyzer_model.exchange_rate_model.convert_currency(
                amount=amount,
                from_currency=source_currency,
                to_currency=budget["currency"]
            )
            spent_converted += converted

        amount_budget = budget.get("amount", 0)
        percent_complete = spent_converted / amount_budget if amount_budget > 0 else 0

        return {
            "total_spent": spent_converted,
            "percent_complete": percent_complete
        }

'''
if __name__ == "__main__":
    budget_model = BudgetModel()
    budget_model.set_user_id("6936e87c628a6ac20ec0de8e")
    get_budgets = budget_model.get_budgets()
    print(len(get_budgets))
#'''