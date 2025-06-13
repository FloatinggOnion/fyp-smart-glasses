#!/usr/bin/env python3
"""
Test script for the mobile-first API endpoints
"""

import requests
import base64
import json
from PIL import Image
import io

# Configuration
API_BASE_URL = "http://localhost:8000"  # Change this to your backend URL
TEST_IMAGE_PATH = "frame_20250506_085146.jpg"  # Use an existing test image

def image_to_base64(image_path: str) -> str:
    """Convert image file to base64 string"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def test_query_with_image():
    """Test the /query endpoint with image"""
    print("Testing /query endpoint with image...")
    
    try:
        # Convert test image to base64
        image_base64 = image_to_base64(TEST_IMAGE_PATH)
        
        # Test query that requires image
        query_data = {
            "query": "What do you see in this image?",
            "image": image_base64
        }
        
        response = requests.post(f"{API_BASE_URL}/query", json=query_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
    except Exception as e:
        print(f"Error testing query with image: {e}")

def test_query_without_image():
    """Test the /query endpoint without image"""
    print("\nTesting /query endpoint without image...")
    
    try:
        # Test query that doesn't require image
        query_data = {
            "query": "Hello, how are you?"
        }
        
        response = requests.post(f"{API_BASE_URL}/query", json=query_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
    except Exception as e:
        print(f"Error testing query without image: {e}")

def test_extract_text():
    """Test the /extract_text endpoint"""
    print("\nTesting /extract_text endpoint...")
    
    try:
        # Convert test image to base64
        image_base64 = image_to_base64(TEST_IMAGE_PATH)
        
        request_data = {
            "image": image_base64
        }
        
        response = requests.post(f"{API_BASE_URL}/extract_text", json=request_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
    except Exception as e:
        print(f"Error testing extract_text: {e}")

def test_describe_scene():
    """Test the /describe_scene endpoint"""
    print("\nTesting /describe_scene endpoint...")
    
    try:
        # Convert test image to base64
        image_base64 = image_to_base64(TEST_IMAGE_PATH)
        
        request_data = {
            "image": image_base64
        }
        
        response = requests.post(f"{API_BASE_URL}/describe_scene", json=request_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
    except Exception as e:
        print(f"Error testing describe_scene: {e}")

def test_save_screenshot():
    """Test the /save_screenshot endpoint"""
    print("\nTesting /save_screenshot endpoint...")
    
    try:
        # Convert test image to base64
        image_base64 = image_to_base64(TEST_IMAGE_PATH)
        
        request_data = {
            "image": image_base64
        }
        
        response = requests.post(f"{API_BASE_URL}/save_screenshot", json=request_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
    except Exception as e:
        print(f"Error testing save_screenshot: {e}")

def test_requires_image_detection():
    """Test the intelligent image requirement detection"""
    print("\nTesting image requirement detection...")
    
    test_queries = [
        "What do you see?",
        "Read the text in this image",
        "Who is this person?",
        "Hello, how are you?",
        "What's the weather like?",
        "Describe this scene",
        "Save this screenshot"
    ]
    
    for query in test_queries:
        try:
            response = requests.post(f"{API_BASE_URL}/query", json={"query": query})
            result = response.json()
            
            if result.get("requires_image"):
                print(f"✓ '{query}' - Requires image")
            else:
                print(f"✗ '{query}' - No image required")
                
        except Exception as e:
            print(f"Error testing query '{query}': {e}")

if __name__ == "__main__":
    print("=== Mobile-First API Test Suite ===\n")
    
    # Run all tests
    test_query_with_image()
    test_query_without_image()
    test_extract_text()
    test_describe_scene()
    test_save_screenshot()
    test_requires_image_detection()
    
    print("\n=== Test Suite Complete ===") 