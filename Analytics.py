import datetime as dt

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

import src.utils as utils
import src.config as config
import src.analytics as analytics
from src.data_handler import get_logbook_data


utils.set_custom_page_config("Logbook Analytics")

# Load data using shared functionality
try:
    df, loaded_path = get_logbook_data()

except Exception as e:
    st.error(f"Error loading data: {str(e)}")
    st.stop()

# Filter data for the last 7 days and the previous 7 days
df_last_7_days = analytics.filter_date_range(df, delta_days=7)
df_previous_7_days = analytics.filter_date_range(df, delta_days=7, offset_days=7)

# Main metrics
with st.expander("📊 Weekly Stats Comparison", expanded=True):
    st.caption("Comparing last 7 days with previous week")
    col1, col2, col3 = st.columns(3)

    time_columns = list(config.get_fields('time').keys())
    # Ensure "Inne" is at the beginning of the list
    if "Inne" in time_columns:
        time_columns.remove("Inne")
        time_columns.insert(0, "Inne")

    # Filter dataframe to include only active fields
    tracked_columns = config.get_fields(active_only=True, include_system=True)
    df_last_7_days = df_last_7_days[tracked_columns]
    df_previous_7_days = df_previous_7_days[tracked_columns]

    try:
        if df_last_7_days.empty:
            raise ValueError("No data available for the current week")

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
            st.metric("Average Daily Total (min)", 
                     f"{avg_total:.0f}", 
                     f"{avg_total_change:.1f}%")

        with col2:
            st.metric("Most Productive Day (min)", 
                     f"{most_productive_day['Razem']:.0f}", 
                     f"{most_productive_day_change:.1f}%")

        with col3:
            st.metric("Total Productive Hours", 
                     f"{total_productive_hours:.1f}", 
                     f"{total_productive_hours_change:.1f}%")

    except Exception as e:
            st.warning("No data available for this period")
            
# Filter data for the last 30 days
df_last_30_days = analytics.filter_date_range(df, delta_days=30)

# Daily breakdown with trend line for the last 30 days
with st.expander("📈 Daily Activity Analysis", expanded=True):
    st.caption("Activity breakdown and trends for the last 30 days")
    df_last_30_days['7_day_avg'] = df_last_30_days['Razem'].rolling(7, min_periods=1).mean()

    # Get color mapping
    column_colors = config.get_column_colors()

    # Create the figure with custom colors
    fig_daily_trend = go.Figure()

    # First add grey bars for NA days
    na_mask = df_last_30_days['Razem'].isna()
    for date in df_last_30_days[na_mask]['Data']:
        fig_daily_trend.add_trace(go.Bar(
            x=[date],
            y=[df_last_30_days['Razem'].max()],
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

    # Then plot regular bars in normal order
    for column in time_columns:
        values = df_last_30_days[column].fillna(0)  # Fill NA with 0 for proper stacking
        fig_daily_trend.add_trace(go.Bar(
            x=df_last_30_days['Data'],
            y=values,
            name=column,
            marker_color=column_colors.get(column, None),
        ))

    # Finally add the trend line on top
    fig_daily_trend.add_trace(go.Scatter(
        x=df_last_30_days['Data'],
        y=df_last_30_days['7_day_avg'],
        mode='lines',
        name='7-day Average',
        line=dict(width=2, dash='dot', color='#47ff2f'),
        hovertemplate='7-day avg: %{y:.1f} min<extra></extra>'
    ))

    # Update layout to ensure proper stacking
    fig_daily_trend.update_layout(
        barmode='stack',
        xaxis_title="Date",
        yaxis_title="Minutes",
        legend_title="Activity",
        xaxis=dict(tickformat="%Y-%m-%d"),
        barnorm=None,  # Ensure no normalization is applied
    )

    st.plotly_chart(fig_daily_trend, use_container_width=True)
