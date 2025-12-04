from datetime import datetime, timedelta
from core.database_manager import DatabaseManager
from core import config
from dotenv import load_dotenv
import requests, os

class ExchangeRateModel:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.collection = self.db_manager.get_collection(config.COLLECTIONS["exchange_rate"])

    def get_rate(self, current_currency: str, target_currency: str):
        current_currency = current_currency.upper()
        target_currency = target_currency.upper()
        record = self.collection.find_one({"_id": current_currency})

        # Nếu chưa có record → fetch API
        if not record:
            rates = self.fetch_rate_from_api(current_currency)
            if not rates:
                return None # fetch bị lỗi thì trả về None
            self.save_rate(current_currency, rates)
            return rates.get(target_currency)

        # Nếu có rồi → check thời gian cập nhật
        updated_at = record["updated_at"]
        if datetime.now() - updated_at > timedelta(hours=24):
            rates = self.fetch_rate_from_api(current_currency)
            self.update_rate(current_currency, rates)
            return rates

        # Còn trong hạn → dùng cache
        return record["rate"]

    def save_rate(self, current_currency: str, rates: dict):
        self.collection.insert_one({
            "_id": current_currency,
            "rate": rates,
            "updated_at": datetime.now()
        })

    def update_rate(self, current_currency: str, rates: dict):
        self.collection.update_one(
            {"_id": current_currency},
            {"$set": {"rate": rates, "updated_at": datetime.now()}},
            upsert=True
        )

    def fetch_rate_from_api(self, current_currency) -> dict:

        # Check API key
        try:
            load_dotenv()
            exchange_API_key = os.getenv("EXCHANGE_API") # API lấy từ web cập nhập giá USD tự động
        except Exception as e:
            print(f"Missing exchange API key: {e}")
            return None
        
        # Fetch API
        url = f"https://v6.exchangerate-api.com/v6/{exchange_API_key}/latest/{current_currency}" # Cấu trúc endpoint
        try:
            resp = requests.get(url).json()
            result = resp
        except Exception as e:
            print(f"Error when exchange currency: {e}")
            result = None
        return result["conversion_rates"]
    
'''
if __name__ == "__main__":
    exchange_rate_model = ExchangeRateModel()
    rate = exchange_rate_model.get_rate("USD", "VND")
    print("Exchange Rate USD to VND:", rate)
#''' 