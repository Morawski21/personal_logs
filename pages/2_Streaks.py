import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta
import utils
import numpy as np
from config import HABITS_CONFIG

st.set_page_config(
    page_title="Habit Streaks", 
    layout="wide",
    page_icon="icon.png"
)

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
    df, loaded_path = utils.load_logbook_data()
    # Filter out future dates
    df = df[df['Data'] <= datetime.now()]
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
    # Convert series to float, replacing NaN with 0 only for completed days
    values = series.copy()
    
    # For duration habits, convert to binary based on 20min threshold but preserve NaN
    if values.max() > 1:  # If we find values > 1, this is a duration-based habit
        values = values.apply(lambda x: 1.0 if pd.notnull(x) and x >= 20 else (0.0 if pd.notnull(x) else np.nan))
    
    # Convert to list for easier processing
    values = values.values
    
    # Start from the most recent day and count backwards
    current_streak = 0
    
    # Skip NaN values at the end (today if not filled in yet)
    idx = len(values) - 1
    while idx >= 0 and pd.isna(values[idx]):
        idx -= 1
        
    # Count streak from last valid entry
    while idx >= 0:
        if pd.isna(values[idx]):  # Skip NaN values (incomplete days)
            idx -= 1
            continue
        elif values[idx] >= 1:  # Success
            current_streak += 1
        else:  # Break on explicit 0
            break
        idx -= 1
            
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
        if pd.isna(val):  # Skip NaN values
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
        with st.expander(f"{HABITS_CONFIG[habit]['emoji']} {habit}", expanded=True):
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
        with st.expander(f"{HABITS_CONFIG[habit]['emoji']} {habit}", expanded=True):
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
