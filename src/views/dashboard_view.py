from src.core import config
from src.models.category_models import CategoryModel
from streamlit import st

def show_dashboard():
    col1, col2 = st.columns(2)
    with col1:
        st.title("Dashboard")
        st.write("Welcome to your dashboard!")
        st.selectbox("Select a month", ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"])
    with col2:
        st.title("Statistics")
        st.write("You can see your statistics here.")

if __name__ == "__main__":
    show_dashboard()