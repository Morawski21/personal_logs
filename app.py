import streamlit as st
import pandas as pd
import random

st.title("Hello Synology!")
st.write(f"Here's your random number: {random.randint(1, 100)}")

df = pd.read_excel("C:\\Users\\Jakub\\Desktop\\Logbook 2025.xlsx")

st.dataframe(df.head())