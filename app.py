import streamlit as st
import pandas as pd
import datetime
import os
import utils

# Page config
st.set_page_config(page_title="Logbook", layout="wide")
st.title("Daily Logbook 2025")

# Load existing data
try:
    df, loaded_path = utils.load_logbook_data()
    st.success(f"Excel file loaded successfully from: {loaded_path}")
    # Convert any datetime columns to DD.MM.YYYY format for display
    if 'Data' in df.columns:
        df['Data'] = df['Data'].dt.strftime('%d.%m.%Y')
except FileNotFoundError as e:
    st.error(str(e))
    st.warning("Creating new DataFrame")
    df = pd.DataFrame()
    loaded_path = utils.get_data_paths()[0]  # Default to first path for saving

# Get today's record if it exists
today = datetime.datetime.now()
today_str = today.strftime('%d.%m.%Y')
today_record = df[df['Data'] == today_str].iloc[0] if not df.empty and (df['Data'] == today_str).any() else None

# Create form for input
st.header("Add/Update Today's Record")

# Create columns for better layout
col1, col2, col3 = st.columns(3)

# Initialize all form variables with existing values if available
with col1:
    st.subheader("Time Activities")
    tech_praca = st.number_input("Tech + Praca (minutes)", 
                                min_value=0, 
                                value=int(today_record['Tech + Praca']) if today_record is not None else 0,
                                key='tech_praca')
    youtube = st.number_input("YouTube (minutes)", 
                             min_value=0, 
                             value=int(today_record['YouTube']) if today_record is not None else 0,
                             key='youtube')
    czytanie = st.number_input("Czytanie (minutes)", 
                              min_value=0, 
                              value=int(today_record['Czytanie']) if today_record is not None else 0,
                              key='czytanie')
    gitara = st.number_input("Gitara (minutes)", 
                            min_value=0, 
                            value=int(today_record['Gitara']) if today_record is not None else 0,
                            key='gitara')
    inne = st.number_input("Inne (minutes)", 
                          min_value=0, 
                          value=int(today_record['Inne']) if today_record is not None else 0,
                          key='inne')

    # Calculate total immediately
    razem = tech_praca + youtube + czytanie + gitara + inne
    st.write(f"Total time: {razem} minutes")

with col2:
    st.subheader("Daily Tasks")
    clean_20min = st.checkbox("20min clean", 
                             value=bool(today_record['20min clean']) if today_record is not None else False,
                             key='clean')
    ynab = st.checkbox("YNAB", 
                       value=bool(today_record['YNAB']) if today_record is not None else False,
                       key='ynab')
    anki = st.checkbox("Anki", 
                       value=bool(today_record['Anki']) if today_record is not None else False,
                       key='anki')
    pamietnik = st.checkbox("Pamiętnik", 
                           value=bool(today_record['Pamiętnik']) if today_record is not None else False,
                           key='pamietnik')
    plan_jutro = st.checkbox("Plan na jutro", 
                            value=bool(today_record['Plan na jutro']) if today_record is not None else False,
                            key='plan_jutro')
    no_porn = st.checkbox("No porn", 
                         value=bool(today_record['No porn']) if today_record is not None else False,
                         key='no_porn')
    gaming = st.checkbox("Gaming <1h", 
                        value=bool(today_record['Gaming <1h']) if today_record is not None else False,
                        key='gaming')

with col3:
    st.subheader("Additional Info")
    sport = st.text_input("Sport", 
                         value=str(today_record['sport']) if today_record is not None and pd.notna(today_record['sport']) else "",
                         key='sport')
    accessories = st.text_input("Accessories", 
                               value=str(today_record['accessories']) if today_record is not None and pd.notna(today_record['accessories']) else "",
                               key='accessories')
    suplementy = st.text_input("Suplementy", 
                              value=str(today_record['suplementy']) if today_record is not None and pd.notna(today_record['suplementy']) else "",
                              key='suplementy')

# Add/Update record button
button_text = "Update Today's Record" if today_record is not None else "Add Today's Record"
if st.button(button_text):
    weekday = today.strftime('%A').upper()
    
    new_record = {
        'Data': today_str,
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
    
    if today_record is not None:
        # Update existing record
        df.loc[df['Data'] == today_str] = new_record
    else:
        # Add new record
        df = pd.concat([df, pd.DataFrame([new_record])], ignore_index=True)
    
    try:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(loaded_path), exist_ok=True)
        
        # Save updated DataFrame to Excel
        df.to_excel(loaded_path, index=False)
        st.success(f"Record {'updated' if today_record is not None else 'added'} successfully in {loaded_path}!")
    except Exception as e:
        st.error(f"Error saving record: {str(e)}")

# Display recent records
st.header("Recent Records")
if not df.empty:
    st.dataframe(df.tail(7))
else:
    st.write("No records found in the logbook.")