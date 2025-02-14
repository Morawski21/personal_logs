import streamlit as st
import pandas as pd
import datetime
import os

# Page config
st.set_page_config(page_title="Logbook", layout="wide")
st.title("Daily Logbook 2025 test")

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

# Rest of your existing code remains the same until the save part

# When saving, use the loaded path or default to the first path
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