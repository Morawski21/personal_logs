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
        os.path.join('Z:\\personal-logs\\data', filename),  # Network drive path
        os.path.join('\\\\NAS\\personal-logs\\data', filename),  # Alternative network path
    ]

def load_logbook_data(filename: str = config.FILENAME):
    """Load the logbook data from the first available path."""
    data_paths = get_data_paths(filename)
    
    for path in data_paths:
        try:
            if os.path.exists(path):
                csv_path = path.replace('.xlsx', '.csv')
                
                # Check if Excel file is newer than CSV or if CSV doesn't exist
                excel_modified = os.path.getmtime(path) if os.path.exists(path) else 0
                csv_modified = os.path.getmtime(csv_path) if os.path.exists(csv_path) else 0
                
                # If Excel is newer or CSV doesn't exist, convert Excel to CSV
                if excel_modified > csv_modified or not os.path.exists(csv_path):
                    print(f"Converting Excel to CSV: {path} -> {csv_path}")
                    # Read from Excel with NA handling
                    excel_df = pd.read_excel(path, keep_default_na=True, na_values=['', ' '])
                    
                    # Ensure numeric columns preserve actual NA values
                    numeric_cols = excel_df.select_dtypes(include=['float64', 'int64']).columns
                    for col in numeric_cols:
                        excel_df[col] = pd.to_numeric(excel_df[col], errors='coerce')
                    
                    # Save to CSV with the same NA handling
                    excel_df.to_csv(csv_path, index=False)
                
                # Read from CSV with consistent NA handling
                df = pd.read_csv(csv_path, keep_default_na=True, na_values=['', ' '])
                
                # Apply the same numeric handling as with Excel
                numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
                for col in numeric_cols:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                
                return df, path
            
        except Exception as e:
            print(f"Error loading file {path}: {str(e)}")
            continue
    
    raise FileNotFoundError(f"Could not find or load {filename} in any known location")


def preprocess_logbook_data(df: pd.DataFrame) -> pd.DataFrame:
    """Preprocess the logbook data by converting dates and handling NA values."""
    df = df.copy()  # Create a copy to avoid modifying the original dataframe
    
    # Convert dates - handle CSV format which may parse dates differently from Excel
    try:
        # First check if Data is already a datetime
        if not pd.api.types.is_datetime64_any_dtype(df['Data']):
            # Try standard date format from CSV
            df['Data'] = pd.to_datetime(df['Data'], errors='coerce')
            
            # If that fails, try the original format
            if df['Data'].isna().all():
                df['Data'] = pd.to_datetime(df['Data'], format='%d.%m.%Y', errors='coerce')
    except Exception as e:
        print(f"Error converting dates: {str(e)}")
        # Fallback to original format
        df['Data'] = pd.to_datetime(df['Data'], format='%d.%m.%Y', errors='coerce')

    # Filter out future dates
    today = dt.datetime.now()
    df = df[df['Data'] <= today]
    
    # Handle NA values in numeric columns of the last row
    numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
    if not df.empty:
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