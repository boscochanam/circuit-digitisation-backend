from ultralytics import YOLO
import numpy as np

# Prev Implementation of extract_pred

# def extract_pred(image):
#     model_path = "../models/120epoch.pt"
#     model = YOLO(model_path)

#     results = model(image)
#     r = np.array(results[0].boxes.xyxyn)
#     names = model.names
#     classes = []

#     for result in results:
#         for c in result.boxes.cls:
#             classes.append(names[int(c)])

#     print("r: ", r)
#     print("classes: ", classes)
#     return r, classes

# (yolo format to normal bbox format)
# def yolobbox2bbox(x,y,w,h):
#     x1, y1 = x-w/2, y-h/2
#     x2, y2 = x+w/2, y+h/2
#     return x1, y1, x2, y2

# Extracts the predictions from the image (coordinates and classes) 
def extract_pred(image):
    model_path = "../models/component_nov.pt"
    model = YOLO(model_path)

    results = model(image)
    boxes = results[0].boxes.xyxyn
    
    # Box for masking(white)
    component_boxes = results[0].boxes.xyxy.cpu().numpy()

    classes = []
    coords = []

    # coordinates
    for box in boxes:
        coordinate = tuple(box.flatten().tolist())
        coords.append(coordinate)
        
    # classes
    names = model.names
    for result in results:
        for c in result.boxes.cls:
            classes.append(names[int(c)])
    
    # print("coords: ", coords)
    return coords, classes, component_boxes
    # print("r: ", r)
    # print("classes: ", classes)

if __name__ == "__main__":
    data = extract_pred(r"C:\Users\HP\Desktop\wire_images\AC-Voltage-Detector-Circuit.png")