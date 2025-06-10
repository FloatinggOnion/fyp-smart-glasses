import os
import numpy as np
from typing import List, Optional
from google.cloud import vision
import requests
from io import BytesIO

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

    def extract_text(self) -> List[str]:
        """
        Extract text from an image using Google Cloud Vision API.

        Args:
            image_url (str): URL of the image to analyze

        Returns:
            List[str]: List of extracted text blocks
        """
        print("OCRService: Entering extract_text function.")
        # Download the image
        image_content = self.get_current_image()
        if image_content is None:
            print("OCRService: No image available for OCR.")
            return []

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
                return []

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
            return []
