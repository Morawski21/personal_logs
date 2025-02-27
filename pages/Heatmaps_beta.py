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
except Exception as e:
    st.error(f"Error loading data: {str(e)}")
    st.stop()

# Define habits to track and their grouping
ROW1_HABITS = ['Anki', 'Pamiętnik', 'YNAB']
ROW2_HABITS = ['YouTube', 'Gitara', 'Czytanie']
HABITS = ROW1_HABITS + ROW2_HABITS

# Convert duration habits to binary based on 20-minute threshold
for habit in ROW2_HABITS:
    df[f'{habit}_binary'] = (df[habit] >= 20).astype(float)

def prepare_habit_data(habit, is_duration=False):
    """Prepare habit data for heatmap visualization."""
    if is_duration:
        habit_col = f'{habit}_binary'
    else:
        habit_col = habit
    
    # Get dates from dataframe
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

# Process binary habits
for habit in ROW1_HABITS:
    habits_data.append(prepare_habit_data(habit, is_duration=False))

# Process duration habits
for habit in ROW2_HABITS:
    habits_data.append(prepare_habit_data(habit, is_duration=True))

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

# Display the HTML component
components.html(html_content, height=800, scrolling=False)