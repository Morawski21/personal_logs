from datetime import datetime, timedelta

import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

import src.utils as utils
import src.config as config

from src.data_handler import get_logbook_data

utils.set_custom_page_config("Habit Streaks")

# Add CSS to hide delta arrows
st.write(
    """
    <style>
    [data-testid="stMetricDelta"] svg {
        display: none;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

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
    # Replace the original column name in HABITS with the binary version
    HABITS[HABITS.index(habit)] = f'{habit}_binary'

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

# Create metrics for each habit
st.header("🎯 Habit Streaks")

cols1 = st.columns(3)
for idx, habit in enumerate(ROW1_HABITS):
    current_streak = calculate_current_streak(df[habit])
    longest_streak = calculate_longest_streak(df[habit])
    
    with cols1[idx]:
        with st.expander(f"{config.HABITS_CONFIG[habit]['emoji']} {habit}", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                st.metric(
                    label="Current streak", 
                    value=f"{current_streak}d",
                    delta="Record-breaking 💥" if current_streak >= longest_streak and current_streak > 0 
                          else "Active 🔥" if current_streak > 0 else None,
                    delta_color="normal" if current_streak >= longest_streak and current_streak > 0 
                               else "normal"
                )
            with col2:
                st.metric(
                    label="Best streak",
                    value=f"{longest_streak}d",
                    delta="Best 🏆",
                    delta_color="off"
                )

cols2 = st.columns(3)
for idx, habit in enumerate(ROW2_HABITS):
    binary_habit = f'{habit}_binary'
    current_streak = calculate_current_streak(df[binary_habit])
    longest_streak = calculate_longest_streak(df[binary_habit])
    
    with cols2[idx]:
        with st.expander(f"{config.HABITS_CONFIG[habit]['emoji']} {habit}", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                st.metric(
                    label="Current streak", 
                    value=f"{current_streak}d",
                    delta="Record-breaking 💥" if current_streak >= longest_streak and current_streak > 0 
                          else "Active 🔥" if current_streak > 0 else None,
                    delta_color="normal" if current_streak >= longest_streak and current_streak > 0 
                               else "normal"
                )
            with col2:
                st.metric(
                    label="Best streak",
                    value=f"{longest_streak}d",
                    delta="Best 🏆",
                    delta_color="off"
                )