import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from matplotlib.path import Path

class CircuitSymbols:
    """Class containing methods to draw electrical component symbols"""
    
    @staticmethod
    def resistor(ax, x, y, width=40, height=20, rotation=0, **kwargs):
        """Draw a resistor symbol"""
        # Create zigzag path for resistor
        verts = [(0, 0), (5, 0), (10, height/2), (15, -height/2), 
                (20, height/2), (25, -height/2), (30, height/2),
                (35, -height/2), (40, 0), (width, 0)]
        
        # Apply rotation
        if rotation != 0:
            theta = np.radians(rotation)
            rot_matrix = np.array([[np.cos(theta), -np.sin(theta)], 
                                  [np.sin(theta), np.cos(theta)]])
            
            # Rotate around center
            center_x, center_y = width/2, 0
            verts_array = np.array(verts) - np.array([center_x, center_y])
            verts_array = np.dot(verts_array, rot_matrix.T)
            verts = verts_array + np.array([center_x, center_y])
            
        # Translate to position
        verts = [(x + xv, y + yv) for xv, yv in verts]
        
        # Create path
        codes = [Path.MOVETO] + [Path.LINETO] * (len(verts) - 1)
        path = Path(verts, codes)
        
        # Draw path
        patch = patches.PathPatch(path, **kwargs)
        ax.add_patch(patch)
        
        return patch
    
    @staticmethod
    def capacitor(ax, x, y, width=40, height=20, rotation=0, **kwargs):
        """Draw a capacitor symbol"""
        # Create path for capacitor (two parallel lines)
        left_line = [(width/2 - 5, height/2), (width/2 - 5, -height/2)]
        right_line = [(width/2 + 5, height/2), (width/2 + 5, -height/2)]
        connecting_line_left = [(0, 0), (width/2 - 5, 0)]
        connecting_line_right = [(width/2 + 5, 0), (width, 0)]
        
        lines = [left_line, right_line, connecting_line_left, connecting_line_right]
        
        # Apply rotation
        if rotation != 0:
            theta = np.radians(rotation)
            rot_matrix = np.array([[np.cos(theta), -np.sin(theta)], 
                                  [np.sin(theta), np.cos(theta)]])
            
            # Rotate each line around center
            center_x, center_y = width/2, 0
            for i, line in enumerate(lines):
                line_array = np.array(line) - np.array([center_x, center_y])
                line_array = np.dot(line_array, rot_matrix.T)
                lines[i] = line_array + np.array([center_x, center_y])
        
        # Translate to position
        for i, line in enumerate(lines):
            lines[i] = [(x + xv, y + yv) for xv, yv in line]
        
        # Draw lines
        for line in lines:
            line_patch = plt.Polygon(line, closed=False, **kwargs)
            ax.add_patch(line_patch)
        
        return lines
    
    @staticmethod
    def inductor(ax, x, y, width=40, height=20, rotation=0, **kwargs):
        """Draw an inductor symbol (coil)"""
        # Create semi-circles for inductor coils
        theta = np.linspace(0, np.pi, 20)
        num_coils = 4
        coil_width = width / (num_coils + 1)
        
        # Create baseline
        verts = [(0, 0)]
        
        # Add each coil
        for i in range(num_coils):
            coil_center_x = (i + 1) * coil_width
            semicircle_x = coil_center_x + coil_width/2 * np.cos(theta)
            semicircle_y = height/2 * np.sin(theta)
            
            for j in range(len(theta)):
                verts.append((semicircle_x[j], semicircle_y[j]))
        
        # Add final point
        verts.append((width, 0))
        
        # Apply rotation
        if rotation != 0:
            theta = np.radians(rotation)
            rot_matrix = np.array([[np.cos(theta), -np.sin(theta)], 
                                  [np.sin(theta), np.cos(theta)]])
            
            # Rotate around center
            center_x, center_y = width/2, 0
            verts_array = np.array(verts) - np.array([center_x, center_y])
            verts_array = np.dot(verts_array, rot_matrix.T)
            verts = verts_array + np.array([center_x, center_y])
        
        # Translate to position
        verts = [(x + xv, y + yv) for xv, yv in verts]
        
        # Create patch
        poly = plt.Polygon(verts, closed=False, **kwargs)
        ax.add_patch(poly)
        
        return poly
    
    @staticmethod
    def diode(ax, x, y, width=40, height=20, rotation=0, **kwargs):
        """Draw a diode symbol (triangle and line)"""
        # Triangle vertices
        tri_verts = [(width/2, -height/2), (width/2, height/2), (width*3/4, 0)]
        # Line vertices
        line_verts = [(width*3/4, height/2), (width*3/4, -height/2)]
        # Connecting lines
        left_line = [(0, 0), (width/2, 0)]
        right_line = [(width*3/4, 0), (width, 0)]
        
        all_shapes = [tri_verts, line_verts, left_line, right_line]
        
        # Apply rotation
        if rotation != 0:
            theta = np.radians(rotation)
            rot_matrix = np.array([[np.cos(theta), -np.sin(theta)], 
                                  [np.sin(theta), np.cos(theta)]])
            
            # Rotate shapes around center
            center_x, center_y = width/2, 0
            for i, shape in enumerate(all_shapes):
                shape_array = np.array(shape) - np.array([center_x, center_y])
                shape_array = np.dot(shape_array, rot_matrix.T)
                all_shapes[i] = shape_array + np.array([center_x, center_y])
        
        # Translate to position
        for i, shape in enumerate(all_shapes):
            all_shapes[i] = [(x + xv, y + yv) for xv, yv in shape]
        
        # Draw shapes
        triangle = plt.Polygon(all_shapes[0], closed=True, **kwargs)
        line = plt.Polygon(all_shapes[1], closed=False, **kwargs)
        left_conn = plt.Polygon(all_shapes[2], closed=False, **kwargs)
        right_conn = plt.Polygon(all_shapes[3], closed=False, **kwargs)
        
        ax.add_patch(triangle)
        ax.add_patch(line)
        ax.add_patch(left_conn)
        ax.add_patch(right_conn)
        
        return [triangle, line, left_conn, right_conn]
    
    @staticmethod
    def transistor(ax, x, y, width=40, height=40, rotation=0, **kwargs):
        """Draw a transistor symbol (NPN)"""
        # Base line
        base_line = [(0, 0), (width/3, 0)]
        
        # Collector and emitter lines
        collector_line = [(width*2/3, height/3), (width, height/3)]
        emitter_line = [(width*2/3, -height/3), (width, -height/3)]
        
        # Transistor body
        body_line = [(width/3, -height/2), (width/3, height/2)]
        ce_line = [(width/3, -height/3), (width*2/3, -height/3), 
                   (width*2/3, height/3), (width/3, height/3)]
        
        # Arrow for NPN
        arrow_pts = [(width*2/3 - 5, -height/3 + 5), (width*2/3, -height/3), 
                   (width*2/3 - 5, -height/3 - 5)]
        
        all_shapes = [base_line, collector_line, emitter_line, body_line, ce_line, arrow_pts]
        
        # Apply rotation if needed
        if rotation != 0:
            theta = np.radians(rotation)
            rot_matrix = np.array([[np.cos(theta), -np.sin(theta)], 
                                  [np.sin(theta), np.cos(theta)]])
            
            # Rotate shapes around center
            center_x, center_y = width/2, 0
            for i, shape in enumerate(all_shapes):
                shape_array = np.array(shape) - np.array([center_x, center_y])
                shape_array = np.dot(shape_array, rot_matrix.T)
                all_shapes[i] = shape_array + np.array([center_x, center_y])
        
        # Translate to position
        for i, shape in enumerate(all_shapes):
            all_shapes[i] = [(x + xv, y + yv) for xv, yv in shape]
        
        # Draw shapes
        patches_list = []
        for i, shape in enumerate(all_shapes):
            if i == 5:  # Arrow should be filled
                patch = plt.Polygon(shape, closed=True, fill=True, **kwargs)
            else:
                patch = plt.Polygon(shape, closed=False, **kwargs)
            ax.add_patch(patch)
            patches_list.append(patch)
        
        return patches_list
    
    @staticmethod
    def generic_component(ax, x, y, width=40, height=20, rotation=0, label="", **kwargs):
        """Draw a generic component (rectangle with text)"""
        # Draw rectangle
        rect = patches.Rectangle((x, y - height/2), width, height, rotation_point='center', 
                                angle=rotation, **kwargs)
        ax.add_patch(rect)
        
        # Add text in center
        if label:
            # Calculate text position after rotation
            if rotation == 0 or rotation == 180:
                text_x = x + width/2
                text_y = y
            else:
                text_x = x
                text_y = y + width/2
                
            ax.text(text_x, text_y, label, ha='center', va='center', 
                   rotation=rotation if -90 <= rotation <= 90 else rotation-180)
        
        return rect

def build_circuit_diagram(devices, wires, img_size, freenodes=None, figsize=(12, 8)):
    """
    Build a circuit diagram using matplotlib
    
    Args:
        devices: Dictionary of device objects from inception
        wires: Dictionary of wire objects from inception
        img_size: Tuple with (width, height) of the original image
        freenodes: List of free node coordinates (optional)
        figsize: Tuple with (width, height) for matplotlib figure
        
    Returns:
        Matplotlib figure with reconstructed circuit
    """
    fig, ax = plt.subplots(figsize=figsize)
    img_width, img_height = img_size
    
    # Set limits based on image dimensions
    ax.set_xlim(0, img_width)
    ax.set_ylim(img_height, 0)  # Invert y-axis to match image coordinates
    
    # Component colors and styles
    component_color = 'blue'
    component_props = {'edgecolor': component_color, 'facecolor': 'none', 
                      'linewidth': 2, 'alpha': 0.9}
    
    # Wire properties
    wire_props = {'color': 'black', 'linewidth': 1.5, 'alpha': 0.9}
    
    # Symbol factory mapping component types to their draw functions
    symbol_factory = {
        'resistor': CircuitSymbols.resistor,
        'res': CircuitSymbols.resistor,
        'capacitor': CircuitSymbols.capacitor,
        'cap': CircuitSymbols.capacitor,
        'inductor': CircuitSymbols.inductor,
        'diode': CircuitSymbols.diode,
        'transistor': CircuitSymbols.transistor,
        'bjt': CircuitSymbols.transistor,
        'default': CircuitSymbols.generic_component
    }
    
    # Draw devices with appropriate symbols
    device_list = devices.values() if isinstance(devices, dict) else devices
    for device in device_list:
        try:
            # Extract coordinates and type
            if hasattr(device, 'coordinates'):
                coords = device.coordinates
                device_type = device.type if hasattr(device, 'type') else 'unknown'
                pins = device.pins if hasattr(device, 'pins') else []
            elif isinstance(device, dict):
                coords = device.get('coordinates', [])
                device_type = device.get('type', 'unknown')
                pins = device.get('pins', [])
            else:
                continue
                
            # Skip if no coordinates
            if not coords:
                continue
                
            x1, y1, x2, y2 = coords
            width = x2 - x1
            height = y2 - y1
            center_x = x1 + width/2
            center_y = y1 + height/2
            
            # Determine component orientation
            is_horizontal = width > height
            rotation = 0 if is_horizontal else 90
            
            # Draw the appropriate symbol
            symbol_type = device_type.lower().replace(' ', '_')
            symbol_func = symbol_factory.get(symbol_type, symbol_factory['default'])
            
            # Scale symbol size based on detection
            symbol_width = width * 0.8  # 80% of detected width
            symbol_height = height * 0.4  # 40% of detected height
            
            if symbol_type in symbol_factory:
                symbol = symbol_func(ax, center_x - symbol_width/2, center_y, 
                                   width=symbol_width, height=symbol_height, 
                                   rotation=rotation, **component_props)
            else:
                label = device_type if len(device_type) <= 10 else device_type[:10] + "..."
                symbol = CircuitSymbols.generic_component(ax, center_x - symbol_width/2, center_y,
                                                       width=symbol_width, height=symbol_height,
                                                       rotation=rotation, label=label, **component_props)
            
            # Draw pins
            for pin in pins:
                # Get pin coordinates
                pin_coords = None
                if hasattr(pin, 'coordinates'):
                    pin_coords = pin.coordinates
                elif isinstance(pin, dict) and 'coordinates' in pin:
                    pin_coords = pin['coordinates']
                
                if pin_coords:
                    px, py = pin_coords
                    pin_dot = plt.Circle((px, py), radius=3, facecolor='red', 
                                      edgecolor='black', linewidth=1, alpha=0.7)
                    ax.add_patch(pin_dot)
        except Exception as e:
            print(f"Error plotting component {device_type if 'device_type' in locals() else 'unknown'}: {str(e)}")
    
    # Draw wires
    wire_list = wires.values() if isinstance(wires, dict) else wires
    for wire in wire_list:
        try:
            # Get wire coordinates
            points = []
            if hasattr(wire, 'coordinates'):
                points = wire.coordinates
            elif isinstance(wire, dict) and 'coordinates' in wire:
                points = wire['coordinates']
                
            if len(points) >= 2:
                # Extract x and y coordinates for plotting
                x_coords = [p[0] for p in points]
                y_coords = [p[1] for p in points]
                ax.plot(x_coords, y_coords, **wire_props)
        except Exception as e:
            print(f"Error plotting wire: {str(e)}")
    
    # Draw free nodes if provided
    if freenodes:
        for node in freenodes:
            x, y = node
            node_dot = plt.Circle((x, y), radius=4, facecolor='yellow', 
                                edgecolor='black', linewidth=1, alpha=0.9)
            ax.add_patch(node_dot)
    
    # Set title and turn off axis
    ax.set_title("Circuit Diagram Reconstruction")
    ax.set_axis_off()
    
    plt.tight_layout()
    return fig
