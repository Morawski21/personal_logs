import datetime as dt
import pandas as pd
import numpy as np

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

def get_last_n_valid_days(df, n=7, date_column='Data', value_column='Razem'):
    """
    Get the last n valid days (excluding NA days) from a DataFrame.
    
    Args:
        df (pd.DataFrame): DataFrame containing date and value columns
        n (int): Number of valid days to retrieve
        date_column (str): Name of the date column
        value_column (str): Name of the value column to check for NA values
        
    Returns:
        pd.DataFrame: DataFrame containing the last n valid days
    """
    # Sort by date descending
    sorted_df = df.sort_values(date_column, ascending=False)
    
    # Filter out rows where value_column is NA
    valid_df = sorted_df[sorted_df[value_column].notna()]
    
    # Take the first n rows
    result_df = valid_df.head(n)
    
    # Sort back by date ascending
    return result_df.sort_values(date_column, ascending=True)

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