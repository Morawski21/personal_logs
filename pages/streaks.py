import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta
import utils
import numpy as np

st.set_page_config(page_title="Habit Streaks", layout="wide")

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
    current_streak = 0
    for val in series[::-1]:  # Iterate from most recent
        if val == 1:
            current_streak += 1
        elif val == 0:  # Break streak on 0
            break
        # Skip NA values (they don't break the streak)
        elif pd.isna(val):
            continue
    return current_streak

def calculate_longest_streak(series):
    """Calculate the longest streak from a series of values."""
    max_streak = 0
    current = 0
    for val in series:
        if val == 1:
            current += 1
            max_streak = max(max_streak, current)
        elif val == 0:
            current = 0
        # Skip NA values
        elif pd.isna(val):
            continue
    return max_streak

# Create metrics for each habit in two rows
st.subheader("Habit Streaks")

# First row
st.write("**Daily Habits**")
cols1 = st.columns(3)
for idx, habit in enumerate(ROW1_HABITS):
    current_streak = calculate_current_streak(df[habit])
    longest_streak = calculate_longest_streak(df[habit])
    
    with cols1[idx]:
        st.caption(habit)
        subcol1, subcol2 = st.columns(2)
        with subcol1:
            st.metric(
                label="Current streak", 
                value=f"{current_streak}d",
                label_visibility="collapsed",
                delta="Record-breaking 💥" if current_streak >= longest_streak and current_streak > 0 
                      else "Active 🔥" if current_streak > 0 else None,
                delta_color="normal" if current_streak >= longest_streak and current_streak > 0 
                           else "normal"
            )
        with subcol2:
            st.metric(
                label="Best streak",
                value=f"{longest_streak}d",
                label_visibility="collapsed",
                delta="Best 🏆",
                delta_color="off"
            )

# Second row
st.write("**20+ Minute Activities**")
cols2 = st.columns(3)
for idx, habit in enumerate(ROW2_HABITS):
    binary_habit = f'{habit}_binary'
    current_streak = calculate_current_streak(df[binary_habit])
    longest_streak = calculate_longest_streak(df[binary_habit])
    
    with cols2[idx]:
        st.caption(habit)
        subcol1, subcol2 = st.columns(2)
        with subcol1:
            st.metric(
                label="Current streak", 
                value=f"{current_streak}d",
                label_visibility="collapsed",
                delta="Record-breaking 💥" if current_streak >= longest_streak and current_streak > 0 
                      else "Active 🔥" if current_streak > 0 else None,
                delta_color="normal" if current_streak >= longest_streak and current_streak > 0 
                           else "normal"
            )
        with subcol2:
            st.metric(
                label="Best streak",
                value=f"{longest_streak}d",
                label_visibility="collapsed",
                delta="Best 🏆",
                delta_color="off"
            )

# Create calendar heatmaps
st.subheader("Habit Completion Calendar")

# Prepare data for heatmap
last_6_months = datetime.now() - timedelta(days=180)
df_heatmap = df[df['Data'] >= last_6_months].copy()

# Create calendar heatmap for each habit
for habit in ROW1_HABITS + [f'{h}_binary' for h in ROW2_HABITS]:
    st.write(f"**{habit}**")
    
    # Prepare the data
    df_plot = df_heatmap.copy()
    df_plot['week'] = df_plot['Data'].dt.isocalendar().week
    df_plot['weekday'] = df_plot['Data'].dt.weekday
    
    # Create pivot table
    pivot_table = df_plot.pivot_table(
        values=habit,
        index='weekday',
        columns='week',
        aggfunc='first'
    )
    
    # Create custom colormap
    colors = ['#ff6b6b', '#e9ecef', '#69db7c']  # red, gray, green
    cmap = sns.blend_palette(colors, as_cmap=True)
    
    # Create the heatmap
    fig, ax = plt.subplots(figsize=(15, 2.5))
    fig.patch.set_facecolor('#f0f2f6')  # Light neutral grey that works in both themes
    ax.set_facecolor('#f0f2f6')
    
    sns.heatmap(
        pivot_table,
        cmap=cmap,
        center=0.5,
        vmin=0,
        vmax=1,
        cbar=False,
        linewidths=1,
        linecolor='white',
        ax=ax
    )
    
    # Customize the plot
    weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    ax.set_yticklabels(weekdays, rotation=0)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
    ax.set_xlabel('')
    ax.set_ylabel('')
    
    # Add text annotations
    for i in range(pivot_table.shape[0]):
        for j in range(pivot_table.shape[1]):
            val = pivot_table.iloc[i, j]
            if pd.isna(val):
                text = 'NA'
                color = 'gray'
            else:
                text = str(int(val))
                color = 'white' if val == 0 else 'black'
            ax.text(j + 0.5, i + 0.5, text,
                   horizontalalignment='center',
                   verticalalignment='center',
                   color=color)
    
    plt.tight_layout()
    st.pyplot(fig)
