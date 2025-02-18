import os
import pandas as pd
from datetime import datetime

def get_data_paths():
    """Return possible data file paths."""
    return [
        os.path.join('data', 'Logbook 2025.xlsx'),  # Local development path
        os.path.join('/app/data', 'Logbook 2025.xlsx'),  # Docker container path
    ]

def load_logbook_data():
    """Load the logbook data from the first available path."""
    data_paths = get_data_paths()
    
    for path in data_paths:
        try:
            if os.path.exists(path):
                df = pd.read_excel(path, keep_default_na=True, na_values=['', ' '])  # Removed na_filter=False
                df['Data'] = pd.to_datetime(df['Data'], format='%d.%m.%Y')
                
                # Get numeric columns (excluding 'Data', 'WEEKDAY', etc.)
                numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
                
                # Replace zeros with NAs only in numeric columns of the last row
                last_row_index = df.index[-1]
                for col in numeric_cols:
                    if pd.isna(df.loc[last_row_index, col]) or df.loc[last_row_index, col] == 0 or df.loc[last_row_index, col] == 0.0:
                        df.loc[last_row_index, col] = pd.NA
                
                # Convert columns to nullable integer type to better handle NAs
                for col in numeric_cols:
                    df[col] = df[col].astype('Float64')  # Using Float64 to handle NAs better
                
                return df, path
        except Exception as e:
            print(f"Error loading file {path}: {str(e)}")  # Added error printing for debugging
            continue
    
    raise FileNotFoundError("Could not find or load Logbook 2025.xlsx in any known location")

def calculate_streak(df, column, min_value=1):
    """Calculate the current streak for a given column."""
    streak = 0
    for value in df[column]:
        if value >= min_value:
            streak += 1
        else:
            break
    return streak