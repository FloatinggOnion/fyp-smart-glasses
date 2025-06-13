import os
import numpy as np
from typing import List, Optional
from google.cloud import vision
import requests
from io import BytesIO
from PIL import Image

from camera_service import get_latest_frame


class OCRService:
    def __init__(self):
        """
        Initialize the OCR service using Google Cloud Vision API.
        Requires GOOGLE_APPLICATION_CREDENTIALS environment variable to be set.
        """
        self.client = vision.ImageAnnotatorClient()

    def get_current_image(self) -> Optional[np.ndarray]:
        latest_frame = get_latest_frame()
        return np.array(latest_frame)

    def extract_text_from_image(self, image: Image.Image) -> List[str]:
        """
        Extract text from a provided PIL Image using Google Cloud Vision API.

        Args:
            image (Image.Image): PIL Image to analyze

        Returns:
            List[str]: List of extracted text blocks, or ["No text is shown in the image"] if no text found
        """
        print("OCRService: Entering extract_text_from_image function.")
        try:
            # Convert PIL Image to numpy array
            image_array = np.array(image)
            
            # Create image object for Google Cloud Vision
            print("OCRService: Creating Vision Image object.")
            vision_image = vision.Image(content=image_array.tobytes())

            # Perform text detection
            print("OCRService: Performing text detection with Google Cloud Vision.")
            response = self.client.text_detection(image=vision_image)
            texts = response.text_annotations

            if not texts:
                print("OCRService: No text detected.")
                return ["No text is shown in the image"]

            # Extract text from annotations
            # First annotation contains the entire text
            full_text = texts[0].description
            print(f"OCRService: Full text detected: {full_text}")

            # Split into lines and clean up
            text_lines = [
                line.strip() for line in full_text.split("\n") if line.strip()
            ]
            print(f"OCRService: Extracted text lines: {text_lines}")

            return text_lines

        except Exception as e:
            print(f"OCRService: Error in OCR processing: {e}")
            return ["No text is shown in the image"]

    def extract_text(self) -> List[str]:
        """
        Extract text from an image using Google Cloud Vision API.
        Legacy method that gets image from camera.

        Returns:
            List[str]: List of extracted text blocks, or ["No text is shown in the image"] if no text found
        """
        print("OCRService: Entering extract_text function.")
        # Download the image
        image_content = self.get_current_image()
        if image_content is None:
            print("OCRService: No image available for OCR.")
            return ["No text is shown in the image"]

        try:
            # Create image object for Google Cloud Vision
            print("OCRService: Creating Vision Image object.")
            image = vision.Image(content=image_content)

            # Perform text detection
            print("OCRService: Performing text detection with Google Cloud Vision.")
            response = self.client.text_detection(image=image)
            texts = response.text_annotations

            if not texts:
                print("OCRService: No text detected.")
                return ["No text is shown in the image"]

            # Extract text from annotations
            # First annotation contains the entire text
            full_text = texts[0].description
            print(f"OCRService: Full text detected: {full_text}")

            # Split into lines and clean up
            text_lines = [
                line.strip() for line in full_text.split("\n") if line.strip()
            ]
            print(f"OCRService: Extracted text lines: {text_lines}")

            return text_lines

        except Exception as e:
            print(f"OCRService: Error in OCR processing: {e}")
            return ["No text is shown in the image"]
