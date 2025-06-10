# type:ignore
import io
import os
from typing import List, Dict, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from google.genai import types
from camera_service import get_latest_frame
from face_detection import FaceRecognitionClass
from ocr_service import OCRService
import threading
from google import genai
from scene_service import SceneService

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="Smart Glasses API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
try:
    face_recognition = FaceRecognitionClass()
except Exception as e:
    print(f"Warning: Face recognition service failed to initialize: {e}")
    face_recognition = None

try:
    ocr_service = OCRService()
except Exception as e:
    print(f"Warning: OCR service failed to initialize: {e}")
    ocr_service = None

try:
    scene_service = SceneService()
except Exception as e:
    print(f"Warning: Scene service failed to initialize: {e}")
    scene_service = None

try:
    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
except Exception as e:
    print(f"Warning: Gemini client failed to initialize: {e}")
    client = None

# Configure Gemini

# genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
# model = genai.GenerativeModel("models/gemini-2.0-flash")


# Pydantic models for request/response
class ImageRequest(BaseModel):
    image_url: str


class FaceResponse(BaseModel):
    matches: List[Dict]


class OCRResponse(BaseModel):
    text_lines: List[str]


class QueryRequest(BaseModel):
    query: str


class SaveFaceRequest(BaseModel):
    identity: str


class SceneDescriptionRequest(BaseModel):
    image_url: str


class DailyRecapRequest(BaseModel):
    date: Optional[str] = None


# Function definitions for Gemini
functions = [
    {
        "name": "recognize_face",
        "description": "Recognize a face in an image from the stored database. Use this function when someone asks 'who is this?' or 'who is in this image?' or similar questions about identifying a person in an image.",
    },
    {
        "name": "extract_text",
        "description": "Extract text from an image using OCR. Use this function when someone asks to read text from an image or identify text in an image.",
    },
    {
        "name": "save_face",
        "description": "Save a new face to the database with a given identity. Use this function when someone wants to add a new person to the face recognition system.",
        "parameters": {
            "type": "object",
            "properties": {
                "identity": {
                    "type": "string",
                    "description": "Name or identifier for the face",
                },
            },
            "required": ["identity"],
        },
    },
    {
        "name": "save_screenshot",
        "description": "Save a screenshot/scene from the current view. Use this function when someone wants to capture the current scene or take a screenshot.",
    },
    {
        "name": "get_daily_recap",
        "description": "Get a comprehensive description of all scenes from a specific date. Use this function when someone asks 'what happened today?' or 'what happened yesterday?' or similar questions about daily activities.",
        "parameters": {
            "type": "object",
            "properties": {
                "date": {
                    "type": "string",
                    "description": "Date to get scenes from (optional, format: YYYYMMDD)",
                }
            },
        },
    },
]


# API endpoints
@app.post("/recognize_face", response_model=FaceResponse)
async def recognize_face():
    """Recognize a face in the given image."""
    matches = face_recognition.find_face()
    return FaceResponse(matches=matches)


@app.post("/extract_text", response_model=OCRResponse)
async def extract_text():
    """Extract text from the given image."""
    text_lines = ocr_service.extract_text()
    return OCRResponse(text_lines=text_lines)


@app.post("/save_face")
async def save_face(request: SaveFaceRequest):
    """Save a new face to the database."""
    success = face_recognition.add_face(request.identity)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to save face")
    return {"status": "success", "message": f"Face saved as {request.identity}"}


@app.post("/save_screenshot")
async def save_screenshot():
    """Save a screenshot from the given image."""
    result = scene_service.save_screenshot()
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result


@app.post("/describe_scene")
async def describe_scene():
    """Describe a single scene from the provided image."""
    result = scene_service.describe_scene()
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result


@app.post("/daily_recap")
async def get_daily_recap(request: DailyRecapRequest):
    """Get a comprehensive description of all scenes from a specific date."""
    result = scene_service.get_daily_recap(request.date)
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result


@app.post("/query")
async def process_query(request: QueryRequest):
    """Process a natural language query and determine which function to call."""
    print("Received request to /query endpoint.")
    try:
        tools = types.Tool(function_declarations=functions)
        config = types.GenerateContentConfig(tools=[tools])

        current_image = get_latest_frame()

        image_bytes = io.BytesIO()
        current_image.save(image_bytes, format="PNG")
        image_bytes = image_bytes.getvalue()  # Get the bytes data
        # Generate function calling response from Gemini
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[
                types.Part.from_bytes(data=image_bytes, mime_type="image/png"),
                request.query,
            ],
            config=config,
        )

        # Extract function call details
        function_call = response.candidates[0].content.parts[0].function_call
        if function_call:
            if function_call.name == "recognize_face":
                matches = face_recognition.find_face()
                if not matches:
                    return {
                        "function": "recognize_face",
                        "result": {
                            "status": "not_found",
                            "message": "No matching faces found in the database",
                        },
                    }
                return {
                    "function": "recognize_face",
                    "result": {
                        "status": "success",
                        "matches": matches,
                        "message": f"Found {len(matches)} potential matches",
                    },
                }
            elif function_call.name == "extract_text":
                text_lines = ocr_service.extract_text()
                return {
                    "function": "extract_text",
                    "result": {"status": "success", "text": text_lines},
                }
            elif function_call.name == "save_face":
                success = face_recognition.add_face(function_call.args["identity"])
                if not success:
                    raise HTTPException(status_code=400, detail="Failed to save face")
                return {
                    "function": "save_face",
                    "result": {
                        "status": "success",
                        "message": f"Face saved as {function_call.args['identity']}",
                    },
                }
            elif function_call.name == "save_screenshot":
                result = scene_service.save_screenshot()
                if result["status"] == "error":
                    raise HTTPException(status_code=400, detail=result["message"])
                return {"function": "save_screenshot", "result": result}
            elif function_call.name == "describe_scene":
                result = scene_service.describe_scene()
                if result["status"] == "error":
                    raise HTTPException(status_code=400, detail=result["message"])
                return {"function": "describe_scene", "result": result}
            elif function_call.name == "get_daily_recap":
                result = scene_service.get_daily_recap(function_call.args.get("date"))
                if result["status"] == "error":
                    raise HTTPException(status_code=400, detail=result["message"])
                return {"result": result}

            else:
                return {"response": response}
        else:
            return {"text": response.candidates[0].content.parts[0].text}
            raise HTTPException(status_code=400, detail="Unsupported function")

    except Exception as e:
        raise e


# App is imported by run.py
