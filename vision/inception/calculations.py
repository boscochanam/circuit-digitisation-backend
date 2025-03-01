from typing import List, Tuple, Dict, Set
from vision.inception.classes import Component
import math
# from inception.classes import Component


def calculate_avg_component_area(
    data_device: List[Component],
    image_size: Tuple[int, int]
):
    """ Calculate the average area of the components in the image. """
    area = 0
    for device in data_device:
        area += device.get_area()
    
    return math.sqrt(area / len(data_device))

def calculate_distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    """Calculate Euclidean distance between two points."""
    return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)