import streamlit as st
import pandas as pd
import random
import os

# Debug information
st.title("GitHub actions deployed this app")
st.write("Current working directory:", os.getcwd())

# Define path to the data directory and Excel file
data_path = os.path.join('data', 'Logbook 2025.xlsx')

try:
    # Load the Excel file
    if os.path.exists(data_path):
        df = pd.read_excel(data_path)
        st.write("Excel file loaded successfully!")
        st.write("Data shape:", df.shape)
    else:
        st.error(f"Excel file not found at: {data_path}")
        st.write("Contents of /app/data:", os.listdir('/app/data'))
except Exception as e:
    st.error(f"Error loading Excel file: {str(e)}")

st.dataframe(df.tail())

st.write(df.columns.to_list())