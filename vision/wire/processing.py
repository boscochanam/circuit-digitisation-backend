from ultralytics import YOLO

# wire calc import
from vision.wire.wire_calc import calculate_angle

def extract_pred_wire(image, model):
    """Modified to accept model as parameter instead of loading it"""
    w, h = image.size

    coords = []
    results = model(image)
    obb_boxes = results[0].obb.xyxyxyxyn
    conf = results[0].obb.conf

    for obb_box, confidence in zip(obb_boxes, conf):
        coordinate = obb_box.flatten().tolist()
        pixel_coords = [
            coordinate[i] * w if i % 2 == 0 else coordinate[i] * h 
            for i in range(8)
        ]
        angle, x1, y1, x2, y2 = calculate_angle(pixel_coords)
        coords.append((angle, x1/w, y1/h, x2/w, y2/h))

    return coords

# if __name__ == "__main__":
#     data = extract_pred_wire(r'C:\Users\chana\Documents\Coding\Backend\vision\test.jpg')