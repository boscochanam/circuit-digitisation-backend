import numpy as np
from PIL import Image, ImageDraw

# creating a white mask on the components detected
def create_white_mask(image: Image.Image, boxes: np.ndarray) -> Image.Image:
    """Create a copy of the image with white rectangles over detected areas"""
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    masked_image = image.copy()
    draw = ImageDraw.Draw(masked_image)
    
    for box in boxes:
        x1, y1, x2, y2 = map(int, box[:4])
        draw.rectangle([(x1, y1), (x2, y2)], fill='white')
    
    return masked_image