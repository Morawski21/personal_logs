import os
import datetime as dt
import pandas as pd
from datetime import datetime
import streamlit as st

import src.config as config

def get_data_paths(filename: str = config.FILENAME):
    """Return possible data file paths."""
    return [
        os.path.join('data', filename),  # Local development path
        
        os.path.join('/app/data', filename),  # Docker container path
    ]

def load_logbook_data(filename: str = config.FILENAME):
    """Load the logbook data from the first available path."""
    data_paths = get_data_paths(filename)
    
    for path in data_paths:
        try:
            if os.path.exists(path):
                # Explicitly set which values should be treated as NA
                # Empty strings and spaces will be NA, but preserve actual NA values
                df = pd.read_excel(path, keep_default_na=True, na_values=['', ' '])
                
                # Ensure numeric columns preserve actual NA values and don't convert them to 0
                numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
                for col in numeric_cols:
                    # Convert empty strings that might have been missed to NaN
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                
                return df, path
            
        except Exception as e:
            print(f"Error loading file {path}: {str(e)}")
            continue
    
    raise FileNotFoundError("Could not find or load Logbook 2025.xlsx in any known location")


def preprocess_logbook_data(df: pd.DataFrame) -> pd.DataFrame:
    """Preprocess the logbook data by converting dates and handling NA values."""
    df = df.copy()  # Create a copy to avoid modifying the original dataframe
    
    # Convert dates
    df['Data'] = pd.to_datetime(df['Data'], format='%d.%m.%Y')

    # Filter out future dates
    today = dt.datetime.now()
    df = df[df['Data'] <= today]
    
    # Handle NA values in numeric columns of the last row
    numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
    last_row_index = df.index[-1]
    
    for col in numeric_cols:
        if pd.isna(df.loc[last_row_index, col]) or df.loc[last_row_index, col] == 0:
            df.loc[last_row_index, col] = 0.0
    
    return df

def get_logbook_data(filename: str = config.FILENAME) -> tuple[pd.DataFrame, str]:
    """Load and preprocess the logbook data."""
    df, path = load_logbook_data(filename)
    df = preprocess_logbook_data(df)
    return df, path