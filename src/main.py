import streamlit as st
import pandas as pd

item_count = 100
column_count = 100
row_count = 1000

columns = []
for col in range(column_count):
    columns.append(f'column_{col:04d}')
df = pd.DataFrame(columns=columns)
for row in range(row_count):
    cells = []
    for col in range(column_count):
        cells.append(f'cell_{row:04d}_{col:04d}')
    df.loc[row] = cells

with st.sidebar:
    st.write("sidebar")
    for i in range(item_count):
        st.write(f"item_{i:04d}")

with st.container():
    st.write("header")
    st.dataframe(df, use_container_width=False)
    st.write("footer")