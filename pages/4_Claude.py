import streamlit as st
import pandas as pd
from datetime import datetime
from src.data_handler import get_logbook_data
from src.claude_handler import get_advice
import src.utils as utils
import traceback

utils.set_custom_page_config("Claude Assistant")

today = datetime.now()
is_weekend = today.weekday() >= 5

# Custom greeting based on day
if is_weekend:
    st.header(f"🤖 Weekend Insights with Claude")
else:
    st.header(f"🤖 Claude's Daily Insights")

# Add a brief introduction
st.markdown("""
This page provides personalized productivity insights and advice based on your tracked activities. 
Claude analyzes your recent patterns and offers day-specific recommendations.
""")

# Debug information
st.sidebar.markdown("### Debug Info")
debug_expander = st.sidebar.expander("Show Debug Info")

try:
    # Load data with debug info
    with debug_expander:
        st.write("Loading data...")
    
    df, loaded_path = get_logbook_data()
    
    with debug_expander:
        st.write(f"Data loaded from: {loaded_path}")
        st.write(f"DataFrame shape: {df.shape}")
    
    if df is not None and not df.empty:
        # Add a pleasant loading message with emoji
        with st.spinner("🔍 Claude is analyzing your productivity patterns..."):
            advice = get_advice(df)
            
            if advice and not advice.startswith("Error"):
                # Create columns for better layout
                col1, col2 = st.columns([5, 1])
                
                with col1:
                    # Display the advice with nice formatting
                    st.markdown(advice)
                
                with col2:
                    # Add a motivational image or icon in the second column
                    st.markdown("### Today's Focus")
                    if is_weekend:
                        st.markdown("🏖️ Balance")
                    else:
                        st.markdown("💪 Productivity")
            else:
                st.error("Failed to get meaningful advice from Claude")
                with debug_expander:
                    st.markdown("Claude response:", advice)
    else:
        st.error("No data available for analysis")
        
except Exception as e:
    st.error("An error occurred while loading the page")
    with debug_expander:
        st.error(f"Error type: {type(e).__name__}")
        st.error(f"Error message: {str(e)}")
        st.error("Traceback:")
        st.code(traceback.format_exc())