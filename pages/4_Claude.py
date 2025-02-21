import streamlit as st
import pandas as pd
from src.data_handler import get_logbook_data
from src.claude_handler import get_advice
import src.utils as utils
import traceback

utils.set_custom_page_config("Claude Assistant")

st.header("🤖 Claude's Daily Insights")

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
        with st.spinner("Claude is analyzing your data..."):
            advice = get_advice(df)
            
            if advice and not advice.startswith("Error"):
                st.markdown(advice)
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
