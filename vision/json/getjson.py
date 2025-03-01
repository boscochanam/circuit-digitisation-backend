import json
import random
import numpy as np
import uuid

# from vision.proces
from vision.processing import extract_pred
# from vision.processing import extract_pred
from vision.class_map import get_class_mapping

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
def deviceJSON(data_device, classes):

    # components json
    devices_json = []
    devices_uuid = {}
    num_nodes = []
    for i, d in enumerate(data_device):
        
        x1, y1, x2, y2 = map(float, d)

        # get class name from label (0 - 10)
        class_num = int(classes[i])
        className = get_class_mapping(class_num)
        
        if className in ["text"]:
            continue
        elif className == "transformer":
            nodes = 4
        else:
            nodes = 2
        num_nodes.append(nodes)
        # 3(transformer) - 2 up and 2 down
        # 8, 9 - 2 down
        # rest - 2 nodes(1 up, 1 down)

        deviceId = str(uuid.uuid4())
        device_uuid = [deviceId]

        # adding nodes based on the component
        for _ in range(nodes):
            new_node = str(uuid.uuid4())
            device_uuid.append(new_node)

        device = {
            "nodes": device_uuid[1:],
            "deviceId": deviceId,
            "position":{
                "x": ((x1+x2)/2),
                "y": 0,
                "z": ((1-y1-y2)/2),
                
                
            },
            "rotation": 0.0,
            "deviceType": className,
            
        }
        # devices_uuid = [deviceId, node1, node2]
        devices_uuid[deviceId] = device_uuid[1:]
        # devices_uuid.append(device_uuid)
        devices_json.append(device)
    return devices_json, devices_uuid, num_nodes

# Wire json
def wireJSON(data_wire, wire_uuid):
    wire_json = []
    if data_wire is not None:
        for i, dw in enumerate(data_wire):
            
            # print(dw)
            angle, x1, y1, x2, y2 = dw
            # print(type(angle))

            # x1, y1, x2, y2, x3, y3, x4, y4 = map(float, dw)
            wireId = str(uuid.uuid4())
            node1, node2 = wire_uuid[i]
            wire_device = {
                "nodes":[
                        node1,
                        node2
                    ],
                
                "wireId": wireId,
                # for Future use
                # "position":{
                #     "(x1, y1)": (x1, y1),
                #     "y": 0,
                #     "(x2, y2)": (x2, y2),
                    
                    
                # },
                # "rotation": angle,
                # "deviceType": "line",
                
            }

            wire_json.append(wire_device)
    return wire_json

# Main test
# if __name__ == "__main__":
#     r, classes = extract_pred(r'C:\Users\HP\Desktop\wire_images\AC-Voltage-Detector-Circuit.png')
#     print(type(r))
#     print(toJSON(r, classes)) 