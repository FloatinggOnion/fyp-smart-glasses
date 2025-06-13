# type:ignore
import io
import os
import base64
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
from scene_service import SceneService, strip_markdown
from PIL import Image
from datetime import datetime, timedelta
from dateutil import parser, relativedelta

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

# Pydantic models for request/response
class ImageRequest(BaseModel):
    image_url: str

class ImageQueryRequest(BaseModel):
    query: str
    image: Optional[str] = None  # base64 encoded image

class SceneDescriptionRequest(BaseModel):
    image: str  # base64 encoded image

class OCRRequest(BaseModel):
    image: str  # base64 encoded image

class FaceResponse(BaseModel):
    matches: List[Dict]

class OCRResponse(BaseModel):
    text_lines: List[str]

class QueryRequest(BaseModel):
    query: str

class SaveFaceRequest(BaseModel):
    identity: str
    image: Optional[str] = None  # base64 encoded image

class DailyRecapRequest(BaseModel):
    date: Optional[str] = None

# Helper function to determine if query requires image
def requires_image(query: str) -> bool:
    """Determine if a query requires image processing"""
    image_keywords = [
        'see', 'look', 'what', 'describe', 'read', 'text', 'face', 'person',
        'scene', 'picture', 'image', 'capture', 'screenshot', 'save', 'show',
        'tell me about', 'what is', 'who is', 'identify', 'recognize'
    ]
    
    query_lower = query.lower()
    return any(keyword in query_lower for keyword in image_keywords)

# Helper function to convert base64 to PIL Image
def base64_to_image(base64_string: str) -> Image.Image:
    """Convert base64 string to PIL Image"""
    try:
        print(f"Processing base64 image, length: {len(base64_string)}")
        
        # Remove data URL prefix if present
        if base64_string.startswith('data:image'):
            base64_string = base64_string.split(',')[1]
            print("Removed data URL prefix")
        
        print(f"Base64 string after processing, length: {len(base64_string)}")
        print(f"First 50 chars: {base64_string[:50]}...")
        
        image_data = base64.b64decode(base64_string)
        print(f"Decoded image data size: {len(image_data)} bytes")
        
        image = Image.open(io.BytesIO(image_data))
        print(f"Image opened successfully: {image.size} {image.mode}")
        return image
    except Exception as e:
        print(f"Error in base64_to_image: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid image format: {str(e)}")

# Function definitions for Gemini
functions = [
    {
        "name": "recognize_face",
        "description": "Recognize a face in an image from the stored database and provide a natural response with the person's name. Use this function when someone asks 'who is this?', 'who is in this image?', 'do you recognize this person?', or similar questions about identifying a person in an image. The system will respond with the person's name and confidence level in a conversational way.",
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
        "name": "describe_scene",
        "description": "Describe the current scene in detail. Use this function when someone asks 'what do you see?' or 'describe this scene' or similar questions.",
    },
    {
        "name": "get_daily_recap",
        "description": "Get a comprehensive description of all scenes from a specific date. Use this function when someone asks about their daily activities, such as 'what happened today?', 'recap my day so far', 'what did I do yesterday?', 'give me a recap of two weeks ago', 'what happened on the 6th of June?', 'what did I do last Monday?', etc. The system can parse various date expressions including relative dates (today, yesterday, X days/weeks/months ago) and absolute dates.",
        "parameters": {
            "type": "object",
            "properties": {
                "date": {
                    "type": "string",
                    "description": "Date to get scenes from (optional, format: YYYYMMDD). If not provided, the system will parse the date from the user's query.",
                }
            },
        },
    },
]

# API endpoints
@app.post("/recognize_face", response_model=FaceResponse)
async def recognize_face(request: ImageQueryRequest):
    """Recognize a face in the given image."""
    if not request.image:
        raise HTTPException(status_code=400, detail="Image is required for face recognition")
    
    image = base64_to_image(request.image)
    matches = face_recognition.find_face_from_image(image)
    
    if not matches:
        return FaceResponse(matches=[])
    
    # Create a natural response with the person's name
    best_match = matches[0]  # Get the highest confidence match
    confidence = best_match["confidence"]
    identity = best_match["identity"]
    
    # Create different response styles based on confidence
    if confidence >= 0.9:
        message = f"I can see {identity} in the image. I'm very confident this is them."
    elif confidence >= 0.8:
        message = f"This looks like {identity}. I'm quite confident about this identification."
    elif confidence >= 0.7:
        message = f"I think this might be {identity}, but I'm not completely certain."
    else:
        message = f"This could be {identity}, though I'm not very confident about this match."
    
    # If there are multiple matches, mention them
    if len(matches) > 1:
        other_matches = [m["identity"] for m in matches[1:3]]  # Top 2 other matches
        message += f" I also see some similarity to {', '.join(other_matches)}."
    
    # Add the message to each match for consistency
    for match in matches:
        match["message"] = message
    
    return FaceResponse(matches=matches)

@app.post("/extract_text", response_model=OCRResponse)
async def extract_text(request: OCRRequest):
    """Extract text from the given image."""
    image = base64_to_image(request.image)
    text_lines = ocr_service.extract_text_from_image(image)
    return OCRResponse(text_lines=text_lines)

@app.post("/describe_scene")
async def describe_scene(request: SceneDescriptionRequest):
    """Describe a single scene from the provided image."""
    image = base64_to_image(request.image)
    result = scene_service.describe_scene_from_image(image)
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result

@app.post("/save_face")
async def save_face(request: SaveFaceRequest):
    """Save a new face to the database."""
    if not request.image:
        raise HTTPException(status_code=400, detail="I need an image to save a face. Please provide a photo with your request.")
    
    image = base64_to_image(request.image)
    success = face_recognition.add_face_from_image(request.identity, image)
    if not success:
        raise HTTPException(status_code=400, detail="I couldn't save that face. There might be an issue with the image or the face might not be clearly visible.")
    return {"status": "success", "message": f"Face saved as {request.identity}"}

@app.post("/save_screenshot")
async def save_screenshot(request: ImageQueryRequest):
    """Save a screenshot from the given image."""
    if not request.image:
        raise HTTPException(status_code=400, detail="I need an image to save a screenshot. Please provide a photo with your request.")
    
    image = base64_to_image(request.image)
    result = scene_service.save_screenshot_from_image(image)
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result

@app.post("/daily_recap")
async def get_daily_recap(request: DailyRecapRequest):
    """Get a comprehensive description of all scenes from a specific date."""
    # Use provided date or default to today
    date_param = request.date if request.date else datetime.now().strftime("%Y%m%d")
    result = scene_service.get_daily_recap(date_param)
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result

@app.post("/query")
async def process_query(request: ImageQueryRequest):
    """Process a natural language query and determine which function to call."""
    print("Received request to /query endpoint.")
    
    # Check if query requires image
    if requires_image(request.query):
        if not request.image:
            return {
                "status": "error",
                "message": "I need an image to answer that question. Please provide a photo with your request.",
                "requires_image": True
            }
    
    try:
        tools = types.Tool(function_declarations=functions)
        config = types.GenerateContentConfig(tools=[tools])

        # Use provided image or get from camera
        if request.image:
            current_image = base64_to_image(request.image)
        else:
            current_image = get_latest_frame()
            if current_image is None:
                return {
                    "status": "error",
                    "message": "No image available and no image provided in request"
                }

        image_bytes = io.BytesIO()
        current_image.save(image_bytes, format="PNG")
        image_bytes = image_bytes.getvalue()

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
                matches = face_recognition.find_face_from_image(current_image)
                if not matches:
                    return {
                        "function": "recognize_face",
                        "result": {
                            "status": "not_found",
                            "message": "I don't recognize anyone in the image. This person is not in my database.",
                        },
                    }
                
                # Create a natural response with the person's name
                best_match = matches[0]  # Get the highest confidence match
                confidence = best_match["confidence"]
                identity = best_match["identity"]
                
                # Create different response styles based on confidence
                if confidence >= 0.9:
                    message = f"I can see {identity} in the image. I'm very confident this is them."
                elif confidence >= 0.8:
                    message = f"This looks like {identity}. I'm quite confident about this identification."
                elif confidence >= 0.7:
                    message = f"I think this might be {identity}, but I'm not completely certain."
                else:
                    message = f"This could be {identity}, though I'm not very confident about this match."
                
                # If there are multiple matches, mention them
                if len(matches) > 1:
                    other_matches = [m["identity"] for m in matches[1:3]]  # Top 2 other matches
                    message += f" I also see some similarity to {', '.join(other_matches)}."
                
                return {
                    "function": "recognize_face",
                    "result": {
                        "status": "success",
                        "matches": matches,
                        "message": message,
                    },
                }
            elif function_call.name == "extract_text":
                text_lines = ocr_service.extract_text_from_image(current_image)
                return {
                    "function": "extract_text",
                    "result": {"status": "success", "text": text_lines},
                }
            elif function_call.name == "save_face":
                success = face_recognition.add_face_from_image(function_call.args["identity"], current_image)
                if not success:
                    raise HTTPException(status_code=400, detail="I couldn't save that face. There might be an issue with the image or the face might not be clearly visible.")
                return {
                    "function": "save_face",
                    "result": {
                        "status": "success",
                        "message": f"Face saved as {function_call.args['identity']}",
                    },
                }
            elif function_call.name == "save_screenshot":
                result = scene_service.save_screenshot_from_image(current_image)
                if result["status"] == "error":
                    raise HTTPException(status_code=400, detail=result["message"])
                return {"function": "save_screenshot", "result": result}
            elif function_call.name == "describe_scene":
                result = scene_service.describe_scene_from_image(current_image)
                if result["status"] == "error":
                    raise HTTPException(status_code=400, detail=result["message"])
                return {"function": "describe_scene", "result": result}
            elif function_call.name == "get_daily_recap":
                # Use provided date or parse from query
                date_param = function_call.args.get("date")
                if not date_param:
                    # Parse date from the original query
                    date_param = parse_natural_language_date(request.query)
                    print(f"Parsed date from query '{request.query}': {date_param}")
                
                result = scene_service.get_daily_recap(date_param)
                if result["status"] == "error":
                    raise HTTPException(status_code=400, detail=result["message"])
                return {"function": "get_daily_recap", "result": result}
            else:
                return {"response": response}
        else:
            return {"text": strip_markdown(response.candidates[0].content.parts[0].text)}

    except Exception as e:
        raise e

# Legacy endpoints for backward compatibility
@app.post("/recognize_face_legacy", response_model=FaceResponse)
async def recognize_face_legacy():
    """Legacy endpoint - Recognize a face in the current camera frame."""
    matches = face_recognition.find_face()
    return FaceResponse(matches=matches)

@app.post("/extract_text_legacy", response_model=OCRResponse)
async def extract_text_legacy():
    """Legacy endpoint - Extract text from the current camera frame."""
    text_lines = ocr_service.extract_text()
    return OCRResponse(text_lines=text_lines)

@app.post("/describe_scene_legacy")
async def describe_scene_legacy():
    """Legacy endpoint - Describe the current camera scene."""
    result = scene_service.describe_scene()
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result

def parse_natural_language_date(query: str) -> str:
    """
    Parse natural language date expressions and return YYYYMMDD format.
    
    Examples:
    - "Recap my day so far" -> today
    - "Give me a recap of what my day was like yesterday" -> yesterday
    - "I need to know what I did two weeks ago" -> two weeks ago
    - "What happened on the 6th of June?" -> June 6th of current year
    - "What happened last Monday?" -> last Monday
    """
    query_lower = query.lower().strip()
    
    # Handle relative dates
    if any(phrase in query_lower for phrase in ["today", "my day so far", "this day", "current day"]):
        return datetime.now().strftime("%Y%m%d")
    
    if any(phrase in query_lower for phrase in ["yesterday", "yesterdays"]):
        yesterday = datetime.now() - timedelta(days=1)
        return yesterday.strftime("%Y%m%d")
    
    if any(phrase in query_lower for phrase in ["tomorrow", "tomorrows"]):
        tomorrow = datetime.now() + timedelta(days=1)
        return tomorrow.strftime("%Y%m%d")
    
    # Handle "X days ago"
    import re
    days_ago_match = re.search(r'(\d+)\s+days?\s+ago', query_lower)
    if days_ago_match:
        days = int(days_ago_match.group(1))
        target_date = datetime.now() - timedelta(days=days)
        return target_date.strftime("%Y%m%d")
    
    # Handle "X weeks ago"
    weeks_ago_match = re.search(r'(\d+)\s+weeks?\s+ago', query_lower)
    if weeks_ago_match:
        weeks = int(weeks_ago_match.group(1))
        target_date = datetime.now() - timedelta(weeks=weeks)
        return target_date.strftime("%Y%m%d")
    
    # Handle "X months ago"
    months_ago_match = re.search(r'(\d+)\s+months?\s+ago', query_lower)
    if months_ago_match:
        months = int(months_ago_match.group(1))
        target_date = datetime.now() - relativedelta.relativedelta(months=months)
        return target_date.strftime("%Y%m%d")
    
    # Handle "X years ago"
    years_ago_match = re.search(r'(\d+)\s+years?\s+ago', query_lower)
    if years_ago_match:
        years = int(years_ago_match.group(1))
        target_date = datetime.now() - relativedelta.relativedelta(years=years)
        return target_date.strftime("%Y%m%d")
    
    # Handle "last week", "last month", etc.
    if "last week" in query_lower:
        target_date = datetime.now() - timedelta(weeks=1)
        return target_date.strftime("%Y%m%d")
    
    if "last month" in query_lower:
        target_date = datetime.now() - relativedelta.relativedelta(months=1)
        return target_date.strftime("%Y%m%d")
    
    if "last year" in query_lower:
        target_date = datetime.now() - relativedelta.relativedelta(years=1)
        return target_date.strftime("%Y%m%d")
    
    # Handle specific weekdays
    weekdays = {
        "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
        "friday": 4, "saturday": 5, "sunday": 6
    }
    
    for day_name, day_num in weekdays.items():
        if f"last {day_name}" in query_lower:
            today = datetime.now()
            days_since = (today.weekday() - day_num) % 7
            if days_since == 0:
                days_since = 7  # Last week's same day
            target_date = today - timedelta(days=days_since)
            return target_date.strftime("%Y%m%d")
    
    # Handle absolute dates like "6th of June", "June 6th"
    try:
        # Try to parse with dateutil
        parsed_date = parser.parse(query, fuzzy=True)
        return parsed_date.strftime("%Y%m%d")
    except:
        pass
    
    # If all else fails, return today's date
    print(f"Could not parse date from query: '{query}', defaulting to today")
    return datetime.now().strftime("%Y%m%d")

# App is imported by run.py
