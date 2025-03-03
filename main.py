from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image, ExifTags
import io
import uuid
import cv2 as cv
import uvicorn
import base64
import numpy as np
import traceback
import time
import os
from ultralytics import YOLO
from loguru import logger
import sys
from typing import Callable
import json

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

# Configure detailed loguru logging
logger.remove()  # Remove default handler

# Console logging with colors and detailed context
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="DEBUG"  # Set to DEBUG for more detailed logs
)

# File logging with rotation and compression
logger.add(
    "logs/api_{time:YYYY-MM-DD}.log",
    rotation="12:00",  # New file at midnight
    retention="30 days",
    compression="zip",
    level="DEBUG",
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | {message}",
    backtrace=True,  # Include detailed exception info
    diagnose=True    # Include variable values in exceptions
)

# Separate file for errors only
logger.add(
    "logs/errors_{time:YYYY-MM-DD}.log",
    level="ERROR",
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | {message}",
    backtrace=True,
    diagnose=True
)

# imports model pred and json output 
from vision.json.getjson import deviceJSON, toJSON, wireJSON
from vision.json.new_json import componentJSON, wiresJSON

from vision.processing import extract_pred
# wire imports
from vision.wire.processing import extract_pred_wire
# tools imports
from vision.tools.operations import create_white_mask
from vision.tools.algo.match_algo_v4 import match_wire_device_points


# inception imports
from vision.inception.main import inceptionFunction as inception

app = FastAPI(title="Circuit Digitisation API", version="1.0.0")

# Request/Response logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next: Callable):
    req_id = str(uuid.uuid4())
    logger.info(f"[{req_id}] Request: {request.method} {request.url}")
    
    # Try to log request body for non-multipart requests
    if not request.headers.get("content-type", "").startswith("multipart/form-data"):
        try:
            body = await request.body()
            if body:
                logger.debug(f"[{req_id}] Request body: {body.decode()}")
        except Exception as e:
            logger.debug(f"[{req_id}] Failed to log request body: {str(e)}")
    else:
        logger.debug(f"[{req_id}] Multipart form data request - body not logged")
    
    start_time = time.time()
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        
        logger.info(f"[{req_id}] Response: {response.status_code} | Time: {process_time:.4f}s")
        return response
    except Exception as exc:
        logger.error(f"[{req_id}] Unhandled exception: {str(exc)}\n{traceback.format_exc()}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal Server Error", "traceback": traceback.format_exc()}
        )

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def init_models():
    """Initialize all models once at startup"""
    logger.info("Initializing models...")
    try:
        component_model_path = r"models\Components\90mapROBOFLOW.pt"
        wire_model_path = 'models/best_wire_new.pt'
        
        logger.info(f"Loading component model from: {component_model_path}")
        component_model = YOLO(component_model_path)
        logger.info(f"Component model loaded successfully. Model type: {type(component_model)}")
        
        logger.info(f"Loading wire model from: {wire_model_path}")
        wire_model = YOLO(wire_model_path)
        logger.info(f"Wire model loaded successfully. Model type: {type(wire_model)}")
        
        return {
            'component_model': component_model,
            'wire_model': wire_model
        }
    except Exception as e:
        logger.error(f"Failed to load models: {str(e)}\n{traceback.format_exc()}")
        raise

@app.on_event("startup")
async def startup_event():
    """Initialize models on startup"""
    logger.info("Application starting up...")
    try:
        app.state.models = init_models()
        logger.info("Models initialized and stored in app state")
        logger.debug(f"Available models: {list(app.state.models.keys())}")
    except Exception as e:
        logger.critical(f"Startup failed: {str(e)}")
        raise

# Detailed image preprocessing function for reuse
def preprocess_image(image, req_id):
    """Common image preprocessing steps with detailed logging"""
    logger.debug(f"[{req_id}] Original image format: {image.format}, mode: {image.mode}, size: {image.size}")
    
    # Auto-orient image
    if hasattr(image, '_getexif'):
        try:
            logger.debug(f"[{req_id}] Checking EXIF for orientation")
            for orientation in ExifTags.TAGS.keys():
                if ExifTags.TAGS[orientation] == 'Orientation':
                    break
            exif = dict(image._getexif() or {}).get(orientation)
            if exif:
                logger.debug(f"[{req_id}] Found orientation: {exif}")
                if exif == 3:
                    logger.debug(f"[{req_id}] Rotating image 180°")
                    image = image.rotate(180, expand=True)
                elif exif == 6:
                    logger.debug(f"[{req_id}] Rotating image 270°")
                    image = image.rotate(270, expand=True)
                elif exif == 8:
                    logger.debug(f"[{req_id}] Rotating image 90°")
                    image = image.rotate(90, expand=True)
        except Exception as e:
            logger.warning(f"[{req_id}] Error processing EXIF: {str(e)}")
    
    # Resize
    logger.debug(f"[{req_id}] Resizing image to 640x640")
    image = image.resize((640, 640), Image.Resampling.LANCZOS)
    
    # Flip
    logger.debug(f"[{req_id}] Flipping image (TOP_BOTTOM)")
    image = image.transpose(Image.FLIP_TOP_BOTTOM)
    
    logger.debug(f"[{req_id}] Final image size: {image.size}, mode: {image.mode}")
    return image

@app.get("/")
def read_root():
    return {"Hello": "Chris"}

@app.post("/analyze-circuit")
async def analyze_circuit(file: UploadFile = File(...)) -> JSONResponse:
    req_id = str(uuid.uuid4())
    logger.info(f"[{req_id}] Starting circuit analysis for file: {file.filename}")
    
    try:
        # Image preprocessing steps remain the same
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        image = preprocess_image(image, req_id)
        width, height = image.size
        
        # Component detection
        logger.info(f"[{req_id}] Running component detection")
        model = app.state.models['component_model']
        data_device, classes, component_boxes = extract_pred(image, model)
        
        # Generate device UUIDs and JSON
        devices_json, devices_uuid, num_nodes = deviceJSON(data_device, classes)
        logger.debug(f"[{req_id}] Generated device UUIDs and JSON for {len(devices_json)} devices")
        
        # Map device coordinates to UUIDs
        data_device_dict = {k: data_device[i] for i, (k, _) in enumerate(devices_uuid.items())}
        
        # Wire detection
        masked_image = create_white_mask(image, component_boxes)
        data_wire = extract_pred_wire(masked_image, app.state.models['wire_model'])
        logger.debug(f"[{req_id}] Detected {len(data_wire)} wires")
        
        # Generate wire UUIDs
        wire_uuids = [(str(uuid.uuid4()), str(uuid.uuid4())) for _ in range(len(data_wire))]
        
        # Process final connections
        devices, wires = inception(data_device_dict, data_wire, (width, height), classes)
        logger.debug(f"[{req_id}] Inception completed: {len(devices)} devices, {len(wires)} wires")
        
        # Generate final JSON
        component_json = componentJSON(devices, [])  # Empty list for freenodes
        wires_json = wiresJSON(wires)  # This should create the wire connections
        
        json_data = {
            "wires": wires_json,
            "devices": component_json
        }
        
        logger.info(f"[{req_id}] Prepared JSON response with {len(component_json)} devices and {len(wires_json)} wires")
        logger.debug(f"[{req_id}] JSON structure: {json.dumps(json_data)[:500]}...")
        
        return JSONResponse(content=json_data)
        
    except Exception as e:
        logger.exception(f"[{req_id}] Circuit analysis failed")
        return JSONResponse(
            status_code=500,
            content={"result": "error", "message": str(e)}
        )

# test pipeline
@app.post("/detect/")
async def detect_image(file: UploadFile = File(...)):

    print(f"Using: {file.filename}")
    
    # Read image from the uploaded file
    image_data = await file.read()
    image = Image.open(io.BytesIO(image_data))
    width, height = image.size
    
    # Use the shared component model instance
    component_results = app.state.models['component_model'](image)[0]
    component_boxes = component_results.boxes.xyxy.cpu().numpy()
    
    # Create masked image with white rectangles
    masked_image = create_white_mask(image, component_boxes)
    
    # Run masked image through final model
    final_results = app.state.models['wire_model'](masked_image)[0]
    
    # Get annotated images
    component_annotated = Image.fromarray(np.uint8(component_results.plot()))
    final_annotated = Image.fromarray(np.uint8(final_results.plot()))
    
    # Create a new image combining both results side by side
    total_width = component_annotated.width + final_annotated.width
    max_height = max(component_annotated.height, final_annotated.height)
    combined_image = Image.new('RGB', (total_width, max_height))
    
    # Paste both images
    combined_image.paste(component_annotated, (0, 0))
    combined_image.paste(final_annotated, (component_annotated.width, 0))
    
    # Convert to bytes
    img_byte_arr = io.BytesIO()
    combined_image.save(img_byte_arr, format='JPEG')
    img_byte_arr.seek(0)
    
    return StreamingResponse(img_byte_arr, media_type="image/jpeg")

@app.post("/detect")
async def detect_steps(file: UploadFile = File(...)):
    req_id = str(uuid.uuid4())
    logger.info(f"[{req_id}] Processing detection steps for file: {file.filename}")
    
    try:
        # Read image
        start_time = time.time()
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        logger.debug(f"[{req_id}] Image opened successfully, format: {image.format}, size: {image.size}")
        
        # Preprocess image
        image = preprocess_image(image, req_id)
        
        # Component detection
        logger.info(f"[{req_id}] Running component detection")
        if 'component_model' not in app.state.models:
            available_models = list(app.state.models.keys()) if hasattr(app.state, 'models') else "None"
            logger.error(f"[{req_id}] Component model not found. Available: {available_models}")
            return JSONResponse(
                content={"error": f"Component model not found. Available: {available_models}"},
                status_code=500
            )
            
        component_start = time.time()
        component_results = app.state.models['component_model'](image)[0]
        component_time = time.time() - component_start
        
        logger.info(f"[{req_id}] Component detection completed in {component_time:.4f}s")
        
        component_boxes = component_results.boxes.xyxy.cpu().numpy()
        component_image = component_results.plot()
        logger.debug(f"[{req_id}] Found {len(component_boxes)} components")
        
        # Create masked image
        logger.info(f"[{req_id}] Creating masked image")
        masked_start = time.time()
        masked_image = create_white_mask(image, component_boxes)
        masked_time = time.time() - masked_start
        
        logger.info(f"[{req_id}] Masked image created in {masked_time:.4f}s")
        
        # Convert masked image correctly
        if isinstance(masked_image, Image.Image):
            masked_np = np.array(masked_image)
            logger.debug(f"[{req_id}] Converted PIL Image to numpy array, shape: {masked_np.shape}")
        else:
            masked_np = masked_image
            logger.debug(f"[{req_id}] Using existing numpy array, shape: {masked_np.shape if hasattr(masked_np, 'shape') else 'unknown'}")
        
        # Wire detection
        logger.info(f"[{req_id}] Running wire detection")
        if 'wire_model' not in app.state.models:
            logger.error(f"[{req_id}] Wire model not found")
            return JSONResponse(
                content={"error": "Wire model not found"},
                status_code=500
            )
            
        wire_start = time.time()
        wire_results = app.state.models['wire_model'](Image.fromarray(masked_np))[0]
        wire_time = time.time() - wire_start
        
        logger.info(f"[{req_id}] Wire detection completed in {wire_time:.4f}s")
        wire_image = wire_results.plot()
        
        # Convert images to base64
        logger.info(f"[{req_id}] Converting images to base64")
        
        def image_to_base64(img_array):
            logger.debug(f"[{req_id}] Converting image to base64. Type: {type(img_array)}")
            try:
                # Handle different input types
                if isinstance(img_array, Image.Image):
                    img = img_array
                else:
                    img = Image.fromarray(np.uint8(img_array))
                
                # Flip the image vertically before converting to base64
                img = img.transpose(Image.FLIP_TOP_BOTTOM)
                
                buffered = io.BytesIO()
                img.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue()).decode()
                return f"data:image/png;base64,{img_str}"
            except Exception as e:
                logger.error(f"[{req_id}] Error in image conversion: {str(e)}")
                raise
        
        b64_start = time.time()
        components_b64 = image_to_base64(component_image)
        masked_b64 = image_to_base64(masked_np)
        lines_b64 = image_to_base64(wire_image)
        b64_time = time.time() - b64_start
        
        logger.info(f"[{req_id}] Base64 conversion completed in {b64_time:.4f}s")
        
        # Calculate total processing time
        total_time = time.time() - start_time
        logger.info(f"[{req_id}] Total processing time: {total_time:.4f}s")
        
        # Prepare response
        response = {
            "components": components_b64,
            "masked": masked_b64,
            "lines": lines_b64,
            "processingTime": {
                "component": f"{component_time:.4f}s",
                "masking": f"{masked_time:.4f}s",
                "wire": f"{wire_time:.4f}s",
                "total": f"{total_time:.4f}s"
            }
        }
        
        logger.info(f"[{req_id}] Response prepared successfully")
        return JSONResponse(content=response)
        
    except Exception as e:
        logger.exception(f"[{req_id}] Detection failed: {str(e)}")
        return JSONResponse(
            content={
                "error": f"Detection failed: {str(e)}",
                "traceback": traceback.format_exc()
            },
            status_code=500
        )

if __name__ == "__main__":
    logger.info("Starting application server")
    try:
        uvicorn.run(app, host="127.0.0.1", port=8000)
    except Exception as e:
        logger.critical(f"Failed to start server: {str(e)}")