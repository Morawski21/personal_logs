import datetime as dt
import pandas as pd

def filter_date_range(df, end_date=None, delta_days=7, offset_days=0):
    """
    Filter DataFrame for a specific date range with optional offset.
    
    Args:
        df (pd.DataFrame): DataFrame containing 'Data' column
        end_date (datetime, optional): End date for filtering. Defaults to today.
        delta_days (int, optional): Number of days to look back. Defaults to 7.
        offset_days (int, optional): Number of days to offset the period. Defaults to 0.
        
    Returns:
        pd.DataFrame: filtered_date_range
    """
    if end_date is None:
        # Convert to pandas Timestamp to match DataFrame's datetime64
        end_date = pd.Timestamp.now().normalize()
    else:
        # Ensure end_date is a pandas Timestamp
        end_date = pd.Timestamp(end_date)
    
    # Apply offset to end date
    end_date = end_date - pd.Timedelta(days=offset_days)
    
    # Filtered period
    filtered_date_range = df[
        (df['Data'] > (end_date - pd.Timedelta(days=delta_days))) &
        (df['Data'] <= end_date)
    ]
    
    return filtered_date_range



import numpy as np
import pandas as pd

def calculate_balance_score(time_data):
    """
    Calculate balance score based on time distribution across activities.
    
    Args:
        time_data (pd.Series): Series containing time values for different activities
    
    Returns:
        float or None: Balance score between 0-100, or None if all values are NA
    """
    # Check if all values are NA
    if time_data.isna().all():
        return None
    
    # Filter out NA values
    time_data = time_data.fillna(0)
    
    if time_data.sum() == 0:
        return 0
    
    # Calculate proportions of time spent on each activity
    proportions = time_data / time_data.sum()
    
    # Calculate perfect distribution (equal time for all activities)
    ideal_proportion = 1.0 / len(time_data)
    
    # Calculate variance from ideal distribution
    variance = np.sum((proportions - ideal_proportion) ** 2)
    
    # Convert variance to score (0-100)
    # Max variance is when all time is spent on one activity: (1 - 1/n)^2 + (n-1)(0 - 1/n)^2
    n = len(time_data)
    max_variance = (1 - 1/n)**2 + (n-1)*(0 - 1/n)**2
    
    # Convert to score where 0 variance = 100 and max variance = 0
    score = 100 * (1 - variance/max_variance)
    
    return max(0, min(100, score))  # Ensure score is between 0 and 100
