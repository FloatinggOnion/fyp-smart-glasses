import io
import os
import cv2
import numpy as np
import re
from datetime import datetime
from typing import List, Dict, Optional

# import google.generativeai as genai
from google import genai
from google.genai import types
from dotenv import load_dotenv
from PIL import Image

# Create the Part object with the image data
from camera_service import get_latest_frame

# Load environment variables
load_dotenv()


def strip_markdown(text: str) -> str:
    """
    Remove markdown formatting from text to make it suitable for text-to-speech.
    
    Args:
        text (str): Text that may contain markdown formatting
        
    Returns:
        str: Clean text without markdown
    """
    if not text:
        return text
    
    # Remove markdown headers
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    
    # Remove bold formatting
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'__(.*?)__', r'\1', text)
    
    # Remove italic formatting
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    text = re.sub(r'_(.*?)_', r'\1', text)
    
    # Remove code blocks
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    
    # Remove inline code
    text = re.sub(r'`(.*?)`', r'\1', text)
    
    # Remove links but keep the text
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    
    # Remove horizontal rules
    text = re.sub(r'^---$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\*\*\*$', '', text, flags=re.MULTILINE)
    
    # Remove blockquotes
    text = re.sub(r'^>\s+', '', text, flags=re.MULTILINE)
    
    # Remove list markers but keep the content
    text = re.sub(r'^[\s]*[-*+]\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^[\s]*\d+\.\s+', '', text, flags=re.MULTILINE)
    
    # Clean up extra whitespace
    text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)  # Multiple newlines to double newlines
    text = re.sub(r'^\s+', '', text, flags=re.MULTILINE)  # Leading whitespace
    text = re.sub(r'\s+$', '', text, flags=re.MULTILINE)  # Trailing whitespace
    
    # Remove any remaining markdown-like patterns
    text = re.sub(r'^\s*[-*+]\s*$', '', text, flags=re.MULTILINE)  # Empty list items
    text = re.sub(r'^\s*\d+\.\s*$', '', text, flags=re.MULTILINE)  # Empty numbered items
    
    return text.strip()


class SceneService:
    def __init__(self):
        self.scenes_dir = "scenes"
        self.ensure_scenes_directory()
        self.client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
        # self.model = genai.GenerativeModel("models/gemini-1.5-pro-001")

    def get_current_image(self):
        latest_frame = get_latest_frame()
        return latest_frame

    def ensure_scenes_directory(self):
        """Ensure the scenes directory exists."""
        if not os.path.exists(self.scenes_dir):
            os.makedirs(self.scenes_dir)

    def save_screenshot_from_image(self, image: Image.Image) -> Dict:
        """Save a screenshot from a provided PIL Image."""
        print("SceneService: Entering save_screenshot_from_image function.")
        try:
            # Create a unique filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"scene_{timestamp}.jpg"
            filepath = os.path.join(self.scenes_dir, filename)

            # Save the provided image
            image.save(filepath, format="JPEG")
            print(f"SceneService: Screenshot saved to {filepath}.")

            return {
                "status": "success",
                "filepath": filepath,
                "timestamp": timestamp,
            }
        except Exception as e:
            print(f"SceneService: Error saving screenshot from image: {e}")
            return {"status": "error", "message": "I couldn't save that screenshot. There might be an issue with the image or storage."}

    def describe_scene_from_image(self, image: Image.Image) -> Dict:
        """Describe a single scene from a provided PIL Image."""
        print("SceneService: Entering describe_scene_from_image function.")
        try:
            image_bytes = io.BytesIO()
            image.save(image_bytes, format="PNG")
            image_bytes = image_bytes.getvalue()
            print("SceneService: Image converted to bytes for scene description.")

            # Now use the bytes with generate_content
            print("SceneService: Sending scene description request to Gemini.")
            response = self.client.models.generate_content(
                model="gemini-2.0-flash",
                contents=[
                    types.Part.from_bytes(data=image_bytes, mime_type="image/png"),
                    f"Describe what you see in this photo in a natural, conversational way. Focus on the general scene, any people, and what might be happening. Speak as if you're describing it to a friend.",
                ],
            )
            print(f"SceneService: Received scene description response from Gemini: {response.text[:100]}...")
            return {
                "status": "success",
                "description": strip_markdown(response.text),
                "source": "provided_image",
            }
        except Exception as e:
            print(f"SceneService: Error describing scene: {e}")
            return {"status": "error", "message": "I'm having trouble describing what I see in that image. The image might be unclear or there could be a processing issue."}

    def save_screenshot(self) -> Dict:
        print("SceneService: Entering save_screenshot function.")
        try:
            # Create a unique filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"scene_{timestamp}.jpg"
            filepath = os.path.join(self.scenes_dir, filename)

            # Get current image and save it
            image = self.get_current_image()
            if image is None:
                print("SceneService: No image available for saving screenshot.")
                return {"status": "error", "message": "I don't have a current image to save. Try taking a photo first."}
            image.save(filepath, format="JPEG")
            print(f"SceneService: Screenshot saved to {filepath}.")

            return {
                "status": "success",
                "filepath": filepath,
                "timestamp": timestamp,
            }
        except Exception as e:
            print(f"SceneService: Error saving screenshot: {e}")
            return {"status": "error", "message": "I couldn't save that screenshot. There might be an issue with the image or storage."}

    def get_daily_scenes(self, date: Optional[str] = None) -> List[str]:
        print(f"SceneService: Entering get_daily_scenes for date: {date}.")
        if date is None:
            date = datetime.now().strftime("%Y%m%d")
            print(f"SceneService: No date provided, using current date: {date}.")

        scenes = []
        for filename in os.listdir(self.scenes_dir):
            if filename.startswith(f"scene_{date}"):
                scenes.append(os.path.join(self.scenes_dir, filename))
        print(f"SceneService: Found {len(scenes)} scenes for date {date}.")
        return scenes

    def get_daily_recap(self, date: Optional[str] = None) -> Dict:
        """Get a comprehensive description of all scenes from a specific date."""
        print(f"SceneService: Entering get_daily_recap for date: {date}.")
        try:
            # Get scenes from the specified date
            scenes = self.get_daily_scenes(date)
            if not scenes:
                print(f"SceneService: No scenes found for {date} for daily recap.")
                
                # Parse the date for a natural response
                try:
                    if date:
                        # Format: YYYYMMDD
                        year = date[:4]
                        month = date[4:6]
                        day = date[6:8]
                        readable_date = f"{year}-{month}-{day}"
                        
                        # Create natural response based on whether it's today or another day
                        from datetime import datetime
                        today = datetime.now().strftime("%Y%m%d")
                        
                        if date == today:
                            natural_response = "I don't have any photos from today yet. It looks like you haven't taken any pictures with your glasses today, or they haven't been saved yet."
                        else:
                            natural_response = f"I don't have any photos from {readable_date}. It seems like you didn't take any pictures with your glasses on that day, or they weren't saved."
                    else:
                        natural_response = "I don't have any photos from today yet. It looks like you haven't taken any pictures with your glasses today."
                        
                except Exception as e:
                    print(f"Error parsing date for natural response: {e}")
                    natural_response = "I don't have any photos from that day. It seems like no pictures were taken or saved on that date."
                
                return {
                    "status": "success",
                    "description": natural_response,
                    "source": "no_data",
                    "scenes_used": [],
                    "scene_count": 0,
                }

            # Load all scene images and prepare them for Gemini
            scene_images = []
            scene_descriptions = []
            timestamps = []
            
            for i, scene_path in enumerate(scenes):
                try:
                    # Load the image
                    scene_image = Image.open(scene_path)
                    
                    # Convert to bytes for Gemini
                    image_bytes = io.BytesIO()
                    scene_image.save(image_bytes, format="PNG")
                    image_bytes = image_bytes.getvalue()
                    
                    # Add to the list of images
                    scene_images.append(types.Part.from_bytes(data=image_bytes, mime_type="image/png"))
                    
                    # Get timestamp from filename for context
                    filename = os.path.basename(scene_path)
                    timestamp_str = filename.replace("scene_", "").replace(".jpg", "")
                    
                    # Parse timestamp for better formatting
                    try:
                        # Format: YYYYMMDD_HHMMSS
                        date_part = timestamp_str[:8]
                        time_part = timestamp_str[9:]
                        
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
                        
                        timestamps.append({
                            "index": i + 1,
                            "time": readable_time,
                            "date": readable_date,
                            "raw": timestamp_str
                        })
                        
                        scene_descriptions.append(f"Photo {i+1} taken at {readable_time if 'readable_time' in locals() else 'unknown time'}")
                        
                    except Exception as e:
                        print(f"Error parsing timestamp {timestamp_str}: {e}")
                        timestamps.append({
                            "index": i + 1,
                            "time": "unknown",
                            "date": "unknown",
                            "raw": timestamp_str
                        })
                        scene_descriptions.append(f"Photo {i+1}")
                    
                    print(f"SceneService: Loaded scene {i+1}: {filename} at {readable_time if 'readable_time' in locals() else 'unknown time'}")
                    
                except Exception as e:
                    print(f"SceneService: Error loading scene {scene_path}: {e}")
                    continue

            if not scene_images:
                return {
                    "status": "success",
                    "description": "I found some photos from that day, but I'm having trouble loading them right now. This might be a temporary issue with the files or storage. You could try again in a moment, or check if the photos are still available.",
                    "source": "load_error",
                    "scenes_used": [],
                    "scene_count": 0,
                }

            # Create a comprehensive prompt for daily recap
            timestamp_info = "\n".join([f"Photo {ts['index']}: {ts['time']}" for ts in timestamps])
            
            prompt = f"""You are a personal assistant helping someone understand their day through photos they've taken. You have {len(scene_images)} photos from the same day.

Photo timestamps:
{timestamp_info}

Please provide a personalized, conversational overview of their day based on these photos. Focus on:

1. **Timeline and Flow**: Use the specific timestamps to tell the story of their day chronologically
2. **Personal Narrative**: Speak directly to them about what they were doing, as if you're having a conversation
3. **General Overview**: Give a broad sense of their activities rather than detailed analysis of each image
4. **Daily Patterns**: Notice any routines, activities, or interesting moments in their day
5. **Natural Language**: Use "you" and speak conversationally, like "You started your day at {timestamps[0]['time'] if timestamps else 'early'}..." or "Later that morning, you were..."

Avoid detailed technical analysis of the images. Instead, focus on the human story and personal experience of their day.

Please provide a warm, conversational summary of their day's activities, incorporating the specific times when they took these photos."""

            # Send all images and prompt to Gemini
            print(f"SceneService: Sending {len(scene_images)} scenes to Gemini for daily recap.")
            
            # Prepare content with all images and the prompt
            content = scene_images + [prompt]
            
            response = self.client.models.generate_content(
                model="gemini-2.0-flash", 
                contents=content
            )
            
            print(f"SceneService: Received daily recap response from Gemini: {response.text[:100]}...")
            return {
                "status": "success",
                "description": strip_markdown(response.text),
                "source": "daily_recap",
                "scenes_used": scenes,
                "scene_count": len(scene_images),
            }
        except Exception as e:
            print(f"SceneService: Error getting daily recap: {e}")
            return {"status": "error", "message": "I'm having trouble creating your daily recap right now. This might be a temporary issue with the photo processing or storage. You could try again in a moment."}

    def answer_image_query(self, query: str) -> Dict:
        print(f"SceneService: Entering answer_image_query with query: {query}.")
        try:
            image = self.get_current_image()  # This returns a PIL Image
            if image is None:
                print("SceneService: No image available for image query.")
                return {"status": "error", "message": "I don't have a current image to analyze. Try taking a photo first."}
            image_bytes = io.BytesIO()
            image.save(image_bytes, format="PNG")
            image_bytes = image_bytes.getvalue()  # Get the bytes data
            print("SceneService: Image converted to bytes for Gemini.")

            # Now use the bytes with generate_content
            print("SceneService: Sending image query to Gemini.")
            response = self.client.models.generate_content(
                model="gemini-2.0-flash",
                contents=[
                    types.Part.from_bytes(data=image_bytes, mime_type="image/png"),
                    query,
                ],
            )
            print(f"SceneService: Received image query response from Gemini: {response.text[:100]}...")
            return {
                "status": "success",
                "description": strip_markdown(response.text),
                "source": "provided_image",
            }
        except Exception as e:
            print(f"SceneService: Error answering image query: {e}")
            return {"status": "error", "message": "I'm having trouble analyzing that image right now. The image might be unclear or there could be a processing issue."}

    def describe_scene(self) -> Dict:
        """Describe a single scene from the provided image URL."""
        print("SceneService: Entering describe_scene function.")
        try:
            image = self.get_current_image()  # This returns a PIL Image
            if image is None:
                print("SceneService: No image available to describe scene.")
                return {"status": "error", "message": "I don't have a current image to describe. Try taking a photo first."}
            image_bytes = io.BytesIO()
            image.save(image_bytes, format="PNG")
            image_bytes = image_bytes.getvalue()  # Get the bytes data
            print("SceneService: Image converted to bytes for scene description.")

            # Now use the bytes with generate_content
            print("SceneService: Sending scene description request to Gemini.")
            response = self.client.models.generate_content(
                model="gemini-2.0-flash",
                contents=[
                    types.Part.from_bytes(data=image_bytes, mime_type="image/png"),
                    f"Describe what you see in this photo in a natural, conversational way. Focus on the general scene, any people, and what might be happening. Speak as if you're describing it to a friend.",
                ],
            )
            print(f"SceneService: Received scene description response from Gemini: {response.text[:100]}...")
            return {
                "status": "success",
                "description": strip_markdown(response.text),
                "source": "provided_image",
            }
        except Exception as e:
            print(f"SceneService: Error describing scene: {e}")
            return {"status": "error", "message": "I'm having trouble describing what I see in that image. The image might be unclear or there could be a processing issue."}
