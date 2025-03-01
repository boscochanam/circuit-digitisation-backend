from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import io
import uuid
import cv2 as cv
import uvicorn
import base64
import numpy as np
from ultralytics import YOLO
from loguru import logger
import sys

# Configure loguru
logger.remove()  # Remove default handler
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO"
)
logger.add(
    "logs/api_{time}.log",
    rotation="500 MB",
    level="DEBUG",
    compression="zip"
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

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"Hello": "Chris"}

@app.post("/analyze-circuit")
async def analyze_circuit(file: UploadFile = File(...)) -> JSONResponse:
    try:
        # open the image
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        # Flip the image upside down immediately
        image = image.transpose(Image.FLIP_TOP_BOTTOM)
        width, height = image.size
        
        # component model
        data_device, classes, component_boxes = extract_pred(image)
        # component_boxes = component_results.boxes.xyxy.cpu().numpy()

        # getting the filtered data for matching
        filtered_data_device = [data_device[i] for i in range(len(classes)) if classes[i] not in ('0', '10')]  

        # component json (for getting device uuid to join in next steps)
        devices_json, devices_uuid, num_nodes = deviceJSON(data_device, classes)

        # mapped coords to id device id
        data_device_dict = {}
        i = 0
        for k, v in devices_uuid.items():
            data_device_dict[k] = data_device[i]
            i += 1
        # print(len(data_device_dict))
        # print(len(classes))
        
        
        # data_device_dict = {devices_uuid[i]: data_device[i] for i in range(len(data_device))}
        # print(type(data_device))

        # for (k, v), coord in zip(devices_uuid.items(), data_device):
        #     print(f"{k}: {v}")
        #     print("coords", coord, '\n\n')
        # Create masked image
        masked_image = create_white_mask(image, component_boxes)

        # wire model - using masked image
        data_wire = extract_pred_wire(masked_image)

        # print("data dict", data_device_dict)
        # print("data wire", data_wire)
        # print("classes", classes)

        # inception
        devices, wires = inception(data_device_dict, data_wire, (width, height), classes)
        freenodes = []
        component_json = componentJSON(devices, freenodes)
        wires_json = wiresJSON(wires)

        # Distance calculation(to join components/wires)

        # wire_uuid = [(str(uuid.uuid4()), str(uuid.uuid4())) for _ in range(len(data_wire))] # all wires having initial uuids
        # match wire and device points
        # wire_uuid_v2 = match_wire_device_points(filtered_data_device, data_wire, devices_uuid, num_nodes, wire_uuid, (width, height))
        
        
        # data_device(x1_c, y1_c, x2_c, y2_c) normalized xyxyn, data_wire(angle, x1, y1, x2, y2) 
        # refer this for format
        

        # stored_data = {
        #     "data_device": data_device_dict,
        #     "data_wire": data_wire,
        #     "device_uuids": devices_uuid,
        #     "num_nodes": num_nodes,
        #     "image_size": (width, height),
        #     "classes": classes
        # }

        # # Save the data to a JSON file (for later use in another file)
        # with open('stored_data_2.json', 'w') as f:
        #     json.dump(stored_data, f, indent=4)

        json_data = {
            "wires": wires_json,
            "devices": component_json,
            "freeNodes": []
        }
        # final json
        # j = toJSON(data_device, classes, data_wire)
        
        return JSONResponse(content=json_data)
    except Exception as e:
        return JSONResponse(content={"result": "error", "message": str(e)})


# test pipeline
@app.post("/detect/")
async def detect_image(file: UploadFile = File(...)):

    component_model = YOLO('models/component_nov.pt') # comp_nojunc_ashay
    final_model = YOLO('models/best_wire_new.pt') # same as models/lines.pt

    # Read image from the uploaded file
    image_data = await file.read()
    image = Image.open(io.BytesIO(image_data))
    width, height = image.size
    # First detection with component model
    component_results = component_model(image)[0]
    component_boxes = component_results.boxes.xyxy.cpu().numpy()
    
    # Create masked image with white rectangles
    masked_image = create_white_mask(image, component_boxes)
    
    # Run masked image through final model
    final_results = final_model(masked_image)[0]
    
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
    try:
        logger.info(f"Processing new image upload: {file.filename}")
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        # Flip the image upside down immediately
        image = image.transpose(Image.FLIP_TOP_BOTTOM)
        
        # Initialize models
        logger.debug("Loading YOLO models")
        component_model = YOLO('models/component_nov.pt')
        wire_model = YOLO('models/best_wire_new.pt')
        
        # Component detection
        logger.debug("Running component detection")
        component_results = component_model(image)[0]
        component_boxes = component_results.boxes.xyxy.cpu().numpy()
        component_image = component_results.plot()
        
        # Create masked image
        logger.debug("Creating masked image")
        masked_image = create_white_mask(image, component_boxes)
        # Convert masked image correctly
        if isinstance(masked_image, Image.Image):
            masked_np = np.array(masked_image)
        else:
            masked_np = masked_image
        
        # Wire detection
        logger.debug("Running wire detection")
        wire_results = wire_model(Image.fromarray(masked_np))[0]
        wire_image = wire_results.plot()
        
        def image_to_base64(img_array):
            logger.debug(f"Converting image to base64. Type: {type(img_array)}")
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
                logger.error(f"Error in image conversion: {str(e)}")
                raise

        logger.info("Preparing response")
        return JSONResponse(content={
            "components": image_to_base64(component_image),
            "masked": image_to_base64(masked_np),
            "lines": image_to_base64(wire_image)
        })
        
    except Exception as e:
        logger.exception(f"Detection failed: {str(e)}")
        return JSONResponse(
            content={"error": f"Detection failed: {str(e)}"},
            status_code=500
        )

if __name__ == "__main__":

    uvicorn.run(app, host="127.0.0.1", port=8000)