import streamlit as st
import pandas as pd
import random
import os

st.title("Hello Synology!")
st.write(f"Here's your random number: {random.randint(1, 100)}")

# Use absolute path to the mounted volume
DATA_DIR = "/data"

# Debug information
st.write("Current working directory:", os.getcwd())
st.write("DATA_DIR path:", DATA_DIR)

# Original Excel file listing code
excel_files = [f for f in os.listdir(DATA_DIR) if f.endswith(('.xlsx', '.xls'))]

if excel_files:
    selected_file = st.selectbox("Select Excel file", excel_files)
    file_path = os.path.join(DATA_DIR, selected_file)
    try:
        df = pd.read_excel(file_path)
        st.dataframe(df.head())
        st.write(f"Total rows: {len(df)}")
    except Exception as e:
        st.error(f"Error reading file: {str(e)}")
else:
    st.warning(f"No Excel files found in {DATA_DIR}")