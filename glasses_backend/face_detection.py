import os
import requests
from typing import List, Optional, Dict
from deepface import DeepFace
from PIL import Image
import numpy as np
from camera_service import get_latest_frame
from io import BytesIO


class FaceRecognitionClass:
    def __init__(self, faces_dir: str = "faces"):
        """
        Initialize the face recognition system.

        Args:
            faces_dir (str): Directory containing reference face images
        """
        self.faces_dir = faces_dir
        if not os.path.exists(faces_dir):
            os.makedirs(faces_dir)

    def get_current_image(self) -> Optional[np.ndarray]:
        latest_frame = get_latest_frame()
        return np.array(latest_frame)

    def find_face(self) -> List[Dict]:
        """
        Find matching faces from the reference database given an image URL.

        Args:
            image_url (str): URL of the image to analyze

        Returns:
            List[Dict]: List of matches with confidence scores and identities
        """
        print("FaceRecognitionClass: Entering find_face function.")
        # Download and process the image
        image = self.get_current_image()
        if image is None:
            print("FaceRecognitionClass: No image available for face recognition.")
            return []

        try:
            # Analyze the image using DeepFace
            print("FaceRecognitionClass: Attempting to analyze image with DeepFace.")
            results = DeepFace.find(
                img_path=image,
                db_path=self.faces_dir,
                enforce_detection=False,
                model_name="VGG-Face",
            )
            print(f"FaceRecognitionClass: DeepFace analysis returned {len(results)} results.")

            # Process and format results
            matches = []
            for result in results:
                # Get the best match (first result)
                if len(result) > 0:
                    match = result.iloc[0]  # Get the first row of the DataFrame
                    identity = os.path.basename(match["identity"])
                    # Convert distance to confidence score (0-100)
                    confidence = float((1 - match["distance"]) * 100)
                    matches.append(
                        {
                            "identity": identity,
                            "confidence": confidence,
                            "path": match["identity"],
                        }
                    )
            print(f"FaceRecognitionClass: Found {len(matches)} matches.")
            return matches

        except Exception as e:
            print(f"FaceRecognitionClass: Error in face recognition: {e}")
            return []

    def add_face(self, identity: str) -> bool:
        """
        Add a new face to the reference database.

        Args:
            image_url (str): URL of the image containing the face
            identity (str): Identifier for the face

        Returns:
            bool: True if successful, False otherwise
        """
        print(f"FaceRecognitionClass: Entering add_face function for identity: {identity}.")
        image = self.get_current_image()
        if image is None:
            print("FaceRecognitionClass: No image available to add face.")
            return False

        try:
            # Save the image with the identity as filename
            save_path = os.path.join(self.faces_dir, f"{identity}.jpg")
            Image.fromarray(image).save(save_path)
            print(f"FaceRecognitionClass: Successfully saved face to {save_path}.")
            return True
        except Exception as e:
            print(f"FaceRecognitionClass: Error adding face: {e}")
            return False
