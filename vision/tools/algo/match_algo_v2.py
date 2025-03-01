import math
from typing import List, Tuple, Dict, NamedTuple
import uuid
from dataclasses import dataclass
from collections import defaultdict

class Point(NamedTuple):
    x: float
    y: float

@dataclass
class ConnectionPoint:
    point: Point
    uuid: str
    is_device: bool
    device_uuid: str = None  # Only for device points
    is_occupied: bool = False

def calculate_distance(p1: Point, p2: Point) -> float:
    """Calculate Euclidean distance between two points."""
    return math.sqrt((p2.x - p1.x)**2 + (p2.y - p1.y)**2)

def get_device_connection_points(device: Tuple[float, float, float, float], num_uuids: int) -> List[Point]:
    """Get connection points for a device."""
    x1, y1, x2, y2 = device
    center_x = (x1 + x2) / 2
    center_y = (y1 + y2) / 2

    points = []
    if num_uuids == 2:
        offset = (x2 - x1) * 0.05
        # Top center and bottom center doesn't work for now 
        # center of componenet with offset
        points.extend([
            Point(center_x + offset, center_y),  # center with small offset
            Point(center_x - offset, center_y)   # center with small offset
        ])
    elif num_uuids == 4:
        offset = (x2 - x1) * 0.1
        points.extend([
            Point(center_x - offset, y1),  # Top left
            Point(center_x + offset, y1),  # Top right
            Point(center_x - offset, y2),  # Bottom left
            Point(center_x + offset, y2)   # Bottom right
        ])
    return points

class SpatialGrid:
    """A spatial grid for faster nearest neighbor searches."""
    def __init__(self, points: List[ConnectionPoint], cell_size: float):
        self.cell_size = cell_size
        self.grid = defaultdict(list)
        
        # Add points to grid
        for point in points:
            cell_x = int(point.point.x / cell_size)
            cell_y = int(point.point.y / cell_size)
            self.grid[(cell_x, cell_y)].append(point)
    
    def get_nearest_unoccupied(self, query_point: Point, max_search_radius: float = float('inf')) -> Tuple[ConnectionPoint, float]:
        """Find nearest unoccupied point within search radius."""
        cell_x = int(query_point.x / self.cell_size)
        cell_y = int(query_point.y / self.cell_size)
        
        search_radius = 1
        min_dist = float('inf')
        nearest_point = None
        
        while search_radius * self.cell_size <= max_search_radius:
            # Search in expanding square pattern
            for dx in range(-search_radius, search_radius + 1):
                for dy in range(-search_radius, search_radius + 1):
                    # Only check cells on the perimeter of the square
                    if abs(dx) == search_radius or abs(dy) == search_radius:
                        cell = (cell_x + dx, cell_y + dy)
                        for point in self.grid[cell]:
                            if not point.is_occupied:
                                dist = calculate_distance(query_point, point.point)
                                if dist < min_dist:
                                    min_dist = dist
                                    nearest_point = point
            
            if nearest_point is not None:
                return nearest_point, min_dist
            
            search_radius += 1
        
        return None, float('inf')

def match_wire_device_points(
    data_device: List[Tuple[float, float, float, float]],
    data_wire: List[Tuple[float, float, float, float, float]],
    device_uuids: Dict[str, List[str]],
    wire_uuids: List[Tuple[str, str]]
) -> Tuple[Dict[str, List[str]], List[Tuple[str, str]]]:
    """Optimized wire and device point matching."""
    
    
    # Precompute all connection points
    all_connection_points = []
    # print(len(device_uuids))
    device_index_to_uuid = list(device_uuids.keys())
    # print(device_index_to_uuid)
    print(len(device_index_to_uuid), len(data_device))
    # Add device connection points
    for dev_idx, device in enumerate(data_device):
        device_uuid = device_index_to_uuid[dev_idx]
        points = get_device_connection_points(device, len(device_uuids[device_uuid]))

        for point_idx, point in enumerate(points):
            all_connection_points.append(
                ConnectionPoint(
                    point=point,
                    uuid=device_uuids[device_uuid][point_idx],
                    is_device=True,
                    device_uuid=device_uuid
                )
            )

    # Add wire endpoints
    for wire_idx, (_, x1, y1, x2, y2) in enumerate(data_wire):
        all_connection_points.extend([
            ConnectionPoint(point=Point(x1, y1), uuid=wire_uuids[wire_idx][0], is_device=False),
            ConnectionPoint(point=Point(x2, y2), uuid=wire_uuids[wire_idx][1], is_device=False)
        ])

    # Create spatial grid for efficient nearest neighbor search
    # Choose cell_size based on average distance between points
    cell_size = 0.1  # This should be tuned based on your data distribution
    spatial_grid = SpatialGrid(all_connection_points, cell_size)
    
    # Process each wire
    for wire_idx, (_, x1, y1, x2, y2) in enumerate(data_wire):
        wire_points = [Point(x1, y1), Point(x2, y2)]
        
        for point_idx, wire_point in enumerate(wire_points):
            nearest_point, min_dist = spatial_grid.get_nearest_unoccupied(wire_point)
            
            if nearest_point:
                # Update wire UUID
                if point_idx == 0:
                    wire_uuids[wire_idx] = (nearest_point.uuid, wire_uuids[wire_idx][1])
                else:
                    wire_uuids[wire_idx] = (wire_uuids[wire_idx][0], nearest_point.uuid)
                
                # Mark point as occupied
                nearest_point.is_occupied = True
    
    return wire_uuids

# Example usage:
def create_example_data():
    data_wire = [
        (45, 0.1, 0.1, 0.3, 0.3),
        (90, 0.5, 0.1, 0.5, 0.4)
    ]
    
    data_device = [
        (0.0, 0.0, 0.2, 0.2),
        (0.4, 0.0, 0.6, 0.2)
    ]
    
    device_uuids = {
        str(uuid.uuid4()): [str(uuid.uuid4()), str(uuid.uuid4())],
        str(uuid.uuid4()): [str(uuid.uuid4()), str(uuid.uuid4()), 
                           str(uuid.uuid4()), str(uuid.uuid4())]
    }
    
    wire_uuids = [(str(uuid.uuid4()), str(uuid.uuid4())) for _ in data_wire]
    
    return data_wire, data_device, device_uuids, wire_uuids