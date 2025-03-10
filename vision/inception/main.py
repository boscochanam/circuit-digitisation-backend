import sys
from typing import List, Tuple, Dict
import math
import uuid
import json

from loguru import logger
from vision.inception.classes import Component, Wire, FreeNode
from vision.inception.calculations import calculate_avg_component_area
from vision.inception.temp import match_wire_device_points, match_wire_points, conversion_to_freenodes
from vision.class_map import get_class_mapping

def classInitialisation(
    data_device: Dict[str, Tuple[float, float, float, float]],
    data_wire: Dict[str, Tuple[float, float, float, float, float]],
    image_size: List[Tuple[str, str]],
    classes: List[str]
) -> Tuple[List[Component], List[Wire], List[FreeNode]]:
    """ Initialize the classes and the data. """

    device_list = []
    wire_list = []
    freenode_list = []

    for i, device in enumerate(data_device):
        print(f"Device: {device} with class: {classes[i]}")
        # Use the class name directly without conversion
        if classes[i] == "junction":  # Compare string directly
            print("Found a free node")
            x_top_left, y_top_left, x_bottom_right, y_bottom_right = data_device[device]
            
            freenode_uuid = str(uuid.uuid4())
            freenode = FreeNode(freenode_uuid, x_top_left, y_top_left, x_bottom_right, y_bottom_right)
            freenode_list.append(freenode)
            continue

        # normal devices
        device_uuid = str(uuid.uuid4())
        x_top_left, y_top_left, x_bottom_right, y_bottom_right = data_device[device]
        device = Component(device_uuid, x_top_left, y_top_left, x_bottom_right, y_bottom_right, classes[i])
        device_list.append(device)
    
    for wire in data_wire:
        angle, x_top_left, y_top_left, x_bottom_right, y_bottom_right = wire[0], wire[1], wire[2], wire[3], wire[4]
        wire = Wire(angle, x_top_left, y_top_left, x_bottom_right, y_bottom_right)
        wire_list.append(wire)
    
    return device_list, wire_list, freenode_list

def inceptionFunction(data_device, data_wire, image_size, classes):
    # based on the len of data_wire
    wire_uuid = [(str(uuid.uuid4()), str(uuid.uuid4())) for _ in range(len(data_wire))] 

    devices, wires, freenodes = classInitialisation(data_device, data_wire, image_size, classes)
    avg_area = calculate_avg_component_area(devices, image_size)

    nodes = {} 
    belongs = {}
    for d in devices:
        node1_pos = (d.x_top_left, (d.y_top_left + d.y_bottom_right)/2)
        node2_pos = (d.x_bottom_right, (d.y_top_left + d.y_bottom_right)/2)
        node1_uuid = d.uuid_endpoint_left
        node2_uuid = d.uuid_endpoint_right

        nodes[node1_uuid] = node1_pos
        nodes[node2_uuid] = node2_pos
        belongs[node1_uuid] = d.uuid
        belongs[node2_uuid] = d.uuid

    for w in wires:
        left = w.get_endpoint_left()
        right = w.get_endpoint_right()
        nodes[left[0]] = left[1:]
        nodes[right[0]] = right[1:]
        belongs[left[0]] = w.uuid
        belongs[right[0]] = w.uuid

    iters = 5
    while(iters > 0):
        iters-=1

        # Use half of the average component area for joining threshold
        min_dist = 10 * avg_area  # Changed from 1.5 to 0.5
        logger.debug(f"Using joining threshold of {min_dist} (half of average component area: {avg_area})")
        
        # parents = {k: k for k in nodes.keys()}
        parents = {}
        for k in nodes.keys():
            parents[k] = k
        
        # Graph variable
        graph = {}
        print("got nodes")
        def calculate_distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
            """Calculate Euclidean distance between two points."""
            return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
        # Union 
        
        for k1, p1 in nodes.items():
            distSort = []
            for k2, p2 in nodes.items():
                if k1 == k2:
                    continue
                if(belongs[k1] == belongs[k2]): continue
                d = calculate_distance(p1, p2)
                # Add all close nodes, not just the closest one
                if d < min_dist:
                    distSort.append((d, k2))

            # Sort by distance and take the N closest points
            distSort.sort()
            max_connections = 3  # Allow more connections per node
            
            for dist, k2 in distSort[:max_connections]:
                if k1 not in graph:
                    graph[k1] = [k2]
                else:
                    graph[k1].append(k2)
                if k2 not in graph:
                    graph[k2] = [k1]
                else:
                    graph[k2].append(k1)
        
        print("created graph")
        
        def dfs_visit(node, visited):
            
            for x in graph[node]:
                if x not in visited:
                    visited.add(x)
                    dfs_visit(x, visited)
            return visited
        
        visited = set()
        for node in graph.keys():
            if node not in visited:
                visited.add(node)
                tempVis = set()
                
                visited = dfs_visit(node, tempVis)
            
            avg = [0,0]
            for v in tempVis:
                avg[0] += nodes[v][0]
                avg[1] += nodes[v][1]
            
            avg[0] /= len(tempVis)
            avg[1] /= len(tempVis)

            for v in tempVis:
                parents[v] = node
                visited.add(v)
                nodes[v] = (avg[0], avg[1])
        
        print("done dfs")
        for p in parents:
            print(p, parents[p])
            
        for d in devices:
            d.uuid_endpoint_left = parents[d.uuid_endpoint_left]
            d.uuid_endpoint_right = parents[d.uuid_endpoint_right]

        for w in wires:
            w.uuid_endpoint_left = parents[w.uuid_endpoint_left]
            w.uuid_endpoint_right = parents[w.uuid_endpoint_right]

        

    # Modify junction detection logic
    junctions = set()
    deviceNodes = set()
    nodePositions = {}  # Store positions for close node detection
    
    # First pass: collect all device nodes and their positions
    for d in devices:
        deviceNodes.add(d.uuid_endpoint_left)
        deviceNodes.add(d.uuid_endpoint_right)
        nodePositions[d.uuid_endpoint_left] = (d.x_top_left, (d.y_top_left + d.y_bottom_right)/2)
        nodePositions[d.uuid_endpoint_right] = (d.x_bottom_right, (d.y_top_left + d.y_bottom_right)/2)

    # Second pass: check wire endpoints
    for w in wires:
        left_pos = w.get_endpoint_left()
        right_pos = w.get_endpoint_right()
        
        # Check if wire endpoints are close to device nodes
        left_close = False
        right_close = False
        
        for device_node in deviceNodes:
            if calculate_distance(left_pos[1:], nodePositions[device_node]) < min_dist:
                left_close = True
            if calculate_distance(right_pos[1:], nodePositions[device_node]) < min_dist:
                right_close = True
                
        if not left_close:
            junctions.add(w.uuid_endpoint_left)
        if not right_close:
            junctions.add(w.uuid_endpoint_right)

    # Create junction components
    junc_uuid = [str(uuid.uuid4()) for _ in range(len(junctions))]
    for i, j in enumerate(junctions):
        temp = Component(junc_uuid[i], nodes[j][0], nodes[j][1], nodes[j][0], nodes[j][1], "junction")
        temp.uuid_endpoint_left = j
        temp.uuid_endpoint_right = j
        devices.append(temp)

    return devices, wires

    
if __name__ == "__main__":
    with open('stored_data_2.json', 'r') as file:
        data = json.load(file)
    
    # Assuming the JSON structure matches the function parameters
    data_device = data['data_device']
    data_wire = data['data_wire']
    device_uuids = data['device_uuids']
    image_size = data['image_size']
    classes = data['classes']
    average_area = 0

    # based on the len of data_wire
    wire_uuid = [(str(uuid.uuid4()), str(uuid.uuid4())) for _ in range(len(data_wire))] 
    
    devices, wires, freenodes = classInitialisation(data_device, data_wire, device_uuids, image_size, classes, average_area)

    # pass 1 - from components to wires only
    match_wire_device_points(devices, wires, freenodes)

    # pass 2 - from wires => getting freenodes
    match_wire_points(wires, devices, freenodes)

    # conversion of freenodes => merging wires
    conversion_to_freenodes(wires, devices, freenodes) 


    # [print(device) for device in devices]
    # [print(wire) for wire in wires]

    print(image_size)
    print("Average Area: ", calculate_avg_component_area(devices, image_size))
    print("FreeNodes: ", freenodes)