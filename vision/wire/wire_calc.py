from math import atan2, degrees
import numpy as np

def calculate_angle(coords):
    """Calculate rotation angle of longest side relative to x-axis."""
    # Convert coordinates to points format [(x1,y1), (x2,y2), (x3,y3), (x4,y4)]
    points = [(coords[i], coords[i+1]) for i in range(0, 8, 2)]
    
    # Calculate lengths of all sides
    sides = []
    for i in range(4):
        x1, y1 = points[i]
        x2, y2 = points[(i+1) % 4]
        length = np.hypot(x2-x1, y2-y1)
        sides.append((length, (x1, y1, x2, y2)))
    
    # Get coordinates of longest side
    longest_side = max(sides, key=lambda x: x[0])
    x1, y1, x2, y2 = longest_side[1]
    
    # Calculate angle with x-axis
    angle = degrees(atan2(y2-y1, x2-x1))

    # Get center point(in case we need it)
    center_x = sum(coords[::2]) / 4
    center_y = sum(coords[1::2]) / 4
    # radius = 5

    # use this to get the center point of the line
    # draw.ellipse(
    #     [(center_x-radius, center_y-radius), 
    #         (center_x+radius, center_y+radius)], 
    #     fill='green'
    # )
    return angle, x1, y1, x2, y2
 

# Example usage
if __name__ == "_main_":
    calculate_angle("")