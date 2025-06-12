import requests
from PIL import Image, ImageEnhance
import io
import time
import datetime
from typing import Optional

# CAPTURE_URL = "http://10.42.0.114/capture" # Use the capture endpoint
CAPTURE_URL = "http://192.168.137.58/capture"
_last_frame: Optional[Image.Image] = None
_last_frame_time: float = 0

def get_latest_frame() -> Optional[Image.Image]:
    """Get the latest frame from the camera. Returns None if no frame is available."""
    global _last_frame, _last_frame_time
    
    # If we have a recent frame (less than 1 second old), return it
    if _last_frame is not None and time.time() - _last_frame_time < 1.0:
        return _last_frame
        
    try:
        print(f"Attempting to fetch image from camera at: {CAPTURE_URL}")
        # request to remove jitter
        requests.get(CAPTURE_URL, timeout=5) # Increased timeout to 5 seconds
        response = requests.get(CAPTURE_URL, timeout=5) # Increased timeout to 5 seconds
        if response.status_code == 200:
            print("Successfully fetched image from camera.")
            img = Image.open(io.BytesIO(response.content))
            img.verify()
            img = Image.open(io.BytesIO(response.content))

            # Rotate 90 degrees clockwise
            img = img.rotate(90, expand=True)

            # Enhance sharpness
            img = ImageEnhance.Sharpness(img).enhance(2.0)

            # Enhance contrast
            img = ImageEnhance.Contrast(img).enhance(1.5)

            # Enhance brightness
            img = ImageEnhance.Brightness(img).enhance(1.2)

            # Enhance color
            img = ImageEnhance.Color(img).enhance(1.3)

            _last_frame = img
            _last_frame_time = time.time()
            return img
    except Exception as e:
        print(f"Warning: Failed to get frame from camera at {CAPTURE_URL}: {e}")
        return None

def save_image(image: Optional[Image.Image], filename: str | None = None):
    """Save an image to disk. If no image is provided, tries to get the latest frame."""
    if image is None:
        image = get_latest_frame()
        if image is None:
            print("Warning: No image available to save")
            return
            
    if filename is None:
        # Auto-generate a filename with timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"frame_{timestamp}.jpg"
    image.save(filename, format="JPEG", quality=95)
    print(f"Image saved to {filename}")
