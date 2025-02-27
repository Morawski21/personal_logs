import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import os
import json

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
        values = values.apply(lambda x: 1.0 if pd.notnull(x) and x >= 20 else 0.0)
    
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
        else:  # Break on explicit 0
            break
            
    return current_streak

def calculate_longest_streak(series):
    """Calculate the longest streak from a series of values."""
    # Same conversion as in current_streak
    values = series.copy()
    
    if values.max() > 1:
        values = values.apply(lambda x: 1.0 if pd.notnull(x) and x >= 20 else (0.0 if pd.notnull(x) else pd.NA))
    
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
st.title("🎯 Habit Streaks 2.0 (Beta)")
st.caption("A new and improved habit tracker with modern visuals and reactive design")

# Create a simple HTML component with custom CSS and vanilla JS
# Create template for HTML content
html_template = """
<html>
<head>
    <style>
        .card {
            background-color: #111827;
            border-radius: 8px;
            padding: 16px;
            color: white;
            margin-bottom: 16px;
            position: relative;
            overflow: hidden;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        }
        
        .grid-container {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 16px;
            padding: 16px;
        }
        
        .card-header {
            display: flex;
            align-items: center;
            margin-bottom: 12px;
        }
        
        .emoji {
            font-size: 24px;
            margin-right: 12px;
        }
        
        .habit-name {
            font-size: 18px;
            font-weight: 600;
        }
        
        .card-content {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
        }
        
        .streak-box {
            display: flex;
            flex-direction: column;
        }
        
        .streak-label {
            font-size: 12px;
            color: #9ca3af;
            margin-bottom: 4px;
        }
        
        .streak-value {
            font-size: 24px;
            font-weight: 700;
            line-height: 1.25;
        }
        
        .streak-status {
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 14px;
        }
        
        .record-breaking {
            color: #c084fc;
        }
        
        .active {
            color: #4ade80;
        }
        
        .inactive {
            color: #9ca3af;
        }
        
        .best {
            color: #9ca3af;
        }
        
        .record-background {
            position: absolute;
            top: 0;
            right: 0;
            bottom: 0;
            left: 0;
            opacity: 0.2;
            background: radial-gradient(
                100% 100% at 0% 0%,
                rgb(236, 72, 153) 0%,
                rgb(147, 51, 234) 25%,
                rgb(45, 212, 191) 50%,
                transparent 75%
            );
            animation: moveGradient 8s ease-in-out infinite;
        }
        
        @keyframes moveGradient {
            0% {
                transform: translate(-25%, -25%) rotate(0deg);
            }
            50% {
                transform: translate(25%, 25%) rotate(180deg);
            }
            100% {
                transform: translate(-25%, -25%) rotate(360deg);
            }
        }
    </style>
</head>
<body>
    <div id="root"></div>
    
    <script type="text/javascript">
        // Get habits data from Streamlit
        const habitsData = HABITS_DATA_PLACEHOLDER;
        
        // Create the habit grid
        const habitGrid = document.createElement('div');
        habitGrid.className = 'grid-container';
        
        // Create each habit card
        habitsData.forEach(habit => {
            const isRecordBreaking = habit.currentStreak >= habit.bestStreak && habit.currentStreak > 0;
            const isActive = habit.currentStreak > 0;
            
            const card = document.createElement('div');
            card.className = 'card';
            
            // Add record-breaking background if applicable
            if (isRecordBreaking) {
                const background = document.createElement('div');
                background.className = 'record-background';
                card.appendChild(background);
            }
            
            // Card header with emoji and name
            const header = document.createElement('div');
            header.className = 'card-header';
            
            const emoji = document.createElement('span');
            emoji.className = 'emoji';
            emoji.textContent = habit.emoji;
            
            const name = document.createElement('h3');
            name.className = 'habit-name';
            name.textContent = habit.name;
            
            header.appendChild(emoji);
            header.appendChild(name);
            card.appendChild(header);
            
            // Card content with streak info
            const content = document.createElement('div');
            content.className = 'card-content';
            
            // Current streak section
            const currentStreakBox = document.createElement('div');
            currentStreakBox.className = 'streak-box';
            
            const currentLabel = document.createElement('p');
            currentLabel.className = 'streak-label';
            currentLabel.textContent = 'Current streak';
            
            const currentValue = document.createElement('p');
            currentValue.className = 'streak-value';
            currentValue.textContent = habit.currentStreak + 'd';
            
            const currentStatus = document.createElement('div');
            currentStatus.className = isRecordBreaking ? 
                'streak-status record-breaking' : 
                (isActive ? 'streak-status active' : 'streak-status inactive');
            
            const statusText = document.createElement('span');
            statusText.textContent = isRecordBreaking ? 'Record-breaking' : (isActive ? 'Active' : 'Inactive');
            
            const statusIcon = document.createElement('span');
            statusIcon.textContent = isRecordBreaking ? '✨' : (isActive ? '🔥' : '');
            
            currentStatus.appendChild(statusText);
            currentStatus.appendChild(statusIcon);
            
            currentStreakBox.appendChild(currentLabel);
            currentStreakBox.appendChild(currentValue);
            currentStreakBox.appendChild(currentStatus);
            
            // Best streak section
            const bestStreakBox = document.createElement('div');
            bestStreakBox.className = 'streak-box';
            
            const bestLabel = document.createElement('p');
            bestLabel.className = 'streak-label';
            bestLabel.textContent = 'Best streak';
            
            const bestValue = document.createElement('p');
            bestValue.className = 'streak-value';
            bestValue.textContent = habit.bestStreak + 'd';
            
            const bestStatus = document.createElement('div');
            bestStatus.className = 'streak-status best';
            
            const bestText = document.createElement('span');
            bestText.textContent = 'Best';
            
            const bestIcon = document.createElement('span');
            bestIcon.textContent = '🏆';
            
            bestStatus.appendChild(bestText);
            bestStatus.appendChild(bestIcon);
            
            bestStreakBox.appendChild(bestLabel);
            bestStreakBox.appendChild(bestValue);
            bestStreakBox.appendChild(bestStatus);
            
            content.appendChild(currentStreakBox);
            content.appendChild(bestStreakBox);
            card.appendChild(content);
            
            habitGrid.appendChild(card);
        });
        
        document.getElementById('root').appendChild(habitGrid);
    </script>
</body>
</html>
"""

# Replace the placeholder with actual habits data
html_content = html_template.replace('HABITS_DATA_PLACEHOLDER', json.dumps(habits_data))

# Display the HTML component
components.html(html_content, height=450, scrolling=False)

# Add explanation about the new version
st.markdown("---")
st.subheader("About Streaks 2.0")
st.markdown("""
This new version of the habit tracker uses a custom component that offers improved visual feedback:

- **Record-breaking streaks** are highlighted with animated gradient backgrounds
- **Active streaks** are clearly marked with flame icons
- **Modern, consistent design** with better visual organization

The component pulls data from the same Excel file and applies the same logic as the original Streaks page, 
ensuring consistent streak calculations.
""")

# Add a space to compare with original
comparison_tab1, comparison_tab2 = st.tabs(["Streaks 2.0 (New)", "Original Streaks"])

with comparison_tab1:
    st.markdown("The new version features:")
    st.markdown("- ✨ Animated backgrounds for record-breaking streaks")
    st.markdown("- 🎨 Consistent color scheme and typography")
    st.markdown("- 📱 Responsive card layout")
    st.markdown("- 🔥 Clear visual indicators for active vs. inactive streaks")

with comparison_tab2:
    st.markdown("The original version uses standard Streamlit metrics and expanders.")