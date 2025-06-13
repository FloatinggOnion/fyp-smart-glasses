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

    def find_face_from_image(self, image: Image.Image) -> List[Dict]:
        """
        Find matching faces from the reference database given a PIL Image.

        Args:
            image (Image.Image): PIL Image to analyze

        Returns:
            List[Dict]: List of matches with confidence scores and identities
        """
        print("FaceRecognitionClass: Entering find_face_from_image function.")
        try:
            # Convert PIL Image to numpy array
            image_array = np.array(image)
            
            # Get reference faces
            reference_faces = self._get_reference_faces()
            if not reference_faces:
                print("FaceRecognitionClass: No reference faces found.")
                return []

            matches = []
            for identity, face_path in reference_faces.items():
                try:
                    result = DeepFace.verify(
                        img1_path=face_path,
                        img2_path=image_array,
                        model_name="VGG-Face",
                        distance_metric="cosine",
                        enforce_detection=False,
                    )
                    
                    if result["verified"]:
                        confidence = 1 - result["distance"]
                        matches.append({
                            "identity": identity,
                            "confidence": confidence,
                            "distance": result["distance"]
                        })
                        print(f"FaceRecognitionClass: Match found for {identity} with confidence {confidence:.3f}")
                except Exception as e:
                    print(f"FaceRecognitionClass: Error comparing with {identity}: {e}")
                    continue

            # Sort by confidence (highest first)
            matches.sort(key=lambda x: x["confidence"], reverse=True)
            print(f"FaceRecognitionClass: Found {len(matches)} matches.")
            return matches

        except Exception as e:
            print(f"FaceRecognitionClass: Error in find_face_from_image: {e}")
            return []

    def add_face_from_image(self, identity: str, image: Image.Image) -> bool:
        """
        Add a new face to the database from a PIL Image.

        Args:
            identity (str): Name or identifier for the face
            image (Image.Image): PIL Image containing the face

        Returns:
            bool: True if successful, False otherwise
        """
        print(f"FaceRecognitionClass: Entering add_face_from_image for {identity}.")
        try:
            # Create filename for the face
            filename = f"{identity.lower().replace(' ', '_')}.jpg"
            filepath = os.path.join(self.faces_dir, filename)
            
            # Save the image
            image.save(filepath, format="JPEG", quality=95)
            print(f"FaceRecognitionClass: Face saved to {filepath}.")
            return True

        except Exception as e:
            print(f"FaceRecognitionClass: Error adding face: {e}")
            return False

    def find_face(self) -> List[Dict]:
        """
        Find matching faces from the reference database given an image URL.
        Legacy method that gets image from camera.

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
            # Get reference faces
            reference_faces = self._get_reference_faces()
            if not reference_faces:
                print("FaceRecognitionClass: No reference faces found.")
                return []

            matches = []
            for identity, face_path in reference_faces.items():
                try:
                    result = DeepFace.verify(
                        img1_path=face_path,
                        img2_path=image,
                        model_name="VGG-Face",
                        distance_metric="cosine",
                        enforce_detection=False,
                    )
                    
                    if result["verified"]:
                        confidence = 1 - result["distance"]
                        matches.append({
                            "identity": identity,
                            "confidence": confidence,
                            "distance": result["distance"]
                        })
                        print(f"FaceRecognitionClass: Match found for {identity} with confidence {confidence:.3f}")
                except Exception as e:
                    print(f"FaceRecognitionClass: Error comparing with {identity}: {e}")
                    continue

            # Sort by confidence (highest first)
            matches.sort(key=lambda x: x["confidence"], reverse=True)
            print(f"FaceRecognitionClass: Found {len(matches)} matches.")
            return matches

        except Exception as e:
            print(f"FaceRecognitionClass: Error in find_face: {e}")
            return []

    def add_face(self, identity: str) -> bool:
        """
        Add a new face to the database.
        Legacy method that gets image from camera.

        Args:
            identity (str): Name or identifier for the face

        Returns:
            bool: True if successful, False otherwise
        """
        print(f"FaceRecognitionClass: Entering add_face for {identity}.")
        try:
            # Get current image
            image = self.get_current_image()
            if image is None:
                print("FaceRecognitionClass: No image available for adding face.")
                return False

            # Create filename for the face
            filename = f"{identity.lower().replace(' ', '_')}.jpg"
            filepath = os.path.join(self.faces_dir, filename)
            
            # Convert numpy array to PIL Image and save
            pil_image = Image.fromarray(image)
            pil_image.save(filepath, format="JPEG", quality=95)
            print(f"FaceRecognitionClass: Face saved to {filepath}.")
            return True

        except Exception as e:
            print(f"FaceRecognitionClass: Error adding face: {e}")
            return False

    def _get_reference_faces(self) -> Dict[str, str]:
        """
        Get all reference faces from the faces directory.

        Returns:
            Dict[str, str]: Dictionary mapping identity to file path
        """
        reference_faces = {}
        if not os.path.exists(self.faces_dir):
            return reference_faces

        for filename in os.listdir(self.faces_dir):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                identity = filename.split('.')[0].replace('_', ' ').title()
                filepath = os.path.join(self.faces_dir, filename)
                reference_faces[identity] = filepath

        return reference_faces
