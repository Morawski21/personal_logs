import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import utils
import config
import pandas as pd

st.set_page_config(
    page_title="Logbook Analytics", 
    layout="wide",
    page_icon="icon.png"
)

# Define today at the start
today = datetime.now()

# Load data using shared functionality
try:
    df, loaded_path = utils.load_logbook_data()
    # Filter out future dates
    df = df[df['Data'] <= today]
    #st.success(f"Data loaded successfully from: {loaded_path}")
except Exception as e:
    st.error(f"Error loading data: {str(e)}")
    st.stop()

# Filter data for the last 7 days and the previous 7 days
df_last_7_days = df[df['Data'] >= (today - timedelta(days=7))]
df_previous_7_days = df[(df['Data'] >= (today - timedelta(days=14))) & (df['Data'] < (today - timedelta(days=7)))]

# Main metrics
st.header("Last week vs. Previous week")
col1, col2, col3 = st.columns(3)

active_fields = config.get_active_fields()
time_columns = [field for field in active_fields if field not in ["20min clean", "YNAB", "Anki", "Pamiętnik", "Plan na jutro", "No porn", "Gaming <1h", "sport", "accessories", "suplementy"]]

# Filter dataframe to include only active fields
df_last_7_days = df_last_7_days[list(active_fields.keys()) + ['Data', 'WEEKDAY', 'Razem']]
df_previous_7_days = df_previous_7_days[list(active_fields.keys()) + ['Data', 'WEEKDAY', 'Razem']]

# Calculate metrics for the current period
avg_total = df_last_7_days['Razem'].mean()
most_productive_day = df_last_7_days.loc[df_last_7_days['Razem'].idxmax()]
total_productive_hours = df_last_7_days['Razem'].sum() / 60

# Calculate metrics for the previous period
avg_total_prev = df_previous_7_days['Razem'].mean() if not df_previous_7_days.empty else 0
most_productive_day_prev = df_previous_7_days['Razem'].max() if not df_previous_7_days.empty else 0
total_productive_hours_prev = df_previous_7_days['Razem'].sum() / 60 if not df_previous_7_days.empty else 0

# Calculate percentage changes
avg_total_change = ((avg_total - avg_total_prev) / avg_total_prev * 100) if avg_total_prev != 0 else 0
most_productive_day_change = ((most_productive_day['Razem'] - most_productive_day_prev) / most_productive_day_prev * 100) if most_productive_day_prev != 0 else 0
total_productive_hours_change = ((total_productive_hours - total_productive_hours_prev) / total_productive_hours_prev * 100) if total_productive_hours_prev != 0 else 0

with col1:
    st.metric("Average Daily Total (min)", f"{avg_total:.0f}", f"{avg_total_change:.1f}%")

with col2:
    st.metric("Most Productive Day (min)", 
              f"{most_productive_day['Razem']:.0f}", 
              f"{most_productive_day_change:.1f}%")

with col3:
    st.metric("Total Productive Hours", 
              f"{total_productive_hours:.1f}", 
              f"{total_productive_hours_change:.1f}%")

# Filter data for the last 30 days
df_last_30_days = df[df['Data'] >= (today - timedelta(days=30))]

# Ensure all dates within the last 30 days are present, excluding future dates
date_range = pd.date_range(
    start=df_last_30_days['Data'].min(),
    end=min(df_last_30_days['Data'].max(), today),
    freq='D'
)
df_last_30_days = df_last_30_days.set_index('Data').reindex(date_range).fillna(0).reset_index().rename(columns={'index': 'Data'})

# Daily breakdown with trend line for the last 30 days
st.header("Daily Activity Breakdown and Trends (Last 30 Days)")
df_last_30_days['7_day_avg'] = df_last_30_days['Razem'].rolling(7, min_periods=1).mean()

fig_daily_trend = go.Figure()

for column in time_columns:
    fig_daily_trend.add_trace(go.Bar(
        x=df_last_30_days['Data'],
        y=df_last_30_days[column],
        name=column
    ))

fig_daily_trend.add_trace(go.Scatter(
    x=df_last_30_days['Data'],
    y=df_last_30_days['7_day_avg'],
    mode='lines',
    name='7-day Average',
    line=dict(width=3, dash='dot', color='red')
))

fig_daily_trend.update_layout(
    barmode='stack',
    title="Daily Activity Distribution and 7-day Average Trend (Last 30 Days)",
    xaxis_title="Date",
    yaxis_title="Minutes",
    legend_title="Activity",
    xaxis=dict(tickformat="%Y-%m-%d")
)

st.plotly_chart(fig_daily_trend, use_container_width=True)