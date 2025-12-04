import pandas as pd
from models.transaction_model import TransactionModel
from datetime import datetime, timedelta

class FinanceAnalyzer:
    def __init__(self, transaction_model: TransactionModel):
        self.transaction_model = transaction_model

    def get_transactions_by_dataframe(self):
        """Convert transactions to pandas dataframe"""
        transactions = self.transaction_model.get_transactions()

        if not transactions:
            return pd.DataFrame()

        df = pd.DataFrame(transactions)
        df['date'] = pd.to_datetime(df['date'])
        return df
    
    def calculate_total_by_type(self, transaction_type, start_date=None, end_date=None):
        '''Calculates the total amount for a given transaction type and date range.'''
        if start_date and end_date:
            transactions = self.transaction_model.get_transactions_by_date_range(start_date, end_date)
        else:
            transactions = self.transaction_model.get_transactions()

        total = sum(t['amount'] for t in transactions if t['type'] == transaction_type)
        return total
    
    def get_spending_by_category(self, start_date=None, end_date=None):
        """Get spending grouped by category"""
        if start_date and end_date:
            transactions = self.transaction_model.get_transactions_by_date_range(start_date, end_date)
        else:
            transactions = self.transaction_model.get_transactions()

        df = pd.DataFrame(transactions)
        df["category_id"] = df["category_id"].astype(str)
        if df.empty:
            return pd.DataFrame()

        # Filter only expenses
        expenses = df[df['type'] == 'Expense']

        if expenses.empty:
            return pd.DataFrame()
   
        category_spending = expenses.groupby('category_id')['amount'].agg(['sum', 'count', 'mean']).reset_index()
        category_spending.columns = ['Category', 'Total', 'Count', 'Average']
        category_spending = category_spending.sort_values('Total', ascending=False)
        
        return category_spending
    
    def get_monthly_trend(self, user_id="default_user", months=6):
        """Get monthly spending and income trend"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=months*30)
        
        transactions = self.transaction_model.get_transactions_by_date_range(
            start_date, end_date
        )
        
        df = pd.DataFrame(transactions)
        
        if df.empty:
            return pd.DataFrame()
        
        df['date'] = pd.to_datetime(df['date'])
        df['month'] = df['date'].dt.to_period('M')
        
        monthly_data = df.groupby(['month', 'type'])['amount'].sum().unstack(fill_value=0)
        monthly_data.index = monthly_data.index.to_timestamp()
        
        return monthly_data
    
    def get_daily_average(self):
        """Calculate daily average spending"""

        # approach 1:
        transactions = self.transaction_model.get_transactions()
        expenses = [t for t in transactions if t['type'] == 'Expense']

        # # approach 2:
        # advanced_filter = {"type": 'Expense'}
        # expenses = self.transaction_model.get_transactions(advanced_filter)

        if not expenses:
            return 0
        
        df = pd.DataFrame(expenses)
        df['date'] = pd.to_datetime(df['date']) # ensure convert properly datetime format
        
        date_range = (df['date'].max() - df['date'].min()).days + 1
        total_spending = df['amount'].sum()
        
        return total_spending / date_range if date_range > 0 else 0
    
    def compare_periods(self, start_date: datetime, end_date: datetime, transaction_type=None):
        """
        Compare total income/expense/net between:
        - current period (start_date → end_date)
        - previous period of same length
        
        transaction_type:
            'Income', 'Expense', None = Net Balance
        """
        # --- Period length ---
        days = (end_date - start_date).days - 1
        print(days)
        
        # --- Previous period ---
        prev_end = start_date - timedelta(days=1)
        prev_start = prev_end - timedelta(days=days - 1)

        # --- Current value ---
        current_transactions = self.transaction_model.get_transactions_by_date_range(start_date, end_date)

        # --- Previous value ---
        prev_transactions = self.transaction_model.get_transactions_by_date_range(prev_start, prev_end)

        # Filter type if needed
        if transaction_type:
            current_value = sum(t['amount'] for t in current_transactions if t['type'] == transaction_type)
            prev_value = sum(t['amount'] for t in prev_transactions if t['type'] == transaction_type)
        else:
            # Net balance = income - expense
            current_income = sum(t['amount'] for t in current_transactions if t['type'] == 'Income')
            current_expense = sum(t['amount'] for t in current_transactions if t['type'] == 'Expense')
            current_value = current_income - current_expense

            prev_income = sum(t['amount'] for t in prev_transactions if t['type'] == 'Income')
            prev_expense = sum(t['amount'] for t in prev_transactions if t['type'] == 'Expense')
            prev_value = prev_income - prev_expense

        # --- Percent change ---
        if prev_value == 0:
            percent_change = None
        else:
            percent_change = ((current_value - prev_value) / prev_value) * 100

        trend = "up" if percent_change and percent_change > 0 else "down"

        return {
            "current": current_value,
            "previous": prev_value,
            "percent": percent_change,
            "trend": trend,
            "period_days": days
        }