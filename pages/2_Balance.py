import streamlit as st
import plotly.graph_objects as go
from datetime import datetime, timedelta
import utils
import config
from balance import calculate_balance_score
import pandas as pd

st.set_page_config(
    page_title="Balance Analysis",
    layout="wide",
    page_icon="⚖️"
)

st.title("⚖️ Time Balance Analysis")

# Load and prepare data
today = datetime.now()
try:
    df, _ = utils.load_logbook_data()
    df = df[df['Data'] <= today]
except Exception as e:
    st.error(f"Error loading data: {str(e)}")
    st.stop()

# Get active time-based fields
active_fields = config.get_active_fields()
time_columns = [field for field in active_fields if field not in ["20min clean", "YNAB", "Anki", "Pamiętnik", "Plan na jutro", "No porn", "Gaming <1h", "sport", "accessories", "suplementy"]]
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
for date in pd.date_range(df_last_30_days['Data'].min(), today):
    day_data = df_last_30_days[df_last_30_days['Data'].dt.date == date.date()]
    if not day_data.empty:
        time_activities = day_data[time_columns].iloc[0]
        score = calculate_balance_score(time_activities)
        daily_scores.append(score)
        dates.append(date)

# Weekly average scores
col1, col2 = st.columns(2)

with col1:
    st.subheader("Weekly Balance Score")
    current_week_avg = sum(daily_scores[-7:]) / 7 if len(daily_scores) >= 7 else 0
    prev_week_avg = sum(daily_scores[-14:-7]) / 7 if len(daily_scores) >= 14 else 0
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
    total_time = df_last_7_days[time_columns].sum()
    
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

# Balance Score Trend
st.subheader("Balance Score Trend")
fig_trend = go.Figure()

# Add balance score line
fig_trend.add_trace(go.Scatter(
    x=dates,
    y=daily_scores,
    mode='lines+markers',
    name='Daily Balance Score',
    line=dict(color='#47ff2f', width=2)
))

# Add 7-day moving average
moving_avg = pd.Series(daily_scores).rolling(7, min_periods=1).mean()
fig_trend.add_trace(go.Scatter(
    x=dates,
    y=moving_avg,
    mode='lines',
    name='7-day Average',
    line=dict(color='#ff9f1c', width=2, dash='dash')
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
    'Balance Score': daily_scores[-7:],
}).set_index('Date')

daily_breakdown['Balance Score'] = daily_breakdown['Balance Score'].round(1)
st.dataframe(daily_breakdown, use_container_width=True)
