import streamlit as st
import numpy as np
import io
import uuid
import cv2
from PIL import Image, ImageDraw
from ultralytics import YOLO
import json
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle

# Import existing processing functions
from vision.json.getjson import deviceJSON
from vision.json.new_json import componentJSON, wiresJSON
from vision.processing import extract_pred
from vision.wire.processing import extract_pred_wire
from vision.tools.operations import create_white_mask
from vision.inception.main import inceptionFunction as inception
# Import new circuit visualization module
from vision.visualization.circuit_viz import build_circuit_diagram

# Set page config
st.set_page_config(page_title="Circuit Detector", layout="wide")

# Load models
@st.cache_resource
def load_models():
    component_model = YOLO('models/98MAPbest.pt')
    wire_model = YOLO('models/best_wire_new.pt')
    return component_model, wire_model

# Function to display bounding boxes
def draw_boxes(image, boxes, labels=None, colors=None):
    img = image.copy()
    draw = ImageDraw.Draw(img)
    
    if colors is None:
        colors = {
            'default': (255, 0, 0)  # Red as default
        }
    
    for i, box in enumerate(boxes):
        x1, y1, x2, y2 = map(int, box[:4])
        
        label = labels[i] if labels is not None else None
        color = colors.get(label, colors['default']) if isinstance(colors, dict) else colors
        
        draw.rectangle([(x1, y1), (x2, y2)], outline=color, width=2)
        if label:
            draw.text((x1, y1-15), str(label), fill=color)
    
    return img

# Add a function to directly visualize YOLO model results
def display_yolo_results(results, source_image):
    """Display YOLO results directly to verify detection is working"""
    # Convert source_image to numpy array if it's a PIL image
    if isinstance(source_image, Image.Image):
        img_array = np.array(source_image)
    else:
        img_array = source_image
        
    # Plot results on the image
    res_plotted = results[0].plot()
    return Image.fromarray(res_plotted)

# Function to plot circuit diagram using matplotlib
def plot_circuit_diagram(devices, wires, img_width, img_height, background_image=None):
    """
    Create a matplotlib plot of circuit components and wires
    
    Args:
        devices: Dictionary of device objects
        wires: Dictionary of wire objects
        img_width, img_height: Dimensions of the image
        background_image: Optional background image as numpy array
    
    Returns:
        matplotlib figure
    """
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Set the limits based on image dimensions
    ax.set_xlim(0, img_width)
    ax.set_ylim(img_height, 0)  # Invert y-axis to match image coordinates
    
    # Add background image if provided
    if background_image is not None:
        ax.imshow(background_image, extent=[0, img_width, img_height, 0], alpha=0.3)
    
    # Component colors and styles
    component_color = 'green'
    pin_color = 'red'
    wire_color = 'blue'
    
    # Draw devices
    device_list = devices.values() if isinstance(devices, dict) else devices
    for device in device_list:
        try:
            # Extract coordinates
            if hasattr(device, 'coordinates'):
                coords = device.coordinates
            elif isinstance(device, dict) and 'coordinates' in device:
                coords = device['coordinates']
            else:
                continue
                
            x1, y1, x2, y2 = coords
            width = x2 - x1
            height = y2 - y1
            
            # Draw component rectangle
            component = Rectangle((x1, y1), width, height, 
                                linewidth=2, edgecolor=component_color, 
                                facecolor='none', alpha=0.8)
            ax.add_patch(component)
            
            # Get device label/type
            device_type = ''
            if hasattr(device, 'type'):
                device_type = device.type
            elif isinstance(device, dict) and 'type' in device:
                device_type = device['type']
                
            # Add label
            ax.text(x1, y1-5, device_type, fontsize=8, color=component_color)
            
            # Draw pins
            pins = []
            if hasattr(device, 'pins'):
                pins = device.pins
            elif isinstance(device, dict) and 'pins' in device:
                pins = device['pins']
                
            for pin in pins:
                # Get pin coordinates
                pin_coords = None
                if hasattr(pin, 'coordinates'):
                    pin_coords = pin.coordinates
                elif isinstance(pin, dict) and 'coordinates' in pin:
                    pin_coords = pin['coordinates']
                
                if pin_coords:
                    px, py = pin_coords
                    pin_circle = Circle((px, py), radius=3, 
                                        facecolor=pin_color, edgecolor='black', 
                                        linewidth=1, alpha=0.8)
                    ax.add_patch(pin_circle)
        except Exception as e:
            print(f"Error plotting component: {str(e)}")
    
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
                ax.plot(x_coords, y_coords, color=wire_color, linewidth=2, alpha=0.8)
        except Exception as e:
            print(f"Error plotting wire: {str(e)}")
    
    # Set plot title and hide axes
    ax.set_title("Circuit Diagram")
    ax.set_axis_off()
    
    plt.tight_layout()
    return fig

def main():
    st.title("Circuit Diagram Analyzer")
    st.write("Upload a circuit diagram to analyze its components and connections")
    
    # Sidebar for controls
    st.sidebar.header("Controls")
    confidence_threshold = st.sidebar.slider("Detection Confidence", 0.1, 1.0, 0.5, 0.05)
    
    # Display options
    st.sidebar.header("Display Options")
    show_original = st.sidebar.checkbox("Show Original Image", True)
    show_components = st.sidebar.checkbox("Show Component Detection", True)
    show_masked = st.sidebar.checkbox("Show Masked Image", True)
    show_wires = st.sidebar.checkbox("Show Wire Detection", True)
    show_raw_detections = st.sidebar.checkbox("Show Raw Wire Detections", True)  # New option
    show_combined = st.sidebar.checkbox("Show Combined Result", True)
    show_json = st.sidebar.checkbox("Show JSON Output", True)
    
    # Wire detection options
    use_original_for_wires = st.sidebar.checkbox("Use Original Image for Wire Detection", False)
    
    # Load models
    component_model, wire_model = load_models()
    
    # File uploader
    uploaded_file = st.file_uploader("Upload Circuit Diagram", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        # Read image
        image_bytes = uploaded_file.read()
        image = Image.open(io.BytesIO(image_bytes))
        width, height = image.size
        
        # Create columns for the main content
        col1, col2 = st.columns(2)
        
        # Original Image
        if show_original:
            with col1:
                st.header("Original Image")
                st.image(image, use_column_width=True)
        
        # Component Detection
        data_device, classes, component_boxes = extract_pred(image, model=component_model, conf_threshold=confidence_threshold)
        
        if show_components:
            with col2:
                st.header("Component Detection")
                component_img = draw_boxes(image, component_boxes)
                st.image(component_img, use_column_width=True)
                
                with st.expander("Component Data"):
                    st.write("Classes:", classes)
                    st.write("Bounding Boxes:", component_boxes.tolist())
        
        # Filter data for matching
        filtered_data_device = [data_device[i] for i in range(len(classes)) if classes[i] not in ('0', '10')]
        
        # Component JSON (for getting device uuid)
        devices_json, devices_uuid, num_nodes = deviceJSON(data_device, classes)
        
        # Map coords to device id
        data_device_dict = {}
        i = 0
        for k, v in devices_uuid.items():
            data_device_dict[k] = data_device[i]
            i += 1
        
        # Create masked image
        masked_image = create_white_mask(image, component_boxes)
        
        if show_masked:
            with col1:
                st.header("Masked Image")
                st.image(masked_image, use_column_width=True)
        
        # Wire detection - use either masked or original image based on checkbox
        wire_source_image = image if use_original_for_wires else masked_image
        
        # Get raw results first
        raw_wire_results = wire_model(wire_source_image, conf=confidence_threshold)
        
        # Show raw detections if selected
        if show_raw_detections:
            with col2:
                st.header("Raw Wire Model Output")
                raw_vis = display_yolo_results(raw_wire_results, wire_source_image)
                st.image(raw_vis, use_column_width=True)
        
        # Process wire detection results and collect free nodes
        freenodes = []
        try:
            data_wire = extract_pred_wire(wire_source_image, model=wire_model, conf_threshold=confidence_threshold)
            if data_wire is None:
                data_wire = []
            
            # Collect endpoints as potential free nodes
            for wire_data in data_wire:
                if len(wire_data) >= 5:
                    _, x1, y1, x2, y2 = wire_data
                    freenodes.extend([(x1, y1), (x2, y2)])
        except Exception as e:
            st.error(f"Error in wire detection: {str(e)}")
            data_wire = []
        
        # Inception (component and wire joining)
        devices, wires = inception(data_device_dict, data_wire, (width, height), classes)
        
        # Ensure devices and wires are properly formatted
        if not isinstance(devices, dict):
            devices = {i: dev for i, dev in enumerate(devices)} if devices else {}
        if not isinstance(wires, dict):
            wires = {i: wire for i, wire in enumerate(wires)} if wires else {}
            
        # Filter free nodes - remove those that are connected to components
        connected_points = set()
        for device in devices.values():
            if hasattr(device, 'pins'):
                for pin in device.pins:
                    if hasattr(pin, 'coordinates'):
                        connected_points.add(tuple(pin.coordinates))
        
        # Keep only unconnected nodes
        freenodes = list(set(tuple(node) for node in freenodes) - connected_points)
        
        # Generate JSON with free nodes
        component_json = componentJSON(devices, freenodes)
        wires_json = wiresJSON(wires)
        
        json_data = {
            "wires": wires_json,
            "devices": component_json,
            "freeNodes": []  # Free nodes are now included in devices
        }
        
        # Display final results
        if show_combined:
            with col1:
                st.header("Combined Result")
                
                # Original PIL drawing for comparison (can be removed later)
                final_img = image.copy()
                draw = ImageDraw.Draw(final_img)
                
                # Draw components and wires using PIL (original method)
                device_list = devices.values() if isinstance(devices, dict) else devices
                for device in device_list:
                    try:
                        # Try object attribute access (for Component objects)
                        if hasattr(device, 'coordinates'):
                            coords = device.coordinates
                        # Try dictionary access
                        elif isinstance(device, dict) and 'coordinates' in device:
                            coords = device['coordinates']
                        else:
                            coords = []
                            
                        if coords:
                            x1, y1, x2, y2 = coords
                            draw.rectangle([(x1, y1), (x2, y2)], outline=(0, 255, 0), width=2)
                            
                            # Draw pins - handle both styles of access
                            pins = []
                            if hasattr(device, 'pins'):
                                pins = device.pins
                            elif isinstance(device, dict) and 'pins' in device:
                                pins = device['pins']
                                
                            for pin in pins:
                                # Get pin coordinates - handle both styles
                                pin_coords = None
                                if hasattr(pin, 'coordinates'):
                                    pin_coords = pin.coordinates
                                elif isinstance(pin, dict) and 'coordinates' in pin:
                                    pin_coords = pin['coordinates']
                                
                                if pin_coords:
                                    px, py = pin_coords
                                    draw.ellipse([(px-3, py-3), (px+3, py+3)], fill=(255, 0, 0))
                    except Exception as e:
                        st.error(f"Error drawing component: {str(e)}")
                        st.write("Component data:", device)
                
                # Draw wires - similar approach for wire objects
                wire_list = wires.values() if isinstance(wires, dict) else wires
                for wire in wire_list:
                    try:
                        # Get coordinates using appropriate access method
                        points = []
                        if hasattr(wire, 'coordinates'):
                            points = wire.coordinates
                        elif isinstance(wire, dict) and 'coordinates' in wire:
                            points = wire['coordinates']
                            
                        if len(points) >= 2:
                            for i in range(0, len(points)-1):
                                x1, y1 = points[i]
                                x2, y2 = points[i+1]
                                draw.line([(x1, y1), (x2, y2)], fill=(0, 0, 255), width=2)
                    except Exception as e:
                        st.error(f"Error drawing wire: {str(e)}")
                        st.write("Wire data:", wire)
                
                # Add free nodes to the visualization
                for node in freenodes:
                    x, y = node
                    draw.ellipse([(x-3, y-3), (x+3, y+3)], fill='yellow', outline='black')
                
                # Display the PIL image version
                st.image(final_img, use_column_width=True, caption="Raw Detection Results")
                
                # Add circuit reconstruction with proper symbols using matplotlib
                st.subheader("Circuit Reconstruction")
                
                # Create circuit diagram with proper component symbols
                circuit_fig = build_circuit_diagram(
                    devices,
                    wires,
                    (width, height),
                    freenodes=freenodes  # Pass free nodes to the visualization
                )
                
                # Display the circuit diagram
                st.pyplot(circuit_fig)
                
                # Add download button for the circuit diagram
                # Save figure to bytes buffer
                buf = io.BytesIO()
                circuit_fig.savefig(buf, format='png', dpi=300, bbox_inches='tight')
                buf.seek(0)
                
                st.download_button(
                    label="Download Circuit Diagram",
                    data=buf,
                    file_name="circuit_diagram.png",
                    mime="image/png"
                )

        # Display JSON output
        if show_json:
            with col2:
                st.header("JSON Output")
                st.json(json_data)
                
                # Download button for JSON
                json_str = json.dumps(json_data, indent=2)
                st.download_button(
                    label="Download JSON",
                    data=json_str,
                    file_name="circuit_data.json",
                    mime="application/json"
                )

if __name__ == "__main__":
    main()
