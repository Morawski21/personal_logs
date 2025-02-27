import datetime as dt
import calendar
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from plotly.subplots import make_subplots

import src.utils as utils
import src.config as config
import src.analytics as analytics
from src.data_handler import get_logbook_data


today = dt.datetime.now()

utils.set_custom_page_config("Productivity Dashboard")

# Custom styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
        color: #1E293B;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: 600;
        margin-top: 1.5rem;
        margin-bottom: 0.75rem;
        color: #334155;
    }
    .highlight-card {
        background-color: #f8fafc;
        border-radius: 8px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }
    .data-caption {
        font-size: 0.875rem;
        color: #64748b;
        font-style: italic;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Load data using shared functionality
try:
    df, loaded_path = get_logbook_data()
except Exception as e:
    st.error(f"Error loading data: {str(e)}")
    st.stop()

# Active fields and time columns
active_fields = config.get_active_fields()
time_columns = [field for field in active_fields if field not in ["20min clean", "YNAB", "Anki", "Pamiętnik", "Plan na jutro", "No porn", "Gaming <1h", "sport", "accessories", "suplementy"]]
# Ensure "Inne" is at the beginning of the list
if "Inne" in time_columns:
    time_columns.remove("Inne")
    time_columns.insert(0, "Inne")

# Filter data for different time periods
df_last_7_days = analytics.filter_date_range(df, delta_days=7)
df_previous_7_days = analytics.filter_date_range(df, today, delta_days=7, offset_days=7)
df_last_30_days = analytics.filter_date_range(df, delta_days=30)
df_last_90_days = analytics.filter_date_range(df, delta_days=90)

# Filter dataframes to include only active fields
df_last_7_days = df_last_7_days[list(active_fields.keys()) + ['Data', 'WEEKDAY', 'Razem']]
df_previous_7_days = df_previous_7_days[list(active_fields.keys()) + ['Data', 'WEEKDAY', 'Razem']]
df_last_30_days = df_last_30_days[list(active_fields.keys()) + ['Data', 'WEEKDAY', 'Razem']]
df_last_90_days = df_last_90_days[list(active_fields.keys()) + ['Data', 'WEEKDAY', 'Razem']]

# Custom header
st.markdown('<div class="main-header">📊 Productivity Dashboard</div>', unsafe_allow_html=True)

# Date range selector
time_period = st.selectbox(
    "Select Time Range",
    ["Last 7 Days", "Last 30 Days", "Last 90 Days", "Year to Date", "All Time"],
    index=1
)

# Create time period filter based on selection
if time_period == "Last 7 Days":
    df_period = df_last_7_days
    period_days = 7
    comparison_text = "vs previous week"
elif time_period == "Last 30 Days":
    df_period = df_last_30_days
    period_days = 30
    comparison_text = "vs previous month"
elif time_period == "Last 90 Days":
    df_period = df_last_90_days
    period_days = 90
    comparison_text = "vs previous 90 days"
elif time_period == "Year to Date":
    df_period = df[df['Data'] >= pd.Timestamp(today.year, 1, 1)]
    period_days = (today - dt.datetime(today.year, 1, 1)).days + 1
    comparison_text = "vs previous year"
else:  # All Time
    df_period = df
    period_days = len(df)
    comparison_text = ""

# Compare with previous period
if time_period != "All Time":
    df_previous_period = analytics.filter_date_range(df, today, delta_days=period_days, offset_days=period_days)
else:
    df_previous_period = pd.DataFrame()  # Empty DataFrame for "All Time"

# Top summary metrics row
st.markdown('<div class="sub-header">Key Metrics</div>', unsafe_allow_html=True)
st.markdown(f'<div class="data-caption">Data for {time_period.lower()} {comparison_text}</div>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

try:
    if df_period.empty:
        raise ValueError("No data available for the selected period")

    # Calculate metrics for the current period
    avg_total = df_period['Razem'].mean()
    most_productive_day = df_period.loc[df_period['Razem'].idxmax()]
    total_productive_hours = df_period['Razem'].sum() / 60
    
    # Calculate balance score
    time_data = df_period[time_columns].sum()
    balance_score = analytics.calculate_balance_score(time_data)
    
    # Calculate metrics for the previous period
    if not df_previous_period.empty:
        avg_total_prev = df_previous_period['Razem'].mean()
        most_productive_day_prev = df_previous_period['Razem'].max()
        total_productive_hours_prev = df_previous_period['Razem'].sum() / 60
        prev_time_data = df_previous_period[time_columns].sum()
        prev_balance_score = analytics.calculate_balance_score(prev_time_data)
    else:
        avg_total_prev = 0
        most_productive_day_prev = 0
        total_productive_hours_prev = 0
        prev_balance_score = 0

    # Calculate percentage changes
    avg_total_change = ((avg_total - avg_total_prev) / avg_total_prev * 100) if avg_total_prev != 0 else 0
    most_productive_day_change = ((most_productive_day['Razem'] - most_productive_day_prev) / most_productive_day_prev * 100) if most_productive_day_prev != 0 else 0
    total_productive_hours_change = ((total_productive_hours - total_productive_hours_prev) / total_productive_hours_prev * 100) if total_productive_hours_prev != 0 else 0
    balance_score_change = (balance_score - prev_balance_score) if prev_balance_score != 0 else 0

    with col1:
        st.metric("Daily Average (min)", 
                 f"{avg_total:.0f}", 
                 f"{avg_total_change:.1f}%" if time_period != "All Time" else None)

    with col2:
        st.metric("Most Productive Day (min)", 
                 f"{most_productive_day['Razem']:.0f}", 
                 f"{most_productive_day_change:.1f}%" if time_period != "All Time" else None)

    with col3:
        st.metric("Total Hours", 
                 f"{total_productive_hours:.1f}", 
                 f"{total_productive_hours_change:.1f}%" if time_period != "All Time" else None)
    
    with col4:
        st.metric("Balance Score", 
                 f"{balance_score:.0f}/100", 
                 f"{balance_score_change:.1f}" if time_period != "All Time" else None)

except Exception as e:
    st.warning("No data available for this period")

# Create tabs for different visualizations
tab1, tab2, tab3 = st.tabs(["Activity Timeline", "Activity Distribution", "Trends & Patterns"])

# Get color mapping
column_colors = config.get_column_colors()

# Tab 1: Activity Timeline
with tab1:
    st.markdown('<div class="sub-header">Daily Activity Timeline</div>', unsafe_allow_html=True)
    st.markdown('<div class="data-caption">Stacked view of time spent across activities</div>', unsafe_allow_html=True)
    
    # Create 7-day rolling average
    df_period['7_day_avg'] = df_period['Razem'].rolling(7, min_periods=1).mean()
    
    # Create the figure with custom colors
    fig_daily_trend = go.Figure()

    # First add grey bars for NA days
    na_mask = df_period['Razem'].isna()
    for date in df_period[na_mask]['Data']:
        fig_daily_trend.add_trace(go.Bar(
            x=[date],
            y=[df_period['Razem'].max() if not df_period.empty else 0],  
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
        fig_daily_trend.add_trace(go.Bar(
            x=df_period['Data'],
            y=df_period[column],
            name=f"{config.HABITS_CONFIG[column]['emoji']} {column}",
            marker_color=column_colors.get(column, None),
            hovertemplate='%{y} min<extra></extra>'
        ))

    # Finally add the trend line on top
    fig_daily_trend.add_trace(go.Scatter(
        x=df_period['Data'],
        y=df_period['7_day_avg'],
        mode='lines',
        name='7-day Rolling Avg',
        line=dict(width=3, color='rgba(255, 255, 255, 0.7)'),
        hovertemplate='Avg: %{y:.1f} min<extra></extra>'
    ))

    # Update layout
    fig_daily_trend.update_layout(
        barmode='stack',
        xaxis_title="Date",
        yaxis_title="Minutes",
        legend_title="Activity",
        xaxis=dict(tickformat="%b %d"),
        hovermode="x unified",
        plot_bgcolor='rgba(240,242,246,0.8)',
        margin=dict(l=10, r=10, t=10, b=10),
        height=450
    )

    st.plotly_chart(fig_daily_trend, use_container_width=True)
    
    # Weekly patterns heatmap
    st.markdown('<div class="sub-header">Weekly Patterns</div>', unsafe_allow_html=True)
    st.markdown('<div class="data-caption">Productivity patterns by day of week and time period</div>', unsafe_allow_html=True)
    
    # Calculate average productivity by day of week
    weekday_order = config.WEEKDAY_ORDER
    df_period['WEEKDAY_NUM'] = df_period['WEEKDAY'].map({day: i for i, day in enumerate(weekday_order)})
    
    # Create a pivot table for weekday productivity heatmap
    weekday_pivot = pd.pivot_table(
        df_period, 
        values='Razem', 
        index=pd.Categorical(df_period['WEEKDAY'], categories=weekday_order, ordered=True),
        aggfunc='mean'
    ).reset_index()
    
    weekday_pivot = weekday_pivot.sort_values(by='WEEKDAY', key=lambda x: x.map({day: i for i, day in enumerate(weekday_order)}))
    
    # Create heatmap for weekday productivity
    fig_weekday_heatmap = px.imshow(
        weekday_pivot['Razem'].values.reshape(1, -1),
        y=['Average'],
        x=weekday_pivot['WEEKDAY'],
        color_continuous_scale='Viridis',
        text_auto='.0f',
        aspect='auto',
        labels=dict(color='Minutes')
    )

    fig_weekday_heatmap.update_layout(
        xaxis_title="Day of Week",
        yaxis_title="",
        coloraxis_showscale=True,
        margin=dict(l=10, r=10, t=10, b=10),
        height=150
    )
    
    st.plotly_chart(fig_weekday_heatmap, use_container_width=True)

# Tab 2: Activity Distribution
with tab2:
    st.markdown('<div class="sub-header">Time Distribution by Activity</div>', unsafe_allow_html=True)
    st.markdown('<div class="data-caption">How time is allocated across different activities</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        # Calculate activity distribution percentages
        activity_totals = df_period[time_columns].sum()
        activity_totals = activity_totals[activity_totals > 0]  # Filter out zero activities
        
        # Create a pie chart showing distribution of time
        fig_distribution = go.Figure()
        
        fig_distribution.add_trace(go.Pie(
            labels=[f"{config.HABITS_CONFIG[col]['emoji']} {col}" for col in activity_totals.index],
            values=activity_totals.values,
            textinfo='percent+label',
            marker=dict(
                colors=[column_colors.get(col, None) for col in activity_totals.index],
                line=dict(color='#FFFFFF', width=1.5)
            ),
            pull=[0.05 if col == activity_totals.idxmax() else 0 for col in activity_totals.index],
            hole=0.4
        ))
        
        total_hours = activity_totals.sum() / 60
        
        fig_distribution.update_layout(
            annotations=[dict(
                text=f"{total_hours:.1f}<br>hours",
                x=0.5, y=0.5,
                font_size=20,
                showarrow=False
            )],
            showlegend=True,
            margin=dict(l=10, r=10, t=10, b=10),
            height=400
        )
        
        st.plotly_chart(fig_distribution, use_container_width=True)
    
    with col2:
        # Create a bar chart showing hours per activity
        activity_hours = (activity_totals / 60).round(1)
        activity_hours = activity_hours.sort_values(ascending=False)
        
        fig_hours = go.Figure()
        
        for i, (activity, hours) in enumerate(activity_hours.items()):
            fig_hours.add_trace(go.Bar(
                x=[hours],
                y=[f"{config.HABITS_CONFIG[activity]['emoji']} {activity}"],
                orientation='h',
                marker_color=column_colors.get(activity, None),
                name=activity,
                showlegend=False,
                hovertemplate=f"{activity}: %{{x:.1f}} hours<extra></extra>"
            ))
        
        fig_hours.update_layout(
            yaxis=dict(
                categoryorder='array',
                categoryarray=[f"{config.HABITS_CONFIG[a]['emoji']} {a}" for a in activity_hours.index]
            ),
            xaxis_title="Hours",
            margin=dict(l=10, r=10, t=10, b=10),
            height=400
        )
        
        st.plotly_chart(fig_hours, use_container_width=True)

    # Activity correlations - what activities happen together?
    st.markdown('<div class="sub-header">Activity Correlations</div>', unsafe_allow_html=True)
    st.markdown('<div class="data-caption">Which activities tend to occur together or displace each other?</div>', unsafe_allow_html=True)
    
    # Calculate correlations between activities
    correlations = df_period[time_columns].corr()
    
    # Create correlation heatmap
    mask = np.triu(np.ones_like(correlations, dtype=bool))
    df_corr = correlations.mask(mask)
    
    # List activities with emojis for the chart
    activities_with_emojis = [f"{config.HABITS_CONFIG[col]['emoji']} {col}" for col in correlations.columns]
    
    fig_corr = px.imshow(
        df_corr,
        x=activities_with_emojis,
        y=activities_with_emojis,
        color_continuous_scale="RdBu_r",
        zmin=-1, zmax=1,
        text_auto='.2f',
        aspect='auto'
    )
    
    fig_corr.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        height=500,
        coloraxis_colorbar=dict(
            title="Correlation",
            thicknessmode="pixels", thickness=20,
            lenmode="pixels", len=300,
            yanchor="top", y=1,
            ticks="outside"
        )
    )
    
    st.plotly_chart(fig_corr, use_container_width=True)

# Tab 3: Trends & Patterns
with tab3:
    st.markdown('<div class="sub-header">Activity Trends</div>', unsafe_allow_html=True)
    st.markdown('<div class="data-caption">How each activity has evolved over time</div>', unsafe_allow_html=True)
    
    # Create a multiple line chart showing trends for each activity
    df_trends = df_period.copy()
    df_trends['Month'] = df_trends['Data'].dt.to_period('M')
    
    # Create 7-day rolling averages for each activity
    for col in time_columns:
        df_trends[f"{col}_7day_avg"] = df_trends[col].rolling(7, min_periods=1).mean()
    
    # Prepare subplot figure with one subplot per activity
    fig_trends = make_subplots(
        rows=len(time_columns),
        cols=1,
        shared_xaxes=True,
        subplot_titles=[f"{config.HABITS_CONFIG[col]['emoji']} {col}" for col in time_columns],
        vertical_spacing=0.03
    )
    
    # Smoothed trend lines
    for i, col in enumerate(time_columns):
        fig_trends.add_trace(
            go.Scatter(
                x=df_trends['Data'],
                y=df_trends[f"{col}_7day_avg"],
                mode='lines',
                name=col,
                line=dict(color=column_colors.get(col, None), width=3),
                showlegend=False,
                hovertemplate=f"{col}: %{{y:.1f}} min<extra></extra>"
            ),
            row=i+1, col=1
        )
        
        # Add a light fill
        fig_trends.add_trace(
            go.Scatter(
                x=df_trends['Data'],
                y=df_trends[f"{col}_7day_avg"],
                mode='none',
                fillcolor=column_colors.get(col, "#888888") + "20",  # Add transparency
                fill='tozeroy',
                showlegend=False,
                hoverinfo='none'
            ),
            row=i+1, col=1
        )
    
    # Update layout
    fig_trends.update_layout(
        height=150 * len(time_columns),
        margin=dict(l=10, r=10, t=10, b=10 + 15*len(time_columns)),
        hovermode="x unified",
        plot_bgcolor='rgba(240,242,246,0.8)'
    )
    
    # Update all x-axes
    for i in range(len(time_columns)):
        fig_trends.update_xaxes(
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(240,240,240,0.5)',
            row=i+1, col=1
        )
        
        # Only show x-axis title and ticks on the last subplot
        if i == len(time_columns) - 1:
            fig_trends.update_xaxes(
                title_text="Date",
                showticklabels=True,
                row=i+1, col=1
            )
        else:
            fig_trends.update_xaxes(
                showticklabels=False,
                row=i+1, col=1
            )
        
        # Update y-axes
        fig_trends.update_yaxes(
            title_text="Minutes",
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(240,240,240,0.5)',
            row=i+1, col=1
        )
    
    st.plotly_chart(fig_trends, use_container_width=True)
    
    # Monthly consistency analysis
    st.markdown('<div class="sub-header">Consistency Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="data-caption">Showing streak patterns and consistency for each activity</div>', unsafe_allow_html=True)
    
    if time_period != "Last 7 Days":  # Only show when we have enough data
        # Calculate consistency metrics
        activity_metrics = []
        
        for activity in time_columns:
            # For each activity, calculate:
            # 1. Percentage of days with any activity
            # 2. Current streak (consecutive days)
            # 3. Longest streak
            
            # Binary version (did activity or not)
            activity_binary = (df_period[activity] > 0).astype(int)
            
            if len(activity_binary) > 0:
                consistency_pct = activity_binary.mean() * 100
                
                # Current streak calculation
                current_streak = 0
                for val in reversed(activity_binary.values):
                    if val > 0:
                        current_streak += 1
                    else:
                        break
                
                # Longest streak calculation
                streak_lengths = []
                current = 0
                
                for val in activity_binary.values:
                    if val > 0:
                        current += 1
                    else:
                        if current > 0:
                            streak_lengths.append(current)
                        current = 0
                
                # Don't forget the last streak if we're in the middle of one
                if current > 0:
                    streak_lengths.append(current)
                
                longest_streak = max(streak_lengths) if streak_lengths else 0
                
                activity_metrics.append({
                    'Activity': f"{config.HABITS_CONFIG[activity]['emoji']} {activity}",
                    'Consistency': consistency_pct,
                    'Current Streak': current_streak,
                    'Longest Streak': longest_streak,
                    'Color': column_colors.get(activity, '#888888')
                })
        
        # Convert to DataFrame for easier visualization
        df_metrics = pd.DataFrame(activity_metrics)
        
        # Create columns for the visualization
        mcol1, mcol2 = st.columns(2)
        
        with mcol1:
            # Consistency percentage chart
            fig_consistency = go.Figure()
            
            for _, row in df_metrics.sort_values('Consistency', ascending=False).iterrows():
                fig_consistency.add_trace(go.Bar(
                    x=[row['Consistency']],
                    y=[row['Activity']],
                    orientation='h',
                    marker_color=row['Color'],
                    text=f"{row['Consistency']:.1f}%",
                    textposition='auto',
                    hovertemplate=f"Consistency: {row['Consistency']:.1f}%<extra></extra>"
                ))
            
            fig_consistency.update_layout(
                title='Activity Consistency (%)',
                xaxis_title='% Days Active',
                xaxis=dict(range=[0, 100]),
                margin=dict(l=10, r=10, t=40, b=10),
                showlegend=False,
                height=400
            )
            
            st.plotly_chart(fig_consistency, use_container_width=True)
            
        with mcol2:
            # Streak comparison chart
            fig_streaks = go.Figure()
            
            df_metrics_sorted = df_metrics.sort_values('Longest Streak', ascending=False)
            
            for _, row in df_metrics_sorted.iterrows():
                fig_streaks.add_trace(go.Bar(
                    x=[row['Current Streak']],
                    y=[row['Activity']],
                    orientation='h',
                    name='Current Streak',
                    marker_color=row['Color'],
                    opacity=0.7,
                    text=f"{row['Current Streak']}d",
                    textposition='auto',
                    hovertemplate=f"Current Streak: {row['Current Streak']} days<extra></extra>"
                ))
                
                fig_streaks.add_trace(go.Bar(
                    x=[row['Longest Streak'] - row['Current Streak']] if row['Longest Streak'] > row['Current Streak'] else [0],
                    y=[row['Activity']],
                    orientation='h',
                    base=row['Current Streak'] if row['Longest Streak'] > row['Current Streak'] else 0,
                    name='Additional to Longest',
                    marker_color=row['Color'],
                    opacity=0.3,
                    text=f"{row['Longest Streak']}d" if row['Longest Streak'] > row['Current Streak'] else "",
                    textposition='auto',
                    hovertemplate=f"Longest Streak: {row['Longest Streak']} days<extra></extra>"
                ))
            
            fig_streaks.update_layout(
                title='Activity Streaks',
                xaxis_title='Days',
                barmode='stack',
                showlegend=False,
                margin=dict(l=10, r=10, t=40, b=10),
                height=400
            )
            
            st.plotly_chart(fig_streaks, use_container_width=True)