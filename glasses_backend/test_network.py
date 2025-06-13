#!/usr/bin/env python3
"""
Network connectivity test for camera
"""

import requests
import socket
import subprocess
import platform

def test_camera_connectivity():
    """Test camera connectivity from different perspectives"""
    camera_ip = "192.168.0.179"
    camera_url = f"http://{camera_ip}/capture"
    
    print("=== Network Connectivity Test ===\n")
    
    # Test 1: Basic ping
    print("1. Testing basic network connectivity...")
    try:
        if platform.system() == "Windows":
            result = subprocess.run(["ping", "-n", "1", camera_ip], capture_output=True, text=True)
        else:
            result = subprocess.run(["ping", "-c", "1", camera_ip], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("   ✓ Ping successful")
        else:
            print("   ✗ Ping failed")
            print(f"   Output: {result.stdout}")
    except Exception as e:
        print(f"   ✗ Ping error: {e}")
    
    # Test 2: Port connectivity
    print("\n2. Testing port connectivity...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((camera_ip, 80))
        sock.close()
        
        if result == 0:
            print("   ✓ Port 80 is open")
        else:
            print(f"   ✗ Port 80 is closed (error code: {result})")
    except Exception as e:
        print(f"   ✗ Port test error: {e}")
    
    # Test 3: HTTP request from this machine
    print("\n3. Testing HTTP request from this machine...")
    try:
        response = requests.get(camera_url, timeout=5)
        print(f"   Status: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('content-type', 'Unknown')}")
        print(f"   Content-Length: {len(response.content)} bytes")
        
        if response.status_code == 200:
            print("   ✓ HTTP request successful")
        else:
            print(f"   ✗ HTTP request failed: {response.status_code}")
    except requests.exceptions.Timeout:
        print("   ✗ HTTP request timed out")
    except requests.exceptions.ConnectionError:
        print("   ✗ HTTP connection failed")
    except Exception as e:
        print(f"   ✗ HTTP request error: {e}")
    
    # Test 4: Network interface info
    print("\n4. Network interface information...")
    try:
        if platform.system() == "Windows":
            result = subprocess.run(["ipconfig"], capture_output=True, text=True)
        else:
            result = subprocess.run(["ifconfig"], capture_output=True, text=True)
        
        print("   Network interfaces:")
        for line in result.stdout.split('\n'):
            if camera_ip.split('.')[0] in line or "192.168" in line:
                print(f"     {line.strip()}")
    except Exception as e:
        print(f"   Error getting network info: {e}")
    
    print("\n=== Troubleshooting Tips ===")
    print("If the camera is not accessible:")
    print("1. Ensure ESP32 and mobile device are on the same WiFi network")
    print("2. Check if ESP32 is powered on and connected")
    print("3. Verify the camera IP address is correct")
    print("4. Try accessing http://192.168.0.179/capture in a browser")
    print("5. Check ESP32 serial monitor for any error messages")

if __name__ == "__main__":
    test_camera_connectivity() 