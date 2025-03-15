import datetime as dt
import streamlit as st
import streamlit.components.v1 as components
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import json
import os

import src.utils as utils
import src.config as config
import src.analytics as analytics
from src.data_handler import get_logbook_data


today = dt.datetime.now()

utils.set_custom_page_config("Logbook Analytics")


# Load data using shared functionality
try:
    df, loaded_path = get_logbook_data()

except Exception as e:
    st.error(f"Error loading data: {str(e)}")
    st.stop()

# Get the last 7 valid days and the previous 7 valid days
df_last_7_valid_days = analytics.get_last_n_valid_days(df, 7)
latest_date = df_last_7_valid_days['Data'].max()

# Get previous 7 valid days before the earliest date in the current period
earliest_date_current = df_last_7_valid_days['Data'].min()
df_previous = df[df['Data'] < earliest_date_current]
df_previous_7_valid_days = analytics.get_last_n_valid_days(df_previous, 7)

# Get active fields
active_fields = config.get_active_fields()
time_columns = [field for field in active_fields if field not in ["20min clean", "YNAB", "Anki", "Pamiętnik", "Plan na jutro", "No porn", "Gaming <1h", "sport", "accessories", "suplementy"]]
# Ensure "Inne" is at the beginning of the list
if "Inne" in time_columns:
    time_columns.remove("Inne")
    time_columns.insert(0, "Inne")

# Filter dataframe to include only active fields
df_last_7_valid_days = df_last_7_valid_days[list(active_fields.keys()) + ['Data', 'WEEKDAY', 'Razem']]
df_previous_7_valid_days = df_previous_7_valid_days[list(active_fields.keys()) + ['Data', 'WEEKDAY', 'Razem']]

# Main metrics
with st.expander("📊 Weekly Stats Comparison", expanded=True):
    st.caption("Comparing last 7 valid days with previous period")
    
    try:
        if df_last_7_valid_days.empty:
            raise ValueError("No data available for the current period")

        # Calculate metrics for the current period
        avg_total = df_last_7_valid_days['Razem'].mean()
        most_productive_day = df_last_7_valid_days.loc[df_last_7_valid_days['Razem'].idxmax()]
        total_productive_hours = df_last_7_valid_days['Razem'].sum() / 60

        # Calculate metrics for the previous period
        avg_total_prev = df_previous_7_valid_days['Razem'].mean() if not df_previous_7_valid_days.empty else 0
        most_productive_day_prev = df_previous_7_valid_days['Razem'].max() if not df_previous_7_valid_days.empty else 0
        total_productive_hours_prev = df_previous_7_valid_days['Razem'].sum() / 60 if not df_previous_7_valid_days.empty else 0

        # Calculate percentage changes
        avg_total_change = ((avg_total - avg_total_prev) / avg_total_prev * 100) if avg_total_prev != 0 else 0
        most_productive_day_change = ((most_productive_day['Razem'] - most_productive_day_prev) / most_productive_day_prev * 100) if most_productive_day_prev != 0 else 0
        total_productive_hours_change = ((total_productive_hours - total_productive_hours_prev) / total_productive_hours_prev * 100) if total_productive_hours_prev != 0 else 0

        # Prepare data for the HTML component
        metrics_data = [
            {
                "id": "avg_daily",
                "title": "Average Daily Total",
                "value": avg_total,
                "change": avg_total_change,
                "unit": "min",
                "format": "time",
                "days": 7
            },
            {
                "id": "most_productive_day",
                "title": "Most Productive Day",
                "value": most_productive_day['Razem'],
                "change": most_productive_day_change,
                "unit": "min",
                "format": "time",
                "days": 7
            },
            {
                "id": "total_hours",
                "title": "Total Productive Hours",
                "value": total_productive_hours,
                "change": total_productive_hours_change,
                "unit": "hrs",
                "format": "hours",
                "days": 7
            }
        ]
        
        # Load the HTML template
        template_path = os.path.join("assets", "analytics-cards.html")
        
        try:
            with open(template_path, "r", encoding="utf-8") as file:
                html_template = file.read()
                
            # Replace the placeholder with actual metrics data
            html_content = html_template.replace('METRICS_DATA_PLACEHOLDER', json.dumps(metrics_data))
            
            # Display the HTML component
            components.html(html_content, height=240, scrolling=False)
            
        except Exception as e:
            st.error(f"Error loading HTML template: {str(e)}")
            
            # Fallback to standard Streamlit metrics
            col1, col2, col3 = st.columns(3)
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
        st.exception(e)
            
# Initialize session state for 30-day window offset if it doesn't exist
if 'day_window_offset' not in st.session_state:
    st.session_state.day_window_offset = 0

# Navigation controls for 30-day window
with st.expander("📈 Daily Activity Analysis", expanded=True):
    # Calculate date range
    end_date = pd.Timestamp.now().normalize() - pd.Timedelta(days=st.session_state.day_window_offset)
    start_date = end_date - pd.Timedelta(days=30)
    
    # Create a row for navigation with columns
    col1, col2, col3 = st.columns([1, 6, 1])
    
    # Previous button
    with col1:
        if st.button("◀", use_container_width=True):
            st.session_state.day_window_offset += 30
            st.rerun()
    
    # Date range display
    with col2:
        if st.session_state.day_window_offset == 0:
            window_title = "Last 30 days"
        else:
            window_title = f"{start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')}"
        st.markdown(f"<div style='text-align: center; font-size: 16px;'>{window_title}</div>", unsafe_allow_html=True)
    
    # Next button (disabled when at current data)
    with col3:
        next_disabled = st.session_state.day_window_offset == 0
        button_style = "color: #CCCCCC;" if next_disabled else "color: #000000;"
        if st.button("▶", use_container_width=True, disabled=next_disabled):
            st.session_state.day_window_offset = max(0, st.session_state.day_window_offset - 30)
            st.rerun()
    
    # Add custom CSS to style the buttons
    st.markdown("""
    <style>
    /* Style for navigation buttons */
    button[data-testid="baseButton-secondary"] {
        background-color: transparent;
        border: none;
        font-size: 18px;
        transition: transform 0.2s;
    }
    button[data-testid="baseButton-secondary"]:hover:not([disabled]) {
        transform: scale(1.2);
        background-color: transparent !important;
    }
    button[data-testid="baseButton-secondary"]:active:not([disabled]) {
        transform: scale(0.9);
        background-color: transparent !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Filter data for the selected 30-day window
    df_last_30_days = analytics.filter_date_range(df, delta_days=30, offset_days=st.session_state.day_window_offset)
    
    # Ensure we have data for all 30 days in the range by creating a complete date range
    date_range = pd.date_range(start=start_date, end=end_date)
    complete_df = pd.DataFrame({'Data': date_range})
    
    # Merge with actual data, resulting in NA for days without data
    df_last_30_days = pd.merge(complete_df, df_last_30_days, on='Data', how='left')
    
    # Fill missing values for numeric columns with 0 for calculations
    numeric_cols = df_last_30_days.select_dtypes(include=['number']).columns
    # Exclude 'Data' column if it's in numeric_cols
    numeric_cols = [col for col in numeric_cols if col != 'Data']
    
    # Create a copy for calculations to avoid SettingWithCopyWarning
    df_calc = df_last_30_days.copy()
    df_calc[numeric_cols] = df_calc[numeric_cols].fillna(0)
    
    # Calculate 7-day moving average
    df_last_30_days['7_day_avg'] = df_calc['Razem'].rolling(7, min_periods=1).mean()

    # Get color mapping
    column_colors = config.get_column_colors()

    # Create the figure with custom colors
    fig_daily_trend = go.Figure()
    
    # For calculating max height for empty bars, use all available data
    # Use a reasonable default if no data is available
    max_height = df_last_30_days['Razem'].max()
    if pd.isna(max_height) or max_height == 0:
        max_height = 300  # Default height if no data available
    
    # First add grey bars for NA days
    na_mask = df_last_30_days['Razem'].isna()
    for date in df_last_30_days[na_mask]['Data']:
        fig_daily_trend.add_trace(go.Bar(
            x=[date],
            y=[max_height],  # Use max value to ensure bars cover full height
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
            hovertext='No data available',
            hoverinfo='text'
        ))

    # Then plot regular bars in normal order
    for column in time_columns:
        # Replace NaN values with 0 for plotting
        y_values = df_last_30_days[column].fillna(0)
        
        fig_daily_trend.add_trace(go.Bar(
            x=df_last_30_days['Data'],
            y=y_values,
            name=column,
            marker_color=column_colors.get(column, None),  # Use None if color not specified
            hovertemplate='%{x|%Y-%m-%d}<br>%{y} min<extra></extra>' if column != 'Inne' else None
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

    # Update layout with a better color scheme
    fig_daily_trend.update_layout(
        barmode='stack',
        xaxis_title="Date",
        yaxis_title="Minutes",
        legend_title="Activity",
        xaxis=dict(
            tickformat="%Y-%m-%d",
            range=[start_date, end_date],  # Fix the x-axis range to ensure all 30 days are shown
            type='date'
        ),
        transition_duration=500,  # Add transition animation when data changes
        transition=dict(
            easing='cubic-in-out'
        )
    )

    st.plotly_chart(fig_daily_trend, use_container_width=True)
