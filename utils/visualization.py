import numpy as np
from PIL import Image, ImageDraw
import cv2

def draw_components(image, boxes, labels=None, colors=None):
    """Draw component boxes on the image with optional labels."""
    img = image.copy()
    draw = ImageDraw.Draw(img)
    
    if colors is None:
        colors = {
            'default': (255, 0, 0)
        }
    
    for i, box in enumerate(boxes):
        x1, y1, x2, y2 = map(int, box[:4])
        
        label = labels[i] if labels is not None else None
        color = colors.get(label, colors['default']) if isinstance(colors, dict) else colors
        
        draw.rectangle([(x1, y1), (x2, y2)], outline=color, width=2)
        if label:
            draw.text((x1, y1-15), str(label), fill=color)
    
    return img

def draw_wires(image, wire_data):
    """Draw detected wires on the image."""
    img = image.copy()
    draw = ImageDraw.Draw(img)
    
    for data in wire_data:
        angle, x1, y1, x2, y2 = data
        draw.line([(x1, y1), (x2, y2)], fill=(0, 0, 255), width=2)
        
        # Optional: Draw angle information
        mid_x, mid_y = (x1 + x2) // 2, (y1 + y2) // 2
        draw.text((mid_x, mid_y), f"{angle:.1f}°", fill=(255, 0, 0))
    
    return img

def draw_circuit(image, devices, wires):
    """Draw the complete circuit with components and connections."""
    img = image.copy()
    draw = ImageDraw.Draw(img)
    
    # Draw components
    for device_id, device in devices.items():
        coords = device.get('coordinates', [])
        if coords:
            x1, y1, x2, y2 = coords
            draw.rectangle([(x1, y1), (x2, y2)], outline=(0, 255, 0), width=2)
            
            # Draw component label
            label = device.get('type', '')
            draw.text((x1, y1-15), label, fill=(0, 255, 0))
            
            # Draw pins
            for pin in device.get('pins', []):
                px, py = pin.get('coordinates', [0, 0])
                pin_id = pin.get('id', '')
                draw.ellipse([(px-3, py-3), (px+3, py+3)], fill=(255, 0, 0))
                draw.text((px+5, py+5), pin_id, fill=(255, 0, 0))
    
    # Draw wires
    for wire in wires:
        points = wire.get('coordinates', [])
        if len(points) >= 2:
            for i in range(0, len(points)-1):
                x1, y1 = points[i]
                x2, y2 = points[i+1]
                draw.line([(x1, y1), (x2, y2)], fill=(0, 0, 255), width=2)
        
        # Draw connection points
        for point in points:
            x, y = point
            draw.ellipse([(x-2, y-2), (x+2, y+2)], fill=(255, 255, 0))
    
    return img
