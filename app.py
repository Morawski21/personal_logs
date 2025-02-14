import streamlit as st
import pandas as pd
import datetime
import os

# Page config
st.set_page_config(page_title="Logbook", layout="wide")
st.title("Daily Logbook 2025")

# Define possible data paths
data_paths = [
    os.path.join('data', 'Logbook 2025.xlsx'),  # Local development path
    os.path.join('/app/data', 'Logbook 2025.xlsx'),  # Docker container path
]

# Load existing data
df = None
loaded_path = None

for path in data_paths:
    try:
        if os.path.exists(path):
            df = pd.read_excel(path)
            loaded_path = path
            st.success(f"Excel file loaded successfully from: {path}")
            break
    except Exception as e:
        continue

if df is None:
    st.error("Could not load Excel file from any known location. Creating new DataFrame.")
    st.warning("Make sure 'Logbook 2025.xlsx' exists in the data directory")
    df = pd.DataFrame()
else:
    # Convert any datetime columns to DD.MM.YYYY format
    if 'Data' in df.columns:
        df['Data'] = pd.to_datetime(df['Data']).dt.strftime('%d.%m.%Y')

# Create form for input
st.header("Add New Daily Record")

# Create columns for better layout
col1, col2, col3 = st.columns(3)

# Initialize all form variables
with col1:
    st.subheader("Time Activities")
    tech_praca = st.number_input("Tech + Praca (minutes)", min_value=0, value=0, key='tech_praca')
    youtube = st.number_input("YouTube (minutes)", min_value=0, value=0, key='youtube')
    czytanie = st.number_input("Czytanie (minutes)", min_value=0, value=0, key='czytanie')
    gitara = st.number_input("Gitara (minutes)", min_value=0, value=0, key='gitara')
    inne = st.number_input("Inne (minutes)", min_value=0, value=0, key='inne')

    # Calculate total immediately
    razem = tech_praca + youtube + czytanie + gitara + inne
    st.write(f"Total time: {razem} minutes")

with col2:
    st.subheader("Daily Tasks")
    clean_20min = st.checkbox("20min clean", key='clean')
    ynab = st.checkbox("YNAB", key='ynab')
    anki = st.checkbox("Anki", key='anki')
    pamietnik = st.checkbox("Pamiętnik", key='pamietnik')
    plan_jutro = st.checkbox("Plan na jutro", key='plan_jutro')
    no_porn = st.checkbox("No porn", key='no_porn')
    gaming = st.checkbox("Gaming <1h", key='gaming')

with col3:
    st.subheader("Additional Info")
    sport = st.text_input("Sport", value="", key='sport')
    accessories = st.text_input("Accessories", value="", key='accessories')
    suplementy = st.text_input("Suplementy", value="", key='suplementy')

# Add record button
if st.button("Add Today's Record"):
    # Get today's date and weekday
    today = datetime.datetime.now()
    weekday = today.strftime('%A').upper()
    
    # Create new record
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
        # Use the path where we successfully loaded the file, or default to first path
        save_path = loaded_path if loaded_path else data_paths[0]
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        # Save updated DataFrame to Excel
        df.to_excel(save_path, index=False)
        st.success(f"Record added successfully to {save_path}!")
    except Exception as e:
        st.error(f"Error saving record: {str(e)}")

# Display recent records
st.header("Recent Records")
if not df.empty:
    st.dataframe(df.tail(7))
else:
    st.write("No records found in the logbook.")