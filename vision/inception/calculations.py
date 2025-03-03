from typing import List, Tuple
from .classes import Component, Comp
import math

def calculate_avg_component_area(devices: List[Component], image_size: Tuple[int, int]) -> float:
    """Calculate average component area from list of devices"""
    if not devices:
        return 0
    
    area = 0
    for device in devices:
        # Calculate area directly since get_area() might not be accessible
        width = abs(device.x_bottom_right - device.x_top_left)
        height = abs(device.y_bottom_right - device.y_top_left)
        area += width * height

    return area / len(devices)

def calculate_grid_size(image_size: Tuple[int, int], avg_area: float) -> float:
    """Calculate appropriate grid size based on average component size"""
    min_dimension = min(image_size)
    grid_cells = 32  # Target number of grid cells
    return min_dimension / grid_cells

def snap_to_grid(value: float, grid_size: float) -> float:
    """Snap a value to the nearest grid point"""
    return round(value / grid_size) * grid_size

def calculate_connection_threshold(avg_area: float, image_size: Tuple[int, int]) -> float:
    """Calculate optimal connection threshold based on component density"""
    grid_size = calculate_grid_size(image_size, avg_area)
    return grid_size * 0.25  # Quarter of grid size for precise connections

def align_component_position(component: Component, grid_size: float):
    """Align component position to grid"""
    component.x_top_left = snap_to_grid(component.x_top_left, grid_size)
    component.y_top_left = snap_to_grid(component.y_top_left, grid_size)
    component.x_bottom_right = snap_to_grid(component.x_bottom_right, grid_size)
    component.y_bottom_right = snap_to_grid(component.y_bottom_right, grid_size)

def calculate_distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    """Calculate Euclidean distance between two points."""
    return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)