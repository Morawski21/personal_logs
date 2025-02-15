import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import utils
import config

st.set_page_config(page_title="Logbook Analytics", layout="wide")
st.title("Productivity Analytics")

# Load data using shared functionality
try:
    df, loaded_path = utils.load_logbook_data()
    st.success(f"Data loaded successfully from: {loaded_path}")
except Exception as e:
    st.error(f"Error loading data: {str(e)}")
    st.stop()

# Time period selector
st.sidebar.header("Time Range")
time_range = st.sidebar.selectbox(
    "Select time period",
    ["Last 7 days", "Last 30 days", "This month", "Last month", "All time"]
)

# Filter data based on selected time range
today = datetime.now()
if time_range == "Last 7 days":
    df_filtered = df[df['Data'] >= (today - timedelta(days=7))]
elif time_range == "Last 30 days":
    df_filtered = df[df['Data'] >= (today - timedelta(days=30))]
elif time_range == "This month":
    df_filtered = df[df['Data'].dt.month == today.month]
elif time_range == "Last month":
    last_month = today.month - 1 if today.month > 1 else 12
    df_filtered = df[df['Data'].dt.month == last_month]
else:
    df_filtered = df.copy()

# Main metrics
st.header("Key Metrics")
col1, col2, col3, col4 = st.columns(4)

active_fields = config.get_active_fields()
time_columns = [field for field in active_fields if field not in ["20min clean", "YNAB", "Anki", "Pamiętnik", "Plan na jutro", "No porn", "Gaming <1h", "sport", "accessories", "suplementy"]]

# Filter dataframe to include only active fields
df_filtered = df_filtered[list(active_fields.keys()) + ['Data', 'WEEKDAY', 'Razem']]

with col1:
    avg_total = df_filtered['Razem'].mean()
    st.metric("Average Daily Total (min)", f"{avg_total:.0f}")

with col2:
    most_productive_day = df_filtered.loc[df_filtered['Razem'].idxmax()]
    st.metric("Most Productive Day", 
              f"{most_productive_day['Data'].strftime('%d.%m.%Y')}", 
              f"{most_productive_day['Razem']:.0f} min")

with col3:
    best_activity = df_filtered[time_columns].mean().idxmax()
    best_activity_avg = df_filtered[best_activity].mean()
    st.metric("Most Time Spent On", 
              best_activity,
              f"{best_activity_avg:.0f} min/day")

with col4:
    total_productive_hours = df_filtered['Razem'].sum() / 60
    st.metric("Total Productive Hours", 
              f"{total_productive_hours:.1f}",
              f"{len(df_filtered)} days tracked")

# Daily breakdown
st.header("Daily Activity Breakdown")
fig_daily = go.Figure()

for column in time_columns:
    fig_daily.add_trace(go.Bar(
        x=df_filtered['Data'],
        y=df_filtered[column],
        name=column
    ))

fig_daily.update_layout(
    barmode='stack',
    title="Daily Activity Distribution",
    xaxis_title="Date",
    yaxis_title="Minutes",
    legend_title="Activity"
)

st.plotly_chart(fig_daily, use_container_width=True)

# Activity distribution
st.header("Activity Distribution")
col1, col2 = st.columns(2)

with col1:
    # Pie chart of average time distribution
    avg_distribution = df_filtered[time_columns].mean()
    fig_pie = px.pie(values=avg_distribution.values, 
                     names=avg_distribution.index,
                     title="Average Time Distribution")
    st.plotly_chart(fig_pie)

with col2:
    # Weekly patterns
    weekday_avg = df_filtered.groupby('WEEKDAY')[time_columns].mean()
    weekday_avg = weekday_avg.reindex(config.WEEKDAY_ORDER)
    
    fig_weekly = px.bar(weekday_avg,
                        title="Average Activity by Weekday",
                        labels={'value': 'Minutes', 'WEEKDAY': 'Day'})
    st.plotly_chart(fig_weekly)

# Trends over time
st.header("Productivity Trends")
df_filtered['7_day_avg'] = df_filtered['Razem'].rolling(7).mean()

fig_trend = go.Figure()
fig_trend.add_scatter(x=df_filtered['Data'], 
                     y=df_filtered['Razem'],
                     mode='markers',
                     name='Daily Total')
fig_trend.add_scatter(x=df_filtered['Data'],
                     y=df_filtered['7_day_avg'],
                     mode='lines',
                     name='7-day Average',
                     line=dict(width=3))
fig_trend.update_layout(title="Productivity Trend Over Time",
                       xaxis_title="Date",
                       yaxis_title="Minutes")
st.plotly_chart(fig_trend, use_container_width=True)

# Detailed statistics
st.header("Detailed Statistics")
col1, col2 = st.columns(2)

with col1:
    st.subheader("Activity Statistics (minutes)")
    stats_df = df_filtered[time_columns + ["Razem"]].describe()
    st.dataframe(stats_df.round(1))

with col2:
    st.subheader("Top Productive Days")
    top_days = df_filtered.nlargest(5, 'Razem')[['Data', 'WEEKDAY', 'Razem']]
    top_days['Data'] = top_days['Data'].dt.strftime('%d.%m.%Y')
    st.dataframe(top_days)