from typing import List, Tuple, Dict
import math

def get_device_connection_points(x1_c: float, y1_c: float, x2_c: float, y2_c: float, num_uuids: int) -> List[Tuple[float, float]]:
    """Calculate center points for device connections based on number of UUIDs."""
    center_x = (x1_c + x2_c) / 2
    center_y = (y1_c + y2_c) / 2
    
    # Calculate y-axis offset based on number of UUIDs
    x_offset = (x1_c - x2_c) * 0.05
    
    points = []
    if num_uuids == 2:
        points.append((center_x + x_offset, center_y))  
        points.append((center_x - x_offset, center_y))  
    elif num_uuids == 4:
        # Two points at top and two at bottom, slightly offset
        points.extend([
            (center_x - x_offset, y1_c + x_offset),  # Top left
            (center_x + x_offset, y1_c + x_offset),  # Top right
            (center_x - x_offset, y2_c - x_offset),  # Bottom left
            (center_x + x_offset, y2_c - x_offset)   # Bottom right
        ])
    return points

def calculate_distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    """Calculate Euclidean distance between two points."""
    return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)

def find_closest_point(
    target_point: Tuple[float, float],
    wire_points: List[Tuple[float, float]],
    device_points: List[Tuple[float, float]],
    occupied_points: set,
    point_to_uuid: Dict[Tuple[float, float], str]
) -> Tuple[Tuple[float, float], str, bool]:  # Returns (closest_point, uuid, is_device)
    """Find the closest unoccupied point and its UUID."""
    min_distance = float('inf')
    closest_point = None
    closest_uuid = None
    is_device = False
    
    # Check wire points
    for point in wire_points:
        if point != target_point and point not in occupied_points:
            dist = calculate_distance(target_point, point)
            if dist < min_distance:
                min_distance = dist
                closest_point = point
                closest_uuid = point_to_uuid.get(point)
                is_device = False
    
    # Check device points
    for point in device_points:
        if point not in occupied_points:
            dist = calculate_distance(target_point, point)
            if dist < min_distance:
                min_distance = dist
                closest_point = point
                closest_uuid = point_to_uuid.get(point)
                is_device = True
    
    return closest_point, closest_uuid, is_device

def match_wire_device_points(
    data_device: List[Tuple[float, float, float, float]],
    data_wire: List[Tuple[float, float, float, float, float]],
    device_uuids: Dict[str, List[str]],
    num_nodes: List[int],
    wire_uuids: List[Tuple[str, str]],
    image_size: Tuple[int, int]
) -> List[Tuple[str, str]]:
    """Match wire endpoints with closest points and update UUIDs."""
    
    # Create mappings for points to UUIDs
    point_to_uuid = {}
    device_points = []
    width, height = image_size

    # Process device points and their UUIDs
    for device_coords, uuids, num_nodes in zip(data_device, device_uuids.values(), num_nodes):
        device_point_list = get_device_connection_points(*device_coords, num_nodes)
        device_points.extend(device_point_list)
        
        # Map points to their UUIDs
        for i, point in enumerate(device_point_list):
            point_to_uuid[point] = uuids[i]
    
    # Process wire points
    wire_points = []
    wire_point_pairs = []
    
    for wire_data, wire_uuid in zip(data_wire, wire_uuids):
        _, x1, y1, x2, y2 = wire_data
        point1, point2 = (x1, y1), (x2, y2)
        wire_points.extend([point1, point2])
        wire_point_pairs.append((point1, point2))
        
        # Map points to their UUIDs
        point_to_uuid[point1] = wire_uuid[0]
        point_to_uuid[point2] = wire_uuid[1]
    
    # Keep track of occupied points
    occupied_points = set()
    updated_wire_uuids = []
    
    # Match points
    for wire_points_pair, wire_uuid in zip(wire_point_pairs, wire_uuids):
        point1, point2 = wire_points_pair
        new_uuid1, new_uuid2 = wire_uuid
        
        # Process first point
        if point1 not in occupied_points:
            closest_point1, closest_uuid1, is_device1 = find_closest_point(
                point1, wire_points, device_points, occupied_points, point_to_uuid
            )
            if closest_point1:
                occupied_points.add(point1)
                occupied_points.add(closest_point1)
                if is_device1:
                    new_uuid1 = closest_uuid1
                else:
                    # Use common UUID for wire-to-wire connections
                    new_uuid1 = closest_uuid1 or new_uuid1
        
        # Process second point
        if point2 not in occupied_points:
            closest_point2, closest_uuid2, is_device2 = find_closest_point(
                point2, wire_points, device_points, occupied_points, point_to_uuid
            )
            if closest_point2:
                occupied_points.add(point2)
                occupied_points.add(closest_point2)
                if is_device2:
                    new_uuid2 = closest_uuid2
                else:
                    # Use common UUID for wire-to-wire connections
                    new_uuid2 = closest_uuid2 or new_uuid2
        
        updated_wire_uuids.append((new_uuid1, new_uuid2))
    
    return updated_wire_uuids