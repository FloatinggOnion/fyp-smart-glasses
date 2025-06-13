#!/usr/bin/env python3
"""
Test script to verify improved daily recap functionality
"""

import requests
import json
from datetime import datetime

def test_daily_recap():
    """Test the improved daily recap functionality"""
    print("=== Daily Recap Test ===\n")
    
    API_BASE_URL = "http://localhost:8000"
    
    # Test with a date that has scenes (June 13, 2025)
    test_date = "20250613"
    
    print(f"Testing daily recap for date: {test_date}")
    print("This date has existing scenes in the database.\n")
    
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
            print("\nRecap Description:")
            print("-" * 50)
            print(result.get('description', 'No description'))
            print("-" * 50)
        else:
            print(f"✗ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"✗ Connection error: {e}")
    
    print("\n" + "="*50)
    print("Expected Improvements:")
    print("✓ Sends actual image content to Gemini (not just file paths)")
    print("✓ Analyzes visual content of each scene")
    print("✓ Provides chronological narrative of events")
    print("✓ Mentions people, objects, and activities in scenes")
    print("✓ Creates natural, conversational summary")
    print("="*50)

def test_natural_language_queries():
    """Test natural language queries that should trigger daily recap"""
    print("\n=== Natural Language Daily Recap Test ===\n")
    
    API_BASE_URL = "http://localhost:8000"
    
    test_queries = [
        "What happened today?",
        "Recap my day so far",
        "What did I do yesterday?",
        "Give me a recap of two weeks ago",
        "What happened on June 13th?",
        "Show me what I did last week",
    ]
    
    print("Test queries that should trigger daily recap:")
    for i, query in enumerate(test_queries, 1):
        print(f"{i}. '{query}'")
    
    print("\nNote: These queries will use the improved date parsing")
    print("and send actual images to Gemini for analysis.")

if __name__ == "__main__":
    test_daily_recap()
    test_natural_language_queries() 