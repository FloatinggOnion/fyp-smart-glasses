#!/usr/bin/env python3
"""
Test script to verify camera connection and endpoints
"""

import requests
import time

# Configuration
CAMERA_IP = "http://192.168.0.179"  # Updated camera IP
CAPTURE_ENDPOINT = f"{CAMERA_IP}/capture"
STREAM_ENDPOINT = f"{CAMERA_IP}/"

def test_camera_connection():
    """Test basic camera connectivity"""
    print("=== Camera Connection Test ===\n")
    
    print(f"Testing camera at: {CAMERA_IP}")
    print(f"Capture endpoint: {CAPTURE_ENDPOINT}")
    print(f"Stream endpoint: {STREAM_ENDPOINT}\n")
    
    # Test 1: Basic connectivity
    print("1. Testing basic connectivity...")
    try:
        response = requests.get(CAPTURE_ENDPOINT, timeout=10)
        print(f"   Status Code: {response.status_code}")
        print(f"   Content Type: {response.headers.get('content-type', 'Unknown')}")
        print(f"   Content Length: {len(response.content)} bytes")
        
        if response.status_code == 200:
            print("   ✓ Camera is accessible")
        else:
            print(f"   ✗ Camera returned error: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("   ✗ Connection failed - camera may be offline or IP incorrect")
        return False
    except requests.exceptions.Timeout:
        print("   ✗ Request timed out - camera may be slow to respond")
        return False
    except Exception as e:
        print(f"   ✗ Unexpected error: {e}")
        return False
    
    # Test 2: Image quality
    print("\n2. Testing image quality...")
    try:
        response = requests.get(CAPTURE_ENDPOINT, timeout=10)
        if response.status_code == 200:
            content_length = len(response.content)
            if content_length > 1000:  # Basic check for reasonable image size
                print(f"   ✓ Image size: {content_length} bytes")
            else:
                print(f"   ⚠ Image seems small: {content_length} bytes")
        else:
            print(f"   ✗ Failed to get image: {response.status_code}")
            
    except Exception as e:
        print(f"   ✗ Error testing image quality: {e}")
    
    # Test 3: Multiple captures
    print("\n3. Testing multiple captures...")
    try:
        for i in range(3):
            response = requests.get(CAPTURE_ENDPOINT, timeout=10)
            if response.status_code == 200:
                print(f"   Capture {i+1}: {len(response.content)} bytes")
            else:
                print(f"   Capture {i+1}: Failed ({response.status_code})")
            time.sleep(1)  # Wait between captures
            
    except Exception as e:
        print(f"   ✗ Error testing multiple captures: {e}")
    
    # Test 4: Stream endpoint (if available)
    print("\n4. Testing stream endpoint...")
    try:
        response = requests.get(STREAM_ENDPOINT, timeout=5)
        print(f"   Status Code: {response.status_code}")
        print(f"   Content Type: {response.headers.get('content-type', 'Unknown')}")
        
        if response.status_code == 200:
            print("   ✓ Stream endpoint is accessible")
        else:
            print(f"   ⚠ Stream endpoint returned: {response.status_code}")
            
    except Exception as e:
        print(f"   ⚠ Stream endpoint error: {e}")
    
    print("\n=== Test Complete ===")
    return True

def test_mobile_api_with_camera():
    """Test the mobile API endpoints with actual camera images"""
    print("\n=== Mobile API Test with Camera ===\n")
    
    API_BASE_URL = "http://localhost:8000"
    
    # Get a fresh image from camera
    print("Getting fresh image from camera...")
    try:
        response = requests.get(CAPTURE_ENDPOINT, timeout=10)
        if response.status_code != 200:
            print("Failed to get camera image")
            return
            
        import base64
        image_base64 = base64.b64encode(response.content).decode('utf-8')
        print(f"Image captured: {len(image_base64)} characters")
        
        # Test scene description
        print("\nTesting scene description...")
        scene_response = requests.post(f"{API_BASE_URL}/describe_scene", json={
            "image": image_base64
        })
        print(f"Scene Description Status: {scene_response.status_code}")
        if scene_response.status_code == 200:
            result = scene_response.json()
            print(f"Scene Description: {result.get('description', 'No description')[:100]}...")
        
        # Test OCR
        print("\nTesting OCR...")
        ocr_response = requests.post(f"{API_BASE_URL}/extract_text", json={
            "image": image_base64
        })
        print(f"OCR Status: {ocr_response.status_code}")
        if ocr_response.status_code == 200:
            result = ocr_response.json()
            print(f"Extracted Text: {result.get('text_lines', [])}")
        
    except Exception as e:
        print(f"Error testing mobile API: {e}")

if __name__ == "__main__":
    # Run camera connection test
    if test_camera_connection():
        # If camera is working, test mobile API
        test_mobile_api_with_camera()
    else:
        print("\nCamera connection failed. Please check:")
        print("1. Camera IP address is correct")
        print("2. Camera is powered on and connected to network")
        print("3. Network connectivity between this machine and camera")
        print("4. Camera firmware is running correctly") 