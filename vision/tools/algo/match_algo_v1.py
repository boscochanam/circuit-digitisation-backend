import math
from typing import List, Tuple, Dict
import uuid

def calculate_distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    """Calculate Euclidean distance between two points."""
    return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)

def get_device_connection_points(device: Tuple[float, float, float, float], num_uuids: int) -> List[Tuple[float, float]]:
    """
    Get connection points for a device based on its bounds and number of UUIDs.
    Returns points in top center and bottom center (with slight x offsets if num_uuids == 4).
    """
    x1, y1, x2, y2 = device
    center_x = (x1 + x2) / 2
    center_y = (y1 + y2) / 2
    offset = (x2 - x1) * 0.05
    points = []
    if num_uuids == 2:
        points.append((center_x + offset, center_y))  
        points.append((center_x - offset, center_y))  
    elif num_uuids == 4:
        # Two points at top and two at bottom, slightly offset
        points.extend([
            (center_x - offset, y1),  # Top left
            (center_x + offset, y1),  # Top right
            (center_x - offset, y2),  # Bottom left
            (center_x + offset, y2)   # Bottom right
        ])
    return points

def match_wire_device_points(
    data_device: List[Tuple[float, float, float, float]],
    data_wire: List[Tuple[float, float, float, float, float]],
    device_uuids: Dict[str, List[str]],  # Changed to use UUID as key
    wire_uuids: List[Tuple[str, str]]
) -> Tuple[Dict[str, List[str]], List[Tuple[str, str]]]:
    """
    Match wire endpoints with their closest device connection points or other wire endpoints.
    
    Args:
        data_wire: List of (angle, x1, y1, x2, y2) for each wire
        data_device: List of (x1, y1, x2, y2) for each device
        device_uuids: Dictionary mapping device UUID to list of connection point UUIDs
        wire_uuids: List of (uuid1, uuid2) pairs for each wire
    
    Returns:
        Updated device_uuids and wire_uuids
    """
    # Track which UUIDs are occupied
    occupied_uuids = set()
    for uuids in device_uuids.values():
        occupied_uuids.update(uuids)
    for uuid1, uuid2 in wire_uuids:
        if uuid1: occupied_uuids.add(uuid1)
        if uuid2: occupied_uuids.add(uuid2)
    
    # Create a mapping of device index to device UUID for easier lookup
    device_index_to_uuid = list(device_uuids.keys())
    
    # Process each wire
    for wire_idx, wire in enumerate(data_wire):
        _, x1, y1, x2, y2 = wire
        wire_points = [(x1, y1), (x2, y2)]
        
        # For each endpoint of the wire
        for point_idx, wire_point in enumerate(wire_points):
            min_distance = float('inf')
            closest_uuid = None
            is_device = False
            device_uuid = None
            connection_point_idx = None
            
            # Check distances to device connection points
            for dev_idx, device in enumerate(data_device):
                device_uuid_key = device_index_to_uuid[dev_idx]
                connection_points = get_device_connection_points(device, len(device_uuids[device_uuid_key]))
                for conn_idx, conn_point in enumerate(connection_points):
                    uuid_value = device_uuids[device_uuid_key][conn_idx]
                    if uuid_value not in occupied_uuids:
                        dist = calculate_distance(wire_point, conn_point)
                        if dist < min_distance:
                            min_distance = dist
                            closest_uuid = uuid_value
                            is_device = True
                            device_uuid = device_uuid_key
                            connection_point_idx = conn_idx
            
            # Check distances to other wire endpoints
            for other_wire_idx, other_wire in enumerate(data_wire):
                if other_wire_idx != wire_idx:
                    _, ox1, oy1, ox2, oy2 = other_wire
                    other_points = [(ox1, oy1), (ox2, oy2)]
                    for other_point_idx, other_point in enumerate(other_points):
                        curr_uuid = wire_uuids[other_wire_idx][other_point_idx]
                        if curr_uuid not in occupied_uuids:
                            dist = calculate_distance(wire_point, other_point)
                            if dist < min_distance:
                                min_distance = dist
                                closest_uuid = curr_uuid
                                is_device = False
                                device_uuid = None
                                connection_point_idx = other_point_idx
            
            # Update UUIDs based on closest point
            if closest_uuid:
                if point_idx == 0:
                    wire_uuids[wire_idx] = (closest_uuid, wire_uuids[wire_idx][1])
                else:
                    wire_uuids[wire_idx] = (wire_uuids[wire_idx][0], closest_uuid)
                occupied_uuids.add(closest_uuid)
    
    return device_uuids, wire_uuids

# Example usage:
def create_example_data():
    # Create sample data
    data_wire = [
        (45, 0.1, 0.1, 0.3, 0.3),  # Wire 1
        (90, 0.5, 0.1, 0.5, 0.4)   # Wire 2
    ]
    
    data_device = [
        (0.0, 0.0, 0.2, 0.2),      # Device 1 (2 UUIDs)
        (0.4, 0.0, 0.6, 0.2)       # Device 2 (4 UUIDs)
    ]
    
    # Initialize UUIDs with UUID keys
    device_uuids = {
        str(uuid.uuid4()): [str(uuid.uuid4()), str(uuid.uuid4())],  # Device 1: 2 UUIDs
        str(uuid.uuid4()): [str(uuid.uuid4()), str(uuid.uuid4()), 
                           str(uuid.uuid4()), str(uuid.uuid4())]     # Device 2: 4 UUIDs
    }
    
    wire_uuids = [(str(uuid.uuid4()), str(uuid.uuid4())) for _ in data_wire]
    
    return data_wire, data_device, device_uuids, wire_uuids

# Example usage
"""
data_wire, data_device, device_uuids, wire_uuids = create_example_data()
updated_device_uuids, updated_wire_uuids = match_wire_device_points(
    data_wire, data_device, device_uuids, wire_uuids
)
"""