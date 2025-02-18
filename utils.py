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
                df = pd.read_excel(path, keep_default_na=True, na_values=['', ' '])
                df['Data'] = pd.to_datetime(df['Data'], format='%d.%m.%Y')
                return df, path
        except Exception as e:
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