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

# Get habits dynamically from config and check if they exist in the data
active_habits = config.get_active_fields()
available_habits = []

for habit in active_habits:
    if habit in df.columns:
        available_habits.append(habit)

# Group habits by type (binary vs duration)
binary_habits = []
duration_habits = []

for habit in available_habits:
    if habit in active_habits and active_habits[habit]['type'] == 'binary':
        binary_habits.append(habit)
    elif habit in active_habits and active_habits[habit]['type'] == 'time':
        duration_habits.append(habit)

# Combine all habits for processing
HABITS = binary_habits + duration_habits

# Convert duration habits to binary based on 20-minute threshold
for habit in duration_habits:
    try:
        # Make sure values are numeric
        df[habit] = pd.to_numeric(df[habit], errors='coerce')
        df[f'{habit}_binary'] = (df[habit] >= 20).astype(float)
    except Exception as e:
        st.warning(f"Error processing habit {habit}: {str(e)}")

def calculate_current_streak(series):
    """Calculate the current streak from a series of values."""
    values = series.copy()
    
    # First, try to convert all values to numeric, coercing errors to NaN
    try:
        values = pd.to_numeric(values, errors='coerce')
        
        # Check if this is a duration-based habit (has values > 1)
        if values.max() > 1:  
            values = values.apply(lambda x: 1.0 if pd.notnull(x) and x >= 20 else (0.0 if pd.notnull(x) else np.nan))
    except:
        # If conversion fails or max() fails, treat as binary
        # Convert non-numeric values: any truthy value = 1, falsy = 0, preserving NaN
        values = values.apply(lambda x: 
            1.0 if pd.notnull(x) and (x == 1 or x == "1" or x == True or x == "True" or str(x).lower() == "true") 
            else (0.0 if pd.notnull(x) else np.nan))
    
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
        try:
            if values[idx] >= 1:  # Success
                current_streak += 1
            elif np.isnan(values[idx]):  # Skip NA values without breaking the streak
                continue
            else:  # Break on explicit 0
                break
        except (TypeError, ValueError):
            # If comparison fails, count as 0 and break streak
            break
            
    return current_streak

def calculate_longest_streak(series):
    """Calculate the longest streak from a series of values."""
    # Same conversion as in current_streak
    values = series.copy()
    
    # First, try to convert all values to numeric, coercing errors to NaN
    try:
        values = pd.to_numeric(values, errors='coerce')
        
        # Check if this is a duration-based habit (has values > 1)
        if values.max() > 1:  
            values = values.apply(lambda x: 1.0 if pd.notnull(x) and x >= 20 else (0.0 if pd.notnull(x) else np.nan))
    except:
        # If conversion fails or max() fails, treat as binary
        # Convert non-numeric values: any truthy value = 1, falsy = 0, preserving NaN
        values = values.apply(lambda x: 
            1.0 if pd.notnull(x) and (x == 1 or x == "1" or x == True or x == "True" or str(x).lower() == "true") 
            else (0.0 if pd.notnull(x) else np.nan))
    
    max_streak = 0
    current = 0
    
    for val in values:
        try:
            if pd.isna(val):  # Skip NaN values without breaking streak
                continue
            elif val >= 1:
                current += 1
                max_streak = max(max_streak, current)
            else:  # Reset on explicit 0
                current = 0
        except (TypeError, ValueError):
            # If comparison fails, treat as 0
            current = 0
            
    return max_streak

# Page header
st.title("Habit Streaks")

# Add habit management options
with st.expander("Manage Habits", expanded=False):
    # Create tabs for selecting/hiding habits and activating/deactivating habits
    tab1, tab2 = st.tabs(["Display Habits", "Activate/Deactivate Habits"])
    
    with tab1:
        st.write("Select which habits to display:")
        
        # Create columns for better layout
        cols = st.columns(3)
        
        # Create checkboxes for each available habit
        selected_habits = {}
        
        for i, habit in enumerate(active_habits):
            col_idx = i % 3
            if habit in available_habits:
                selected = st.session_state.get(f'habit_{habit}_selected', True)
                selected_habits[habit] = cols[col_idx].checkbox(
                    f"{active_habits[habit]['emoji']} {habit}", 
                    value=selected,
                    key=f'habit_{habit}_selected'
                )
                
    with tab2:
        st.write("""
        ⚠️ This tab shows which habits are available in your Excel/CSV file. 
        
        To add a new habit:
        1. Add a new column in Excel
        2. Make sure the column name exactly matches a habit name in your config
        3. Enter your data (1 for binary habits, minutes for time habits)
        4. Save the Excel file
        5. Restart the app to see changes
        """)
        
        # Display two columns with available habits (exist in data) and unavailable habits
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Available in Data")
            for habit in sorted(available_habits):
                st.success(f"{active_habits[habit]['emoji']} {habit}")
                
        with col2:
            st.subheader("Configured but Not in Data")
            missing_habits = [h for h in active_habits if h not in available_habits]
            for habit in sorted(missing_habits):
                st.warning(f"{active_habits[habit]['emoji']} {habit}")

# Create data for habit cards
habits_data = []

# Process binary habits
for habit in binary_habits:
    if habit in selected_habits and selected_habits[habit]:
        try:
            current_streak = calculate_current_streak(df[habit])
            longest_streak = calculate_longest_streak(df[habit])
            habits_data.append({
                "name": habit,
                "emoji": config.HABITS_CONFIG[habit]['emoji'],
                "currentStreak": current_streak,
                "bestStreak": longest_streak
            })
        except Exception as e:
            st.warning(f"Error calculating streaks for {habit}: {str(e)}")

# Process duration habits
for habit in duration_habits:
    if habit in selected_habits and selected_habits[habit]:
        try:
            binary_habit = f'{habit}_binary'
            current_streak = calculate_current_streak(df[binary_habit])
            longest_streak = calculate_longest_streak(df[binary_habit])
            habits_data.append({
                "name": habit,
                "emoji": config.HABITS_CONFIG[habit]['emoji'],
                "currentStreak": current_streak,
                "bestStreak": longest_streak
            })
        except Exception as e:
            st.warning(f"Error calculating streaks for {habit}: {str(e)}")

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

# Dynamically adjust height based on number of habits
num_habits = len(habits_data)
num_rows = (num_habits + 2) // 3  # Calculate number of rows (3 per row, round up)
card_height = 200  # Height per card in pixels
grid_gap = 20  # Gap between cards
total_height = num_rows * card_height + (num_rows - 1) * grid_gap

# Display the HTML component with adjusted height
components.html(html_content, height=total_height, scrolling=True)