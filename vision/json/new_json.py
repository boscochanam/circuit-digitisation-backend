import json
import random
import numpy as np
import uuid
from typing import List, Dict, Tuple


# from vision.proces
from vision.processing import extract_pred
# from vision.processing import extract_pred
from vision.class_map import get_class_mapping
from vision.inception.classes import Component, Wire, FreeNode

def toJSON(data, classes, data_wire = None):

    # components json
    devices_json = []
    for i, d in enumerate(data):
        
        # print("d", d)
        # print(type(d))
        x1, y1, x2, y2 = map(float, d)
        # print("type x1", type(x1))
        # print(x1, y1, x2, y2)

        # print("Checking: ", classes[i], get_class_mapping(int(classes[i])))
        # if get_class_mapping(int(classes[i])) not in ['diode', 'powersource', 'resistor', 'inductor', 'capacitor', 'switch']:
        #     continue

        # get class name from label (0 - 10)
        className = get_class_mapping(int(classes[i]))

        deviceId = str(uuid.uuid4())
        node1 = str(uuid.uuid4())
        node2 = str(uuid.uuid4())
        print(f"Device: {className} with class: {classes[i]} {deviceId}")
        device = {
            "nodes":[
                    node1,
                    node2
                ],
            "deviceId": deviceId,
            "position":{
                "x": ((x1+x2)/2),
                "y": 0,
                "z": ((1-y1-y2)/2),
                
                
            },
            "rotation": 0.0,
            "deviceType": className,
            
        }

        devices_json.append(device)
    
    # ---------- Components ---------- # 

    # wire json
    wire_json = []
    if data_wire is not None:
        for i, dw in enumerate(data_wire):
            
            # print(dw)
            angle, x1, y1, x2, y2 = dw
            # print(type(angle))

            # x1, y1, x2, y2, x3, y3, x4, y4 = map(float, dw)
            wireId = str(uuid.uuid4())
            wire_device = {
                "nodes":[
                        str(random.randint(0,999999)),
                        str(random.randint(0,999999))
                    ],
                
                "wireId": wireId,
                "position":{
                    "(x1, y1)": (x1, y1),
                    "y": 0,
                    "(x2, y2)": (x2, y2),
                    
                    
                },
                "rotation": angle,
                "deviceType": "line",
                
            }

            wire_json.append(wire_device)

    # ---------- Wire ---------- #

    # Final json returned
    json_data = {
        "wires": wire_json,
        "devices": devices_json,
        "freeNodes": []
    }
    return json.loads(json.dumps(json_data, indent=4))
    # print("type",type(json.dumps(json_data, indent=4)))
    # return json.dumps(json_data, indent=4)

# Component json
def componentJSON(devices: List[Component], freeNodes: List[FreeNode]):

    # components json
    devices_json = []
    devices_uuid = {}
    num_nodes = []
    for i, d in enumerate(devices):
        
        x1, y1, x2, y2 = d.x_top_left, d.y_top_left, d.x_bottom_right, d.y_bottom_right

        # get class name from label (0 - 10)
        # print("", d.class_component)
        className = get_class_mapping(int(d.class_component))
        
        if className in ["junction"]:
            nodes = 1
        elif className in ["text"]:
            continue
        # elif className == "transformer":
        #     nodes = 4
        else:
            nodes = 2
        num_nodes.append(nodes)
        # 3(transformer) - 2 up and 2 down
        # 8, 9 - 2 down
        # rest - 2 nodes(1 up, 1 down)

        deviceId = d.uuid
        if(nodes == 2):
            node_uuids = [d.uuid_endpoint_left, d.uuid_endpoint_right]
        elif(nodes == 1):
            node_uuids = [d.uuid_endpoint_left]

        device = {
            "nodes": node_uuids,
            "deviceId": deviceId,
            "position":{
                "x": ((x1+x2)/6),
                "y": 0,
                "z": ((1-y1-y2)/6),
                
                
            },
            "rotation": 90.0,
            "deviceType": className,
            
        }
        # devices_uuid[deviceId] = device

        devices_json.append(device)

    for fn in freeNodes:
        print("FN:", fn)
        x1, y1, x2, y2 = fn.x_top_left, fn.y_top_left, fn.x_bottom_right, fn.y_bottom_right
        freeNode = {
            "deviceId": str(uuid.uuid4()),
            "nodes": [fn.uuid],
            "position": {
                "x": ((fn.x_top_left+fn.x_bottom_right)/2),
                "y": 0,
                "z": ((1-fn.y_top_left-fn.y_bottom_right)/2)
            },
            "deviceType": "junction"
        }
        devices_json.append(freeNode)
    return devices_json

# Wire json
def wiresJSON(wires: List[Wire]):
    wire_json = []
    if wires is not None:

        for i, dw in enumerate(wires):
            
            # print(dw)
            x1, y1, x2, y2 = dw.x_top_left, dw.y_top_left, dw.x_bottom_right, dw.y_bottom_right

            node1, node2 = dw.uuid_endpoint_left, dw.uuid_endpoint_right
            wire_device = {
                "nodes":[
                        node1,
                        node2
                    ],
                "wireId": dw.uuid,
            }

            wire_json.append(wire_device)
    return wire_json

# def freeNodesJSON(devices: List[Component], freeNodes: List[FreeNode]):
#     freeNodes_json = []

#     for fn in freeNodes:
#         print("FN:", fn)
#         x1, y1, x2, y2 = fn.x_top_left, fn.y_top_left, fn.x_bottom_right, fn.y_bottom_right
#         freeNode = {
#             "nodeId": fn.uuid,
#             "position": {
#                 "x": ((fn.x_top_left+fn.x_bottom_right)/2),
#                 "y": 0,
#                 "z": ((1-fn.y_top_left-fn.y_bottom_right)/2)
#             }
#         }
#         devices.append(freeNode)
#     return devices

# Main test
# if __name__ == "__main__":
#     r, classes = extract_pred(r'C:\Users\HP\Desktop\wire_images\AC-Voltage-Detector-Circuit.png')
#     print(type(r))
#     print(toJSON(r, classes)) 