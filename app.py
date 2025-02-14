import streamlit as st
import pandas as pd
import datetime
import os

# Page config
st.set_page_config(page_title="Daily Logbook", layout="wide")
st.title("Daily Logbook 2025")

# Define path to the data directory and Excel file
data_path = os.path.join('data', 'Logbook 2025.xlsx')

# Load existing data
try:
    if os.path.exists(data_path):
        df = pd.read_excel(data_path)
        # Convert any datetime columns to DD.MM.YYYY format
        if 'Data' in df.columns:
            df['Data'] = pd.to_datetime(df['Data']).dt.strftime('%d.%m.%Y')
        st.success("Excel file loaded successfully!")
    else:
        st.error(f"Excel file not found at: {data_path}")
        df = pd.DataFrame()
except Exception as e:
    st.error(f"Error loading Excel file: {str(e)}")
    df = pd.DataFrame()

# Add new record section
st.header("Add New Daily Record")

# Create columns for better layout
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Time Activities")
    tech_praca = st.number_input("Tech + Praca (minutes)", min_value=0, value=0)
    youtube = st.number_input("YouTube (minutes)", min_value=0, value=0)
    czytanie = st.number_input("Czytanie (minutes)", min_value=0, value=0)
    gitara = st.number_input("Gitara (minutes)", min_value=0, value=0)
    inne = st.number_input("Inne (minutes)", min_value=0, value=0)

with col2:
    st.subheader("Daily Tasks")
    clean_20min = st.checkbox("20min clean")
    ynab = st.checkbox("YNAB")
    anki = st.checkbox("Anki")
    pamietnik = st.checkbox("Pamiętnik")
    plan_jutro = st.checkbox("Plan na jutro")
    no_porn = st.checkbox("No porn")
    gaming = st.checkbox("Gaming <1h")

with col3:
    st.subheader("Additional Info")
    sport = st.text_input("Sport")
    accessories = st.text_input("Accessories")
    suplementy = st.text_input("Suplementy")

# Calculate total time
razem = tech_praca + youtube + czytanie + gitara + inne
st.write(f"Total time: {razem} minutes")

# Add record button
if st.button("Add Today's Record"):
    # Get today's date and weekday
    today = datetime.datetime.now()
    weekday = today.strftime('%A').upper()
    
    # Create new record
    # Ensure date is in DD.MM.YYYY format
    formatted_date = today.strftime('%d.%m.%Y')
    
    new_record = {
        'Data': formatted_date,
        'WEEKDAY': weekday,
        'Tech + Praca': tech_praca,
        'YouTube': youtube,
        'Czytanie': czytanie,
        'Gitara': gitara,
        'Inne': inne,
        'Razem': razem,
        'sport': sport,
        'accessories': accessories,
        'suplementy': suplementy,
        '20min clean': int(clean_20min),
        'YNAB': int(ynab),
        'Anki': int(anki),
        'Pamiętnik': int(pamietnik),
        'Plan na jutro': int(plan_jutro),
        'No porn': int(no_porn),
        'Gaming <1h': int(gaming)
    }
    
    # Add new record to DataFrame
    df = pd.concat([df, pd.DataFrame([new_record])], ignore_index=True)
    
    try:
        # Save updated DataFrame to Excel
        df.to_excel(data_path, index=False)
        st.success("Record added successfully!")
    except Exception as e:
        st.error(f"Error saving record: {str(e)}")

# Display recent records
st.header("Recent Records")
if not df.empty:
    st.dataframe(df.tail(7))
else:
    st.write("No records found in the logbook.")