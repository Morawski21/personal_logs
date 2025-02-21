from datetime import datetime, timedelta

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np

import src.utils as utils
import src.config as config
import src.balance as balance
from src.data_handler import get_logbook_data


utils.set_custom_page_config("Balance Analysis")

st.title("⚖️ Time Balance Analysis")

# Load and prepare data
today = datetime.now()
try:
    df, _ = get_logbook_data()
except Exception as e:
    st.error(f"Error loading data: {str(e)}")
    st.stop()

# Get active time-based fields
active_fields = config.get_active_fields()
time_columns = [field for field in active_fields if active_fields[field]["type"] == "time"]
if "Inne" in time_columns:
    time_columns.remove("Inne")
    time_columns.insert(0, "Inne")

# Filter data for different time periods
df_last_7_days = df[df['Data'] >= (today - timedelta(days=7))]
df_previous_7_days = df[(df['Data'] >= (today - timedelta(days=14))) & (df['Data'] < (today - timedelta(days=7)))]
df_last_30_days = df[df['Data'] >= (today - timedelta(days=30))]

# Calculate daily balance scores for the last 30 days
daily_scores = []
dates = []
na_days = []
for date in pd.date_range(df_last_30_days['Data'].min(), today):
    day_data = df_last_30_days[df_last_30_days['Data'].dt.date == date.date()]
    if not day_data.empty:
        time_activities = day_data[time_columns].iloc[0]
        score = balance.calculate_balance_score(time_activities)
        daily_scores.append(score)
        dates.append(date)
        na_days.append(score is None)

# Convert to numpy arrays for easier manipulation
dates = np.array(dates)
daily_scores = np.array(daily_scores, dtype=float)
na_days = np.array(na_days)

# Create mask for non-NA days
valid_days = ~na_days

# Weekly average scores calculation (excluding NA days)
current_week_scores = [s for s, na in zip(daily_scores[-7:], na_days[-7:]) if not na]
prev_week_scores = [s for s, na in zip(daily_scores[-14:-7], na_days[-14:-7]) if not na]

col1, col2 = st.columns(2)

with col1:
    st.subheader("Weekly Balance Score")
    current_week_avg = sum(current_week_scores) / len(current_week_scores) if current_week_scores else 0
    prev_week_avg = sum(prev_week_scores) / len(prev_week_scores) if prev_week_scores else 0
    score_change = current_week_avg - prev_week_avg

    st.metric(
        "Current Week Average",
        f"{current_week_avg:.1f}",
        f"{score_change:+.1f} vs previous week"
    )

    st.info("""
    The Balance Score measures how well you distribute your time across different activities:
    - 100: Perfect balance (equal time across all activities)
    - 0: All time spent on a single activity
    - Higher scores indicate better time distribution
    """)

with col2:
    st.subheader("Current Week Distribution")
    # Filter out rows where all time columns are NA
    valid_days_df = df_last_7_days[~df_last_7_days[time_columns].isna().all(axis=1)]
    total_time = valid_days_df[time_columns].sum()
    
    # Only create pie chart if there's data
    if total_time.sum() > 0:
        fig_pie = go.Figure(data=[go.Pie(
            labels=time_columns,
            values=total_time,
            marker_colors=[config.get_column_colors().get(col, '#808080') for col in time_columns]
        )])
        
        fig_pie.update_layout(
            showlegend=True,
            height=300
        )
        
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("No data available for the current week")

# Balance Score Trend
st.subheader("Balance Score Trend")
fig_trend = go.Figure()

# Add grey bars for NA days
for date, is_na in zip(dates, na_days):
    if is_na:
        fig_trend.add_trace(go.Bar(
            x=[date],
            y=[100],
            marker=dict(
                color='rgba(200,200,200,0.3)',
                pattern=dict(
                    shape="/",
                    bgcolor="rgba(220,220,220,0.3)",
                    solidity=0.5
                )
            ),
            width=24*60*60*1000,  # One day width in milliseconds
            name='NA Day',
            showlegend=False,
            hovertext='No data available'
        ))

# Add balance score line (only for non-NA days)
fig_trend.add_trace(go.Scatter(
    x=dates[valid_days],
    y=daily_scores[valid_days],
    mode='lines+markers',
    name='Daily Balance Score',
    line=dict(color='#47ff2f', width=2),
    connectgaps=False  # Don't connect over NA days
))

# Add 7-day moving average (excluding NA days)
valid_scores = pd.Series(daily_scores)
valid_scores[na_days] = np.nan
moving_avg = valid_scores.rolling(7, min_periods=1).mean()

fig_trend.add_trace(go.Scatter(
    x=dates,
    y=moving_avg,
    mode='lines',
    name='7-day Average',
    line=dict(color='#ff9f1c', width=2, dash='dash'),
    connectgaps=True
))

fig_trend.update_layout(
    xaxis_title="Date",
    yaxis_title="Balance Score",
    yaxis=dict(range=[0, 100]),
    hovermode='x unified',
    height=400
)

st.plotly_chart(fig_trend, use_container_width=True)

# Daily breakdown table
st.subheader("Daily Balance Details")
daily_breakdown = pd.DataFrame({
    'Date': dates[-7:],
    'Balance Score': ['NA' if na else f"{score:.1f}" for score, na in zip(daily_scores[-7:], na_days[-7:])],
}).set_index('Date')

daily_breakdown['Balance Score'] = daily_breakdown['Balance Score'].round(1)
st.dataframe(daily_breakdown, use_container_width=True)
