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

# Define habits to track and their grouping
ROW1_HABITS = ['Anki', 'Cronometer', 'YNAB']
ROW2_HABITS = ['YouTube', 'Gitara', 'Czytanie']
ROW3_HABITS = ['No porn', 'No 9gag', '20min clean']
HABITS = ROW1_HABITS + ROW2_HABITS + ROW3_HABITS

# Define which habits should be blurred (personal)
PERSONAL_HABITS = ['No porn']  # Now only 'No porn' is marked as personal

# Load data using shared functionality
try:
    df, loaded_path = get_logbook_data()
    
    # Identify today's row
    today = pd.Timestamp.now().normalize()
    today_row = df[df['Data'].dt.normalize() == today]
    is_today_in_data = not today_row.empty
    
    # Create a dict to track which habits were completed today
    today_completions = {}
    if is_today_in_data:
        # Check binary habits
        for habit in ROW1_HABITS + ROW3_HABITS:
            if habit in today_row.columns:
                # Convert boolean to string "true" or "false" for JSON serialization
                is_completed = today_row[habit].iloc[0] == 1.0
                today_completions[habit] = "true" if is_completed else "false"
        
        # Check duration habits 
        for habit in ROW2_HABITS:
            if habit in today_row.columns:
                # Convert boolean to string "true" or "false" for JSON serialization
                is_completed = today_row[habit].iloc[0] >= 20.0
                today_completions[habit] = "true" if is_completed else "false"
    else:
        # If today isn't in the data, nothing was completed today
        for habit in ROW1_HABITS + ROW2_HABITS + ROW3_HABITS:
            today_completions[habit] = "false"
except Exception as e:
    st.error(f"Error loading data: {str(e)}")
    st.stop()

# Helper function to detect NA values in various formats
def is_na_value(val):
    """Helper function to check if a value is NA/NaN in various formats"""
    # Check for pandas NA
    if pd.isna(val):
        return True
    
    # Check for string 'NA' (case-insensitive)
    if isinstance(val, str) and val.upper() == 'NA':
        return True
    
    # Check for numpy NaN
    try:
        if np.isnan(val):
            return True
    except (TypeError, ValueError):
        pass
    
    # Check for None
    if val is None:
        return True
        
    return False

# Convert duration habits to binary based on 20-minute threshold while preserving NA values
for habit in ROW2_HABITS:
    # Create a mask of NA values in the original column
    na_mask = df[habit].apply(is_na_value)
    
    # Convert to binary (20 min threshold), preserving NA values
    df[f'{habit}_binary'] = df[habit].copy()
    df.loc[~na_mask, f'{habit}_binary'] = (df.loc[~na_mask, habit] >= 20).astype(float)
    # Ensure NA values remain NA in the binary column
    df.loc[na_mask, f'{habit}_binary'] = np.nan

def calculate_current_streak(series):
    """Calculate the current streak from a series of values."""
    values = series.copy()
    
    # For duration habits, convert to binary based on 20min threshold but preserve NaN
    if values.max() > 1:  # If we find values > 1, this is a duration-based habit
        # Already handled in the binary conversion above
        pass
    
    # Convert to list for easier processing
    values = values.values
    
    # Get today's index
    today_idx = len(values) - 1
    
    # Initialize streak counter
    current_streak = 0
    
    # Skip today if it's 0 (potentially unfilled)
    if today_idx >= 0 and values[today_idx] == 0:
        today_idx -= 1
        
    # Count streak from last valid entry
    for idx in range(today_idx, -1, -1):
        if is_na_value(values[idx]):  # Skip NA values without breaking the streak
            continue
        elif values[idx] >= 1:  # Success
            current_streak += 1
        else:  # Break on explicit 0
            break
            
    return current_streak

def calculate_longest_streak(series):
    """Calculate the longest streak from a series of values."""
    # Same conversion as in current_streak
    values = series.copy()
    
    if values.max() > 1:
        # Already handled in the binary conversion above
        pass
    
    max_streak = 0
    current = 0
    
    for val in values:
        if is_na_value(val):  # Skip NA values without breaking or adding to streak
            continue
        elif val >= 1:  # Success
            current += 1
            max_streak = max(max_streak, current)
        else:  # Reset on explicit 0
            current = 0
            
    return max_streak

# Create data for habit cards
habits_data = []

# Process binary habits
for habit in ROW1_HABITS:
    # Apply the same NA handling to binary habits as we did for duration habits
    na_mask = df[habit].apply(is_na_value)
    df[f'{habit}_processed'] = df[habit].copy()
    df.loc[na_mask, f'{habit}_processed'] = np.nan  # Ensure NA values are consistently detected
    
    current_streak = calculate_current_streak(df[f'{habit}_processed'])
    longest_streak = calculate_longest_streak(df[f'{habit}_processed'])
    habits_data.append({
        "name": habit,
        "emoji": config.HABITS_CONFIG[habit]['emoji'],
        "currentStreak": current_streak,
        "bestStreak": longest_streak,
        "completedToday": today_completions.get(habit, "false"),
        "isPersonal": habit in PERSONAL_HABITS  # Check if this habit should be personal
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
        "bestStreak": longest_streak,
        "completedToday": today_completions.get(habit, "false"),
        "isPersonal": habit in PERSONAL_HABITS  # Check if this habit should be personal
    })

# Process binary habits for row 3
for habit in ROW3_HABITS:
    # Apply the same NA handling to binary habits as we did for duration habits
    na_mask = df[habit].apply(is_na_value) if habit in df.columns else pd.Series(True, index=df.index)
    
    if habit in df.columns:
        df[f'{habit}_processed'] = df[habit].copy()
        df.loc[na_mask, f'{habit}_processed'] = np.nan  # Ensure NA values are consistently detected
        
        current_streak = calculate_current_streak(df[f'{habit}_processed'])
        longest_streak = calculate_longest_streak(df[f'{habit}_processed'])
    else:
        # If habit column doesn't exist yet, initialize with zeros
        current_streak = 0
        longest_streak = 0
        
    habits_data.append({
        "name": habit,
        "emoji": config.HABITS_CONFIG[habit]['emoji'],
        "currentStreak": current_streak,
        "bestStreak": longest_streak,
        "completedToday": today_completions.get(habit, "false"),
        "isPersonal": habit in PERSONAL_HABITS  # Check if this specific habit should be personal
    })

# Store all habits data to session state
st.session_state['habits_data'] = habits_data

# Filter the data to get main and personal habits separately if needed for other parts of the app
st.session_state['main_habits_data'] = [habit for habit in habits_data if not habit.get('isPersonal', False)]
st.session_state['personal_habits_data'] = [habit for habit in habits_data if habit.get('isPersonal', False)]

# Page header
st.title("Habit Streaks")

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

# Display the HTML component (increased height to accommodate perfect day messages and the new row)
components.html(html_content, height=800, scrolling=False)