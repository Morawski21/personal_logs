import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import os
import json
from datetime import datetime, timedelta

import src.utils as utils
import src.config as config
from src.data_handler import get_logbook_data

# Set page config
utils.set_custom_page_config("Habit Heatmaps (beta)")

# Load data using shared functionality
try:
    df, loaded_path = get_logbook_data()
    
    # Check if 'Data' column exists and set it as index
    if 'Data' in df.columns:
        df = df.set_index('Data')
    
except Exception as e:
    st.error(f"Error loading data: {str(e)}")
    st.stop()

# Define habits to track and their grouping
ROW1_HABITS = ['Anki', 'Pamiętnik', 'YNAB']
ROW2_HABITS = ['YouTube', 'Gitara', 'Czytanie']
HABITS = ROW1_HABITS + ROW2_HABITS

# Check if the dataframe has any entries
if df.empty:
    st.error("No data available for visualization. Please check your data source.")
    st.stop()

# Verify the required columns exist
missing_habits = [habit for habit in HABITS if habit not in df.columns]
if missing_habits:
    st.error(f"The following habit columns are missing from your data: {', '.join(missing_habits)}")
    st.warning("Please check your data source or modify the habit list.")
    # Continue with available habits only
    ROW1_HABITS = [h for h in ROW1_HABITS if h not in missing_habits]
    ROW2_HABITS = [h for h in ROW2_HABITS if h not in missing_habits]
    HABITS = ROW1_HABITS + ROW2_HABITS

# Convert duration habits to binary based on 20-minute threshold
for habit in ROW2_HABITS:
    if habit in df.columns:  # Only process if column exists
        df[f'{habit}_binary'] = (df[habit] >= 20).astype(float)

def prepare_habit_data(habit, is_duration=False):
    """Prepare habit data for heatmap visualization."""
    if is_duration:
        habit_col = f'{habit}_binary'
    else:
        habit_col = habit
    
    # Get dates from dataframe - ensure we have a datetime index
    if df.index.dtype == 'datetime64[ns]':
        # Index is datetime - format it properly for JS
        dates = df.index.strftime('%Y-%m-%d').tolist()
    else:
        # If not a datetime index but we have Data column
        if 'Data' in df.columns:
            dates = df['Data'].dt.strftime('%Y-%m-%d').tolist()
        else:
            # Otherwise just convert index to string
            dates = df.index.astype(str).tolist()
    
    # Get habit values and convert to completed/not completed
    values = df[habit_col].tolist()
    
    # Create days data array
    days_data = []
    for i, date in enumerate(dates):
        # Skip NaN values by treating them as not completed
        if pd.isna(values[i]):
            completed = False
        elif is_duration:
            # For duration habits, consider >= 20 as completed
            completed = values[i] >= 1
        else:
            # For binary habits, any non-zero value is completed
            completed = values[i] >= 1
        
        days_data.append({
            "date": date,
            "completed": completed
        })
    
    return {
        "name": habit,
        "emoji": config.HABITS_CONFIG[habit]['emoji'],
        "color": config.HABITS_CONFIG[habit]['color'],
        "daysData": days_data
    }

# Create data for habit heatmaps
habits_data = []

# Process binary habits - with error handling
for habit in ROW1_HABITS:
    try:
        if habit in df.columns:  # Only process if column exists
            habit_data = prepare_habit_data(habit, is_duration=False)
            habits_data.append(habit_data)
        else:
            st.warning(f"Skipping {habit} - column not found in data")
    except Exception as e:
        st.error(f"Error processing {habit}: {str(e)}")

# Process duration habits - with error handling
for habit in ROW2_HABITS:
    try:
        if habit in df.columns and f"{habit}_binary" in df.columns:  # Only process if columns exist
            habit_data = prepare_habit_data(habit, is_duration=True)
            habits_data.append(habit_data)
        else:
            st.warning(f"Skipping {habit} - column or binary column not found in data")
    except Exception as e:
        st.error(f"Error processing {habit}: {str(e)}")

# Page header
st.title("📊 Habit Heatmaps (Beta)")
st.caption("Visualize your habit completion patterns with interactive heatmaps")

# Load the HTML template from external file
template_path = os.path.join("assets", "habit-heatmap.html")

# Read the template file
try:
    with open(template_path, "r") as file:
        html_template = file.read()
except Exception as e:
    st.error(f"Error loading HTML template: {str(e)}")
    st.stop()

# Replace the placeholder with actual habits data
html_content = html_template.replace('HABITS_DATA_PLACEHOLDER', json.dumps(habits_data))

# Add debug information if needed
if st.checkbox("Show debug information"):
    st.write("DataFrame columns:", df.columns.tolist())
    st.write("DataFrame index type:", df.index.dtype)
    st.write("Habits_data sample (first habit):", habits_data[0] if habits_data else "No data")
    st.write("First 5 dates in data:", df.index[:5] if not df.empty else "No data")
    
    # Check if the habits exist in the dataframe
    for habit in HABITS:
        habit_exists = habit in df.columns
        binary_exists = f"{habit}_binary" in df.columns if habit in ROW2_HABITS else "N/A"
        st.write(f"Habit '{habit}' exists in df: {habit_exists}, Binary column exists: {binary_exists}")

# Display the HTML component with increased height
components.html(html_content, height=800, scrolling=False)

# Add a warning if no data is being displayed
if not habits_data or not any(len(habit.get('daysData', [])) > 0 for habit in habits_data):
    st.warning("No habit data found to display in heatmaps. Please check your data source.")