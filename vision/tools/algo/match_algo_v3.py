from collections import defaultdict
from dataclasses import dataclass
from typing import List, Tuple, Dict
import math

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

@dataclass
class ConnectionPoint:
    point: Point
    uuid: str
    is_device: bool
    device_uuid: str = None  # Only for device points
    is_occupied: bool = False
    wire_idx: int = None  # Added to track wire index for wire endpoints
    endpoint_idx: int = None  # Added to track which endpoint of the wire (0 or 1)

def calculate_distance(p1, p2):
    """Calculate Euclidean distance between two points."""
    return math.sqrt((p2.x - p1.x)**2 + (p2.y - p1.y)**2)

def get_device_connection_points(device, num_uuids):
    """Get connection points for a device."""
    x1, y1, x2, y2 = device
    center_x = (x1 + x2) / 2
    center_y = (y1 + y2) / 2

    points = []
    if num_uuids == 2:
        offset = (x2 - x1) * 0.05
        points.extend([
            Point(center_x + offset, center_y),
            Point(center_x - offset, center_y)
        ])
    elif num_uuids == 4:
        offset = (x2 - x1) * 0.1
        points.extend([
            Point(center_x - offset, y1),
            Point(center_x + offset, y1),
            Point(center_x - offset, y2),
            Point(center_x + offset, y2)
        ])
    return points

class SpatialGrid:
    """A spatial grid for faster nearest neighbor searches."""
    def __init__(self, points, cell_size):
        self.cell_size = cell_size
        self.grid = defaultdict(list)
        
        # Add points to grid
        for point in points:
            cell_x = int(point.point.x / cell_size)
            cell_y = int(point.point.y / cell_size)
            self.grid[(cell_x, cell_y)].append(point)
    
    def get_nearest_available_point(self, query_point, current_wire_idx=None, max_search_radius=float('inf')):
        """Find nearest available point within search radius, considering both device and wire points."""
        cell_x = int(query_point.x / self.cell_size)
        cell_y = int(query_point.y / self.cell_size)
        
        search_radius = 1
        min_dist = float('inf')
        nearest_point = None
        
        while search_radius * self.cell_size <= max_search_radius:
            for dx in range(-search_radius, search_radius + 1):
                for dy in range(-search_radius, search_radius + 1):
                    if abs(dx) == search_radius or abs(dy) == search_radius:
                        cell = (cell_x + dx, cell_y + dy)
                        for point in self.grid[cell]:
                            # Skip if point is already occupied
                            if point.is_occupied:
                                continue
                                
                            # Skip if point belongs to the same wire
                            if point.wire_idx == current_wire_idx:
                                continue
                                
                            dist = calculate_distance(query_point, point.point)
                            if dist < min_dist:
                                min_dist = dist
                                nearest_point = point
            
            if nearest_point is not None:
                return nearest_point, min_dist
            
            search_radius += 1
        
        return None, float('inf')

def match_wire_device_points(
    data_device,
    data_wire,
    device_uuids,
    wire_uuids
):
    """Enhanced wire and device point matching that handles both wire-to-device and wire-to-wire connections."""
    
    # Precompute all connection points
    all_connection_points = []
    device_index_to_uuid = list(device_uuids.keys())
    
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

    # Add wire endpoints with wire index information
    for wire_idx, (_, x1, y1, x2, y2) in enumerate(data_wire):
        all_connection_points.extend([
            ConnectionPoint(
                point=Point(x1, y1),
                uuid=wire_uuids[wire_idx][0],
                is_device=False,
                wire_idx=wire_idx,
                endpoint_idx=0
            ),
            ConnectionPoint(
                point=Point(x2, y2),
                uuid=wire_uuids[wire_idx][1],
                is_device=False,
                wire_idx=wire_idx,
                endpoint_idx=1
            )
        ])

    # Create spatial grid for efficient nearest neighbor search
    cell_size = 0.1  # Adjust based on your data distribution
    spatial_grid = SpatialGrid(all_connection_points, cell_size)
    
    # Process each wire
    for wire_idx, (_, x1, y1, x2, y2) in enumerate(data_wire):
        wire_points = [Point(x1, y1), Point(x2, y2)]
        
        for point_idx, wire_point in enumerate(wire_points):
            nearest_point, min_dist = spatial_grid.get_nearest_available_point(
                wire_point,
                current_wire_idx=wire_idx
            )
            
            if nearest_point:
                # Update wire_uuids based on the type of connection
                if nearest_point.is_device:
                    # Wire-to-device connection
                    if point_idx == 0:
                        wire_uuids[wire_idx] = (nearest_point.uuid, wire_uuids[wire_idx][1])
                    else:
                        wire_uuids[wire_idx] = (wire_uuids[wire_idx][0], nearest_point.uuid)
                else:
                    # Wire-to-wire connection
                    # Get the other endpoint's UUID of the connected wire
                    other_wire_idx = nearest_point.wire_idx
                    other_endpoint_idx = 1 - nearest_point.endpoint_idx  # Get opposite endpoint
                    other_uuid = wire_uuids[other_wire_idx][other_endpoint_idx]
                    
                    if point_idx == 0:
                        wire_uuids[wire_idx] = (other_uuid, wire_uuids[wire_idx][1])
                    else:
                        wire_uuids[wire_idx] = (wire_uuids[wire_idx][0], other_uuid)
                
                # Mark the point as occupied
                nearest_point.is_occupied = True
    
    return device_uuids, wire_uuids