import io
import os
import cv2
import numpy as np
from datetime import datetime
from typing import List, Dict, Optional

# import google.generativeai as genai
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Create the Part object with the image data
from camera_service import get_latest_frame

# Load environment variables
load_dotenv()


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
                return {"status": "error", "message": "No image available"}
            image.save(filepath, format="JPEG")
            print(f"SceneService: Screenshot saved to {filepath}.")

            return {
                "status": "success",
                "filepath": filepath,
                "timestamp": timestamp,
            }
        except Exception as e:
            print(f"SceneService: Error saving screenshot: {e}")
            return {"status": "error", "message": str(e)}

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
                return {
                    "status": "error",
                    "message": "No scenes found for the specified date",
                }

            # Create a prompt with all scenes
            prompt = "Here are several scenes from the same day. Please provide a comprehensive description of what happened throughout the day based on these scenes:\n"
            for scene in scenes:
                prompt += f"Scene: {scene}\n"
            print("SceneService: Sending daily recap prompt to Gemini.")
            response = self.client.models.generate_content(
                model="gemini-2.0-flash", contents=[prompt]
            )
            print(f"SceneService: Received daily recap response from Gemini: {response.text[:100]}...")
            return {
                "status": "success",
                "description": response.text,
                "source": "daily_recap",
                "scenes_used": scenes,
            }
        except Exception as e:
            print(f"SceneService: Error getting daily recap: {e}")
            return {"status": "error", "message": str(e)}

    def answer_image_query(self, query: str) -> Dict:
        print(f"SceneService: Entering answer_image_query with query: {query}.")
        try:
            image = self.get_current_image()  # This returns a PIL Image
            if image is None:
                print("SceneService: No image available for image query.")
                return {"status": "error", "message": "No image available"}
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
                "description": response.text,
                "source": "provided_image",
            }
        except Exception as e:
            print(f"SceneService: Error answering image query: {e}")
            return {"status": "error", "message": str(e)}

    def describe_scene(self) -> Dict:
        """Describe a single scene from the provided image URL."""
        print("SceneService: Entering describe_scene function.")
        try:
            image = self.get_current_image()  # This returns a PIL Image
            if image is None:
                print("SceneService: No image available to describe scene.")
                return {"status": "error", "message": "No image available"}
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
                    f"Describe this scene in detail:",
                ],
            )
            print(f"SceneService: Received scene description response from Gemini: {response.text[:100]}...")
            return {
                "status": "success",
                "description": response.text,
                "source": "provided_image",
            }
        except Exception as e:
            print(f"SceneService: Error describing scene: {e}")
            return {"status": "error", "message": str(e)}
