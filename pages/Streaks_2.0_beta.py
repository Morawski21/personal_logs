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

# Create data for React component
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

# Create JS for React component integration
component_js = """
<script src="https://unpkg.com/react@17/umd/react.development.js"></script>
<script src="https://unpkg.com/react-dom@17/umd/react-dom.development.js"></script>
<script src="https://unpkg.com/babel-standalone@6/babel.min.js"></script>
<script src="https://unpkg.com/lucide-react@latest"></script>

<div id="react-root" style="font-family: 'Inter', system-ui, sans-serif;"></div>

<style>
  body {
    background-color: transparent;
    margin: 0;
    padding: 0;
  }
  
  * {
    box-sizing: border-box;
  }
  
  .text-white {
    color: white;
  }
  
  .text-gray-400 {
    color: #9ca3af;
  }
  
  .text-green-400 {
    color: #4ade80;
  }
  
  .text-purple-400 {
    color: #c084fc;
  }
  
  .bg-gray-900 {
    background-color: #111827;
  }
  
  .font-semibold {
    font-weight: 600;
  }
  
  .font-bold {
    font-weight: 700;
  }
  
  .text-xs {
    font-size: 0.75rem;
  }
  
  .text-sm {
    font-size: 0.875rem;
  }
  
  .text-lg {
    font-size: 1.125rem;
  }
  
  .text-xl {
    font-size: 1.25rem;
  }
  
  .text-2xl {
    font-size: 1.5rem;
  }
  
  .leading-tight {
    line-height: 1.25;
  }
  
  .p-3 {
    padding: 0.75rem;
  }
  
  .p-4 {
    padding: 1rem;
  }
  
  .mb-2 {
    margin-bottom: 0.5rem;
  }
  
  .space-x-1 > :not([hidden]) ~ :not([hidden]) {
    margin-left: 0.25rem;
  }
  
  .space-x-2 > :not([hidden]) ~ :not([hidden]) {
    margin-left: 0.5rem;
  }
  
  .space-y-0\\.5 > :not([hidden]) ~ :not([hidden]) {
    margin-top: 0.125rem;
  }
  
  .gap-1\\.5 {
    gap: 0.375rem;
  }
  
  .gap-3 {
    gap: 0.75rem;
  }
  
  .gap-4 {
    gap: 1rem;
  }
  
  .rounded-lg {
    border-radius: 0.5rem;
  }
  
  .shadow-lg {
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  }
  
  .relative {
    position: relative;
  }
  
  .absolute {
    position: absolute;
  }
  
  .inset-0 {
    top: 0;
    right: 0;
    bottom: 0;
    left: 0;
  }
  
  .flex {
    display: flex;
  }
  
  .grid {
    display: grid;
  }
  
  .grid-cols-2 {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  
  .grid-cols-3 {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
  
  .items-center {
    align-items: center;
  }
  
  .justify-between {
    justify-content: space-between;
  }
  
  .w-3 {
    width: 0.75rem;
  }
  
  .h-3 {
    height: 0.75rem;
  }
  
  .w-4 {
    width: 1rem;
  }
  
  .h-4 {
    height: 1rem;
  }
  
  .w-full {
    width: 100%;
  }
  
  .opacity-20 {
    opacity: 0.2;
  }
  
  .overflow-hidden {
    overflow: hidden;
  }
  
  .transition-colors {
    transition-property: color, background-color, border-color, text-decoration-color, fill, stroke;
    transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
    transition-duration: 150ms;
  }
  
  .duration-500 {
    transition-duration: 500ms;
  }
  
  .whitespace-nowrap {
    white-space: nowrap;
  }
</style>

<script type="text/babel">
  const { useState } = React;
  const { Flame, Sparkles, Trophy } = lucideReact;
  
  const HabitCard = ({ name, emoji, currentStreak, bestStreak, isActive = true }) => {
    const isRecordBreaking = currentStreak >= bestStreak && currentStreak > 0;
  
    return (
      <div className="p-3 bg-gray-900 rounded-lg shadow-lg relative overflow-hidden">
        {isRecordBreaking && (
          <>
            <div 
              className="absolute inset-0 opacity-20"
              style={{
                background: `
                  radial-gradient(
                    100% 100% at 0% 0%,
                    rgb(236, 72, 153) 0%,
                    rgb(147, 51, 234) 25%,
                    rgb(45, 212, 191) 50%,
                    transparent 75%
                  )
                `,
                animation: 'moveGradient 8s ease-in-out infinite'
              }}
            />
            <style>
              {`
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
              `}
            </style>
          </>
        )}
        
        <div className="flex items-center justify-between mb-2 relative">
          <div className="flex items-center space-x-2">
            <span className="text-xl">{emoji}</span>
            <h3 className="text-lg font-semibold text-white">{name}</h3>
          </div>
        </div>
        
        <div className="grid grid-cols-2 gap-3 relative">
          <div className="space-y-0.5">
            <p className="text-xs text-gray-400">Current streak</p>
            <p className="text-2xl font-bold text-white leading-tight">{currentStreak}d</p>
            <div className={`flex items-center gap-1.5 transition-colors duration-500 ${
              isRecordBreaking ? 'text-purple-400' : (currentStreak > 0 ? 'text-green-400' : 'text-gray-400')
            }`}>
              <span className="text-sm whitespace-nowrap">
                {isRecordBreaking ? 'Record-breaking' : (currentStreak > 0 ? 'Active' : 'Inactive')}
              </span>
              {isRecordBreaking ? (
                <Sparkles className="w-3 h-3" />
              ) : (
                currentStreak > 0 ? <Flame className="w-3 h-3" /> : null
              )}
            </div>
          </div>
          
          <div className="space-y-0.5">
            <p className="text-xs text-gray-400">Best streak</p>
            <p className="text-2xl font-bold text-white leading-tight">{bestStreak}d</p>
            <div className="flex items-center space-x-1 text-gray-400">
              <span className="text-sm">Best</span>
              <Trophy className="w-3 h-3" />
            </div>
          </div>
        </div>
      </div>
    );
  };
  
  const HabitGrid = ({ habits }) => {
    return (
      <div className="p-4 w-full">
        <div className="grid grid-cols-3 gap-4">
          {habits.map((habit, index) => (
            <HabitCard
              key={habit.name}
              {...habit}
            />
          ))}
        </div>
      </div>
    );
  };
  
  // Get habits data from Streamlit
  const habitsData = JSON.parse('{{habits_data}}');
  
  // Render the component
  ReactDOM.render(
    <HabitGrid habits={habitsData} />,
    document.getElementById('react-root')
  );
</script>
"""

# Replace placeholder with actual data
component_js = component_js.replace("{{habits_data}}", json.dumps(habits_data))

# Display the React component
components.html(component_js, height=450, scrolling=False)

# Add explanation about the new version
st.markdown("---")
st.subheader("About Streaks 2.0")
st.markdown("""
This new version of the habit tracker uses a custom React component that offers improved visual feedback:

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