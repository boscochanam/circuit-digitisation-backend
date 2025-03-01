import json
import uuid
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import random

from calculations import calculate_avg_component_area
from main import classInitialisation
from temp import connect_wires_directly, match_wire_device_points, merge_wires_through_freenode, remove_unused_freenodes

def plot_components_wires_and_freenodes(components, wires, freenodes):
    fig, ax = plt.subplots(figsize=(10, 10))

    # Plot each component as a rectangle
    for c in components:
        width = c.x_bottom_right - c.x_top_left
        height = c.y_bottom_right - c.y_top_left

        rect = patches.Rectangle(
            (c.x_top_left, c.y_top_left), width, height, 
            linewidth=1, edgecolor='blue', facecolor='lightblue', alpha=0.5
        )
        ax.add_patch(rect)
        ax.text(
            c.x_top_left + width / 2, c.y_top_left + height / 2, 
            f"Comp {str(c.uuid)[-4:]}", ha="center", va="center", color="blue"
        )

    # Plot each wire
    for w in wires:
        # Plot wire as a line
        x_vals = [w.x_top_left, w.x_bottom_right]
        y_vals = [w.y_top_left, w.y_bottom_right]
        ax.plot(x_vals, y_vals, "k-", lw=2)

        # Plot endpoints
        left_endpoint = w.get_endpoint_left()
        right_endpoint = w.get_endpoint_right()
        
        # Left endpoint
        color = 'purple' if w.is_attached_to_component_left else 'green'
        ax.plot(left_endpoint[1], left_endpoint[2], "o", color=color)
        label = "C" if w.is_attached_to_component_left else "W"
        ax.text(left_endpoint[1], left_endpoint[2], 
                f"{label}{str(left_endpoint[0])[-4:]}", 
                ha="right", color=color)

        # Right endpoint
        color = 'purple' if w.is_attached_to_component_right else 'red'
        ax.plot(right_endpoint[1], right_endpoint[2], "o", color=color)
        label = "C" if w.is_attached_to_component_right else "W"
        ax.text(right_endpoint[1], right_endpoint[2], 
                f"{label}{str(right_endpoint[0])[-4:]}", 
                ha="right", color=color)

    # Add legend
    legend_elements = [
        patches.Patch(facecolor='lightblue', edgecolor='blue', alpha=0.5, label='Component'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='purple', label='Component Connection', markersize=10),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='green', label='Wire Start', markersize=10),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='red', label='Wire End', markersize=10),
    ]
    ax.legend(handles=legend_elements, loc='upper right')

    # Configure plot
    ax.set_aspect('equal', 'box')
    ax.set_title("Components and Merged Wires")
    ax.set_xlabel("X Coordinate")
    ax.set_ylabel("Y Coordinate")
    plt.grid(True)
    plt.show()

# Update the main execution:
if __name__ == "__main__":
    with open('stored_data_2.json', 'r') as file:
        data = json.load(file)
    
    data_device = data['data_device']
    data_wire = data['data_wire']
    device_uuids = data['device_uuids']
    image_size = data['image_size']
    classes = data['classes']
    average_area = 0

    wire_uuid = [(str(uuid.uuid4()), str(uuid.uuid4())) for _ in range(len(data_wire))]
    
    devices, wires, freenodes = classInitialisation(data_device, data_wire, device_uuids, image_size, classes, average_area)

    # Perform initial matching
    match_wire_device_points(devices, wires, freenodes)
    plot_components_wires_and_freenodes(devices, wires, freenodes)
    
    # Merge wires that connect through freenodes
    wires = merge_wires_through_freenode(wires, freenodes)
    
    # Remove unused freenodes after merging
    freenodes = remove_unused_freenodes(wires, freenodes)
    
    # Visualize final results
    plot_components_wires_and_freenodes(devices, wires, freenodes)