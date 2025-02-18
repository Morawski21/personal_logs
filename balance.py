import numpy as np
import pandas as pd

def calculate_balance_score(time_data):
    """
    Calculate balance score based on time distribution across activities.
    
    Args:
        time_data (pd.Series): Series containing time values for different activities
    
    Returns:
        float: Balance score between 0-100
    """
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
