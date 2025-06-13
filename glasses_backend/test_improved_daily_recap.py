#!/usr/bin/env python3
"""
Test script to verify improved daily recap functionality
"""

import requests
import json
from datetime import datetime

def test_improved_daily_recap():
    """Test the improved daily recap functionality"""
    print("=== Improved Daily Recap Test ===\n")
    
    API_BASE_URL = "http://localhost:8000"
    
    # Test with a date that has scenes (June 13, 2025)
    test_date = "20250613"
    
    print(f"Testing improved daily recap for date: {test_date}")
    print("This date has existing scenes with timestamps: 04:24:22, 04:25:22, 04:26:07")
    print()
    
    try:
        # Test the daily recap endpoint
        response = requests.post(f"{API_BASE_URL}/daily_recap", json={
            "date": test_date
        })
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✓ Daily recap successful!")
            print(f"Scene count: {result.get('scene_count', 'Unknown')}")
            print(f"Scenes used: {len(result.get('scenes_used', []))}")
            print("\nImproved Recap Description:")
            print("-" * 60)
            print(result.get('description', 'No description'))
            print("-" * 60)
        else:
            print(f"✗ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"✗ Connection error: {e}")
    
    print("\n" + "="*60)
    print("Expected Improvements:")
    print("✓ Personalized responses using 'you' and conversational language")
    print("✓ Specific timestamp references (04:24:22, 04:25:22, etc.)")
    print("✓ General overview rather than detailed image analysis")
    print("✓ Focus on human story and personal experience")
    print("✓ Natural timeline flow using actual photo timestamps")
    print("✓ Warm, conversational tone")
    print("="*60)

def test_natural_language_queries():
    """Test natural language queries that should trigger improved daily recap"""
    print("\n=== Natural Language Daily Recap Test ===\n")
    
    API_BASE_URL = "http://localhost:8000"
    
    test_queries = [
        "What happened today?",
        "Recap my day so far",
        "What did I do yesterday?",
        "Give me a recap of two weeks ago",
        "What happened on June 13th?",
        "Show me what I did last week",
        "Tell me about my day",
    ]
    
    print("Test queries that should trigger improved daily recap:")
    for i, query in enumerate(test_queries, 1):
        print(f"{i}. '{query}'")
    
    print("\nExpected improvements in responses:")
    print("- More personalized language ('You started your day at...')")
    print("- Specific time references from photo timestamps")
    print("- General overview rather than detailed analysis")
    print("- Conversational tone and natural flow")

def test_timestamp_parsing():
    """Test the timestamp parsing functionality"""
    print("\n=== Timestamp Parsing Test ===\n")
    
    test_timestamps = [
        "20250613_042422",
        "20250613_042522", 
        "20250613_042607",
        "20250506_085310",
        "20250506_104317",
    ]
    
    print("Testing timestamp parsing:")
    for timestamp in test_timestamps:
        try:
            # Parse timestamp for better formatting
            date_part = timestamp[:8]
            time_part = timestamp[9:]
            
            # Convert to readable format
            year = date_part[:4]
            month = date_part[4:6]
            day = date_part[6:8]
            hour = time_part[:2]
            minute = time_part[2:4]
            second = time_part[4:6]
            
            # Create readable timestamp
            readable_time = f"{hour}:{minute}:{second}"
            readable_date = f"{year}-{month}-{day}"
            
            print(f"  {timestamp} → {readable_date} at {readable_time}")
            
        except Exception as e:
            print(f"  {timestamp} → Error: {e}")

if __name__ == "__main__":
    test_improved_daily_recap()
    test_natural_language_queries()
    test_timestamp_parsing() 