import streamlit as st
import pandas as pd
import datetime
import os
import utils
import config

# Page config
st.set_page_config(page_title="Personal Logbook", layout="wide")

# Load existing data
try:
    df, loaded_path = utils.load_logbook_data()
    st.success(f"Data loaded successfully from: {loaded_path}")
    # Convert any datetime columns to DD.MM.YYYY format for display
    if 'Data' in df.columns:
        df['Data'] = df['Data'].dt.strftime('%d.%m.%Y')
except FileNotFoundError as e:
    st.error(str(e))
    st.warning("Creating new DataFrame")
    df = pd.DataFrame()
    loaded_path = utils.get_data_paths()[0]  # Default to first path for saving


# Date selector for editing records
selected_date = st.date_input("Select a date to edit", datetime.datetime.now())
selected_date_str = selected_date.strftime('%d.%m.%Y')
selected_record = df[df['Data'] == selected_date_str].iloc[0] if not df.empty and (df['Data'] == selected_date_str).any() else None

# Get active fields configuration
active_fields = config.get_active_fields()
time_columns = [field for field in active_fields if field not in ["20min clean", "YNAB", "Anki", "Pamiętnik", "Plan na jutro", "No porn", "Gaming <1h", "sport", "accessories", "suplementy"]]

# Filter dataframe to include only active fields
df = df[list(active_fields.keys()) + ['Data', 'WEEKDAY', 'Razem']]

# Create form for input
st.header("Add/Update Record")

# Create columns for better layout
col1, col2, col3 = st.columns(3)

# Initialize all form variables with existing values if available
with col1:
    st.subheader("Time Activities")
    for field in ["Tech + Praca", "YouTube", "Czytanie", "Gitara", "Inne"]:
        if active_fields.get(field):
            st.number_input(f"{field} (minutes)", 
                            min_value=0, 
                            value=int(selected_record[field]) if selected_record is not None and pd.notna(selected_record[field]) else 0,
                            key=field.lower().replace(" ", "_"))

    # Calculate total immediately
    razem = sum(st.session_state[field.lower().replace(" ", "_")] for field in ["Tech + Praca", "YouTube", "Czytanie", "Gitara", "Inne"] if active_fields.get(field))
    st.write(f"Total time: {razem} minutes")

with col2:
    st.subheader("Daily Tasks")
    for field in ["20min clean", "YNAB", "Anki", "Pamiętnik", "Plan na jutro", "No porn", "Gaming <1h"]:
        if active_fields.get(field):
            st.checkbox(field, 
                        value=bool(selected_record[field]) if selected_record is not None else False,
                        key=field.lower().replace(" ", "_"))

with col3:
    st.subheader("Additional Info")
    for field in ["sport", "accessories", "suplementy"]:
        if active_fields.get(field):
            st.text_input(field.capitalize(), 
                          value=str(selected_record[field]) if selected_record is not None and pd.notna(selected_record[field]) else "",
                          key=field.lower().replace(" ", "_"))

# Add/Update record button
button_text = "Update Record" if selected_record is not None else "Add Record"
if st.button(button_text):
    weekday = selected_date.strftime('%A').upper()
    
    new_record = {
        'Data': selected_date_str,
        'WEEKDAY': weekday,
        'Razem': razem
    }
    for field in active_fields:
        new_record[field] = st.session_state[field.lower().replace(" ", "_")]

    if selected_record is not None:
        # Update existing record
        df = df[df['Data'] != selected_date_str]  # Remove the old record
        df = pd.concat([df, pd.DataFrame([new_record])], ignore_index=True)  # Add the updated record
    else:
        # Add new record
        df = pd.concat([df, pd.DataFrame([new_record])], ignore_index=True)
    
    try:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(loaded_path), exist_ok=True)
        
        # Save updated DataFrame to Excel
        df.to_excel(loaded_path, index=False)
        st.success(f"Record {'updated' if selected_record is not None else 'added'} successfully in {loaded_path}!")
    except Exception as e:
        st.error(f"Error saving record: {str(e)}")

# Display recent records
st.header("Recent Records")
if not df.empty:
    st.dataframe(df[['Data'] + [col for col in df.columns if col != 'Data']].tail(7))
else:
    st.write("No records found in the logbook.")