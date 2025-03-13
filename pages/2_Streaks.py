import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import os
import json
import numpy as np

import src.utils as utils
import src.config as config
from src.data_handler import get_logbook_data



# Set page config
utils.set_custom_page_config("Streaks 2.0 (beta)")

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

def calculate_current_streak(series):
    """Calculate the current streak from a series of values."""
    values = series.copy()
    
    # For duration habits, convert to binary based on 20min threshold but preserve NaN
    if values.max() > 1:  # If we find values > 1, this is a duration-based habit
        values = values.apply(lambda x: 1.0 if pd.notnull(x) and x >= 20 else (0.0 if pd.notnull(x) else np.nan))
    
    # Convert to list for easier processing
    values = values.values
    
    # Get today's index
    today_idx = len(values) - 1
    
    # Initialize streak counter
    current_streak = 0
    
    # Skip today if it's 0 (potentially unfilled)
    if values[today_idx] == 0:
        today_idx -= 1
        
    # Count streak from last valid entry
    for idx in range(today_idx, -1, -1):
        if values[idx] >= 1:  # Success
            current_streak += 1
        elif np.isnan(values[idx]):  # Skip NA values without breaking the streak
            continue
        else:  # Break on explicit 0
            break
            
    return current_streak

def calculate_longest_streak(series):
    """Calculate the longest streak from a series of values."""
    # Same conversion as in current_streak
    values = series.copy()
    
    if values.max() > 1:
        values = values.apply(lambda x: 1.0 if pd.notnull(x) and x >= 20 else (0.0 if pd.notnull(x) else np.nan))
    
    max_streak = 0
    current = 0
    
    for val in values:
        if pd.isna(val):  # Skip NaN values without breaking streak
            continue
        elif val >= 1:
            current += 1
            max_streak = max(max_streak, current)
        else:  # Reset on explicit 0
            current = 0
            
    return max_streak

# Create data for habit cards
habits_data = []

# Process binary habits
for habit in ROW1_HABITS:
    current_streak = calculate_current_streak(df[habit])
    longest_streak = calculate_longest_streak(df[habit])
    habits_data.append({
        "name": habit,
        "emoji": config.HABITS_CONFIG[habit]['emoji'],
        "currentStreak": current_streak,
        "bestStreak": longest_streak
    })

# Process duration habits
for habit in ROW2_HABITS:
    binary_habit = f'{habit}_binary'
    current_streak = calculate_current_streak(df[binary_habit])
    longest_streak = calculate_longest_streak(df[binary_habit])
    habits_data.append({
        "name": habit,
        "emoji": config.HABITS_CONFIG[habit]['emoji'],
        "currentStreak": current_streak,
        "bestStreak": longest_streak
    })

# Page header
st.title("Habit Streaks",)

# Load the HTML template from external file
import os

# Path to the HTML template file
template_path = os.path.join("assets", "habit-cards.html")

# Read the template file
try:
    with open(template_path, "r", encoding="utf-8") as file:
        html_template = file.read()
except Exception as e:
    st.error(f"Error loading HTML template: {str(e)}")
    st.stop()

# Replace the placeholder with actual habits data
html_content = html_template.replace('HABITS_DATA_PLACEHOLDER', json.dumps(habits_data))

# Display the HTML component (increased height to accommodate perfect day messages)
components.html(html_content, height=600, scrolling=False)