#!/usr/bin/env python3
"""
Test script to verify natural language date parsing functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
from dateutil import parser, relativedelta
import re

def parse_natural_language_date(query: str) -> str:
    """
    Parse natural language date expressions and return YYYYMMDD format.
    
    Examples:
    - "Recap my day so far" -> today
    - "Give me a recap of what my day was like yesterday" -> yesterday
    - "I need to know what I did two weeks ago" -> two weeks ago
    - "What happened on the 6th of June?" -> June 6th of current year
    - "What happened last Monday?" -> last Monday
    """
    query_lower = query.lower().strip()
    
    # Handle relative dates
    if any(phrase in query_lower for phrase in ["today", "my day so far", "this day", "current day"]):
        return datetime.now().strftime("%Y%m%d")
    
    if any(phrase in query_lower for phrase in ["yesterday", "yesterdays"]):
        yesterday = datetime.now() - timedelta(days=1)
        return yesterday.strftime("%Y%m%d")
    
    if any(phrase in query_lower for phrase in ["tomorrow", "tomorrows"]):
        tomorrow = datetime.now() + timedelta(days=1)
        return tomorrow.strftime("%Y%m%d")
    
    # Handle "X days ago"
    days_ago_match = re.search(r'(\d+)\s+days?\s+ago', query_lower)
    if days_ago_match:
        days = int(days_ago_match.group(1))
        target_date = datetime.now() - timedelta(days=days)
        return target_date.strftime("%Y%m%d")
    
    # Handle "X weeks ago"
    weeks_ago_match = re.search(r'(\d+)\s+weeks?\s+ago', query_lower)
    if weeks_ago_match:
        weeks = int(weeks_ago_match.group(1))
        target_date = datetime.now() - timedelta(weeks=weeks)
        return target_date.strftime("%Y%m%d")
    
    # Handle "X months ago"
    months_ago_match = re.search(r'(\d+)\s+months?\s+ago', query_lower)
    if months_ago_match:
        months = int(months_ago_match.group(1))
        target_date = datetime.now() - relativedelta.relativedelta(months=months)
        return target_date.strftime("%Y%m%d")
    
    # Handle "X years ago"
    years_ago_match = re.search(r'(\d+)\s+years?\s+ago', query_lower)
    if years_ago_match:
        years = int(years_ago_match.group(1))
        target_date = datetime.now() - relativedelta.relativedelta(years=years)
        return target_date.strftime("%Y%m%d")
    
    # Handle "last week", "last month", etc.
    if "last week" in query_lower:
        target_date = datetime.now() - timedelta(weeks=1)
        return target_date.strftime("%Y%m%d")
    
    if "last month" in query_lower:
        target_date = datetime.now() - relativedelta.relativedelta(months=1)
        return target_date.strftime("%Y%m%d")
    
    if "last year" in query_lower:
        target_date = datetime.now() - relativedelta.relativedelta(years=1)
        return target_date.strftime("%Y%m%d")
    
    # Handle specific weekdays
    weekdays = {
        "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
        "friday": 4, "saturday": 5, "sunday": 6
    }
    
    for day_name, day_num in weekdays.items():
        if f"last {day_name}" in query_lower:
            today = datetime.now()
            days_since = (today.weekday() - day_num) % 7
            if days_since == 0:
                days_since = 7  # Last week's same day
            target_date = today - timedelta(days=days_since)
            return target_date.strftime("%Y%m%d")
    
    # Handle absolute dates like "6th of June", "June 6th"
    try:
        # Try to parse with dateutil
        parsed_date = parser.parse(query, fuzzy=True)
        return parsed_date.strftime("%Y%m%d")
    except:
        pass
    
    # If all else fails, return today's date
    print(f"Could not parse date from query: '{query}', defaulting to today")
    return datetime.now().strftime("%Y%m%d")

def test_date_parsing():
    """Test various date parsing scenarios"""
    print("=== Natural Language Date Parsing Test ===\n")
    
    test_cases = [
        "Recap my day so far",
        "Give me a recap of what my day was like yesterday",
        "I need to know what I did two weeks ago",
        "What happened on the 6th of June?",
        "What happened last Monday?",
        "Show me what I did 3 days ago",
        "Tell me about my activities last month",
        "What did I do last year?",
        "Recap yesterday's activities",
        "What happened today?",
        "Show me last Friday's recap",
        "What did I do 5 weeks ago?",
        "Tell me about June 15th",
        "What happened on the 1st of January?",
        "Show me last week's activities",
    ]
    
    today = datetime.now()
    print(f"Current date: {today.strftime('%Y-%m-%d (%A)')}\n")
    
    for i, query in enumerate(test_cases, 1):
        try:
            parsed_date = parse_natural_language_date(query)
            parsed_datetime = datetime.strptime(parsed_date, "%Y%m%d")
            
            print(f"{i:2d}. Query: '{query}'")
            print(f"    Parsed: {parsed_datetime.strftime('%Y-%m-%d (%A)')}")
            
            # Show relative time
            if parsed_datetime.date() == today.date():
                print(f"    → Today")
            elif parsed_datetime.date() == (today - timedelta(days=1)).date():
                print(f"    → Yesterday")
            elif parsed_datetime.date() == (today + timedelta(days=1)).date():
                print(f"    → Tomorrow")
            else:
                days_diff = (today.date() - parsed_datetime.date()).days
                if days_diff > 0:
                    print(f"    → {days_diff} days ago")
                else:
                    print(f"    → {abs(days_diff)} days from now")
            print()
            
        except Exception as e:
            print(f"{i:2d}. Query: '{query}'")
            print(f"    Error: {e}")
            print()

if __name__ == "__main__":
    test_date_parsing() 