import os
from datetime import datetime

import streamlit as st
from anthropic import Anthropic
import pandas as pd


def get_claude_client():
    """Initialize Claude client with API key."""
    try:
        api_key = os.environ["ANTHROPIC_KEY"]
        
        if not api_key:
            raise ValueError("ANTHROPIC_KEY not found in environment")
            
        return Anthropic(api_key=api_key)
        
    except Exception as e:
        print(f"Failed to initialize Claude client: {str(e)}")
        return None

def generate_context(df: pd.DataFrame):
    """Generate context about recent activities for Claude."""
    today = datetime.now()
    today_weekday = today.strftime("%A")
    is_weekend = today.weekday() >= 5
    
    last_7_days = df.tail(7)
    last_30_days = df.tail(30)
    
    # Check if 'Data' column exists for date information
    if 'Data' in df.columns:
        # Create day-specific insights
        weekday_avg = last_30_days[~last_30_days['Data'].dt.weekday.isin([5, 6])]['Razem'].mean()
        weekend_avg = last_30_days[last_30_days['Data'].dt.weekday.isin([5, 6])]['Razem'].mean()
        
        # Get same weekday average from past data
        same_weekday_data = last_30_days[last_30_days['Data'].dt.weekday == today.weekday()]
        same_weekday_avg = same_weekday_data['Razem'].mean() if not same_weekday_data.empty else 0
    else:
        # Fallback if no date column exists
        weekday_avg = last_30_days['Razem'].mean()
        weekend_avg = weekday_avg
        same_weekday_avg = weekday_avg
    
    context = (
        f"Based on the last 7 days of activity data:\n"
        f"Average daily productive time: {last_7_days['Razem'].mean():.0f} minutes\n"
        f"Most productive day: {last_7_days['Razem'].max():.0f} minutes\n"
        f"Least productive day: {last_7_days['Razem'].min():.0f} minutes\n\n"
        f"Productivity patterns:\n"
        f"Weekday average: {weekday_avg:.0f} minutes\n"
        f"Weekend average: {weekend_avg:.0f} minutes\n"
        f"Average for {today_weekday}s: {same_weekday_avg:.0f} minutes\n\n"
        f"Today is {today.strftime('%Y-%m-%d')}, a {today_weekday} {'(weekend)' if is_weekend else '(weekday)'}"
    )
    return context

def get_advice(df: pd.DataFrame) -> str:
    """Get personalized advice from Claude based on recent activity."""
    try:
        client = get_claude_client()
        if client is None:
            return "Error: Could not initialize Claude client. Check your API key."
            
        context = generate_context(df)
        if context is None:
            return "Error: Could not generate context from data."
        
        prompt = f"""
        You are a productivity coach analyzing my daily activity data.
        I am logging extra activities such as YouTube content creation, reading, upskilling at my job as AI Data Scientist, reading books and others.
        I track various habits such as financial planning with YNAB, daily journaling and more.
        The major goal is to increase productivity day by day.

        Here's the context:
        {context}

        Heres the raw data from last 14 days:
        {df.tail(14).to_string()}
        
        Based on this data, please provide:
        1. A brief analysis of my productivity patterns
        2. Specific, personalized advice for today and the upcoming days
        3. Acknowledge if today is a weekend or special day, and adjust your advice accordingly
        
        Keep your response conversational but professional. Avoid generic advice.
        Consider the day of the week in your recommendations - weekend productivity has different expectations than weekdays.
        Include one specific actionable tip I can implement today.
        
        Reply in markdown format. Use headings and occasional emphasis for readability.
        Be motivational but realistic - acknowledge both progress and areas for improvement.
        """
        
        response = client.messages.create(
            model="claude-3-5-haiku-latest",
            max_tokens=750,
            temperature=0.7,
            messages=[{"role": "user", "content": prompt}]
        )
        
        if not response or not response.content:
            return "Error: Received empty response from Claude"
            
        return response.content[0].text
        
    except Exception as e:
        return f"Error in Claude communication: {str(e)}"