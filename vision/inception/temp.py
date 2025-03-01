import math
from typing import List
import uuid
from vision.inception.calculations import calculate_avg_component_area, calculate_distance
from vision.inception.classes import Component, Wire, FreeNode
import math

# check if junction
def is_junction(node):
    pass

wires = []
components = []

# for w in wires:
#     # left endpoint
#     w_uuid_left, x_left, y_left = w.get_endpoint_left()
#     # right endpoint
#     w_uuid_right, x_right, x_right = w.get_endpoint_right()

    # left match




def match_wire_device_points(
    components: List[Component],
    wires: List[Wire],
    freenodes: List[FreeNode]
): 
    """ Match the wire endpoints to the device nodes. """

    area_of_comp = calculate_avg_component_area(components, (10, 10))

    matching_threshold = 0.2 * area_of_comp
    
    
    def match_component_endpoints(c: Component, is_left: bool):
        """ Match a single component's left or right endpoint to the closest wire. """
        min_dist = float("inf")
        min_w = None
        min_flag = None

        # Get the appropriate endpoint UUID for the component
        component_uuid = c.get_uuid_endpoint_left() if is_left else c.get_uuid_endpoint_right()

        for w in wires:
            if w.is_attached_left and w.is_attached_right:
                continue

            # left endpoint
            w_uuid_left, x_left, y_left = w.get_endpoint_left()
            
            # right endpoint
            w_uuid_right, x_right, y_right = w.get_endpoint_right()
        
        
            temp_dist_left = c.get_distance_wire_to_component(x_left, y_left)
            temp_dist_right = c.get_distance_wire_to_component(x_right, y_right)

            min_temp_dist = min(temp_dist_left, temp_dist_right)
            
            # skip if not within threshold
            if min_temp_dist > matching_threshold:
                continue

            if min_temp_dist == temp_dist_left and not w.is_attached_left:
                flag = "left"
            elif min_temp_dist == temp_dist_right and not w.is_attached_right:
                flag = "right"
            else:
                continue
            
            if min_temp_dist < min_dist:
                min_dist = min_temp_dist
                min_w = w
                min_flag = flag
        
        if min_w:
        
            if min_flag == "left":
                min_w.update_uuid_endpoint_left(component_uuid)
                min_w.is_attached_left = True
                min_w.is_attached_to_component_left = True
            else:
                min_w.update_uuid_endpoint_right(component_uuid)
                min_w.is_attached_right = True
                min_w.is_attached_to_component_left = True
        
    def match_freenode_endpoints(f: FreeNode):
        """ Match a single freenode's left or right endpoint to the proximity wires. """
        # min_w = None
        # min_flag = None

        # Get the appropriate endpoint UUID for the freenode
        # freenode_uuid = f.get_uuid_endpoint_left() if is_left else f.get_uuid_endpoint_right()

        freenode_uuid = f.get_uuid()

        for w in wires:
            if w.is_attached_left and w.is_attached_right:
                continue
            if not (w.is_attached_to_component_left or w.is_attached_to_component_right):
                continue
            
            # Case 1: Wire is attached to a component on the left, and free on the right
            if w.is_attached_to_component_left and not w.is_attached_to_component_right:
                # Use the right endpoint (free side)
                w_uuid, x, y = w.get_endpoint_right()
                temp_dist = f.get_distance_wire_to_component(x, y)
                flag = "right"

            # Case 2: Wire is attached to a component on the right, and free on the left
            elif w.is_attached_to_component_right and not w.is_attached_to_component_left:
                # Use the left endpoint (free side)
                w_uuid, x, y = w.get_endpoint_left()
                temp_dist = f.get_distance_wire_to_component(x, y)
                flag = "left"
            
            
            # skip if not within threshold
            if temp_dist > matching_threshold:
                # prev usage
                # min_w = w
                # min_flag = flag

                if flag == "left":
                    w.update_uuid_endpoint_left(freenode_uuid)
                    w.is_attached_left = True
                    w.is_attached_to_freenode_left = True
                    
                    # min_w.is_attached_to_component_left = True
                else:
                    w.update_uuid_endpoint_right(freenode_uuid)
                    w.is_attached_right = True
                    w.is_attached_to_freenode_right = True
                
                f.endpoints_uuid.append(w.uuid)
                
                # check left or right side of freenode to add wire uuid for easy referencing after
                # if is_left:
                #     f.left_wireid = min_w.uuid
                # else:
                #     f.right_wireid = min_w.uuid 

            # if min_temp_dist == temp_dist_left and not w.is_attached_left:
            #     flag = "left"
            # elif min_temp_dist == temp_dist_right and not w.is_attached_right:
            #     flag = "right"
            # else:
            #     continue
            
            # if temp_dist < min_dist:
            #     min_dist = temp_dist
            #     min_w = w
            #     min_flag = flag
        
        # if min_w:
        
            

    # def match_freenode_endpoints(f: FreeNode, is_left: bool):
    #     """ Match a single freenode's left or right endpoint to the closest wire. """
    #     min_dist = float("inf")
    #     min_w = None
    #     min_flag = None

    #     # Get the appropriate endpoint UUID for the freenode
    #     freenode_uuid = f.get_uuid_endpoint_left() if is_left else f.get_uuid_endpoint_right()

    #     for w in wires:
    #         if w.is_attached_left and w.is_attached_right:
    #             continue
    #         if not (w.is_attached_to_component_left or w.is_attached_to_component_right):
    #             continue
            
    #         # Case 1: Wire is attached to a component on the left, and free on the right
    #         if w.is_attached_to_component_left and not w.is_attached_to_component_right:
    #             # Use the right endpoint (free side)
    #             w_uuid, x, y = w.get_endpoint_right()
    #             temp_dist = f.get_distance_wire_to_freenode(x, y)
    #             flag = "right"

    #         # Case 2: Wire is attached to a component on the right, and free on the left
    #         elif w.is_attached_to_component_right and not w.is_attached_to_component_left:
    #             # Use the left endpoint (free side)
    #             w_uuid, x, y = w.get_endpoint_left()
    #             temp_dist = f.get_distance_wire_to_freenode(x, y)
    #             flag = "left"
            
            
    #         # skip if not within threshold
    #         if temp_dist > matching_threshold:
    #             continue

    #         # if min_temp_dist == temp_dist_left and not w.is_attached_left:
    #         #     flag = "left"
    #         # elif min_temp_dist == temp_dist_right and not w.is_attached_right:
    #         #     flag = "right"
    #         # else:
    #         #     continue
            
    #         if temp_dist < min_dist:
    #             min_dist = temp_dist
    #             min_w = w
    #             min_flag = flag
        
    #     if min_w:
        
    #         if min_flag == "left":
    #             min_w.update_uuid_endpoint_left(freenode_uuid)
    #             min_w.is_attached_left = True
    #             min_w.is_attached_to_freenode_left = True
                
    #             # min_w.is_attached_to_component_left = True
    #         else:
    #             min_w.update_uuid_endpoint_right(freenode_uuid)
    #             min_w.is_attached_right = True
    #             min_w.is_attached_to_freenode_right = True
            
    #         # check left or right side of freenode to add wire uuid for easy referencing after
    #         if is_left:
    #             f.left_wireid = min_w.uuid
    #         else:
    #             f.right_wireid = min_w.uuid  

    # Match left endpoints
    for c in components:
        match_component_endpoints(c, is_left=True)

    # Match right endpoints
    for c in components:
        match_component_endpoints(c, is_left=False)

    # Try both matching at once for each freenode
    # modify to match only wires, since no components to junctions
    # join all wires u can, except ones already joined from before
    for f in freenodes:
        # match_freenode_endpoints(f, is_left=True)
        # match_freenode_endpoints(f, is_left=False)
        
        match_freenode_endpoints(f)
        


def match_wire_points(components: List[Component], wires: List[Wire], freenodes: List[FreeNode], threshold: float = 0.1):
    """Combine wires to form new free junction components."""
    
    area_of_comp = calculate_avg_component_area(components, (10, 10))
    matching_threshold = 0.2 * area_of_comp # maybe use this instead of threshold

    area_junction = math.sqrt(area_of_comp)

    def create_junction(endpoint1, endpoint2, wireId):
        """Helper function to create a new junction component."""
        jx_1, jy_1, jx_2, jy_2 = helper_freenode_dimension(endpoint1[0], endpoint1[1], endpoint2[0], endpoint2[1], area_junction)
        new_junction = FreeNode(str(uuid.uuid4()), jx_1, jy_1, jx_2, jy_2)
        new_junction.endpoints_uuid.append(wireId)

        freenodes.append(new_junction)
        return new_junction
    
    def helper_freenode_dimension(endpoint1_x, endpoint1_y, endpoint2_x, endpoint2_y, junc_threshold):
        """Helper function to modi freenodes to the list."""
        # Calculate the midpoint between the two endpoints
        midpoint_x = (endpoint1_x + endpoint2_x) / 2
        midpoint_y = (endpoint1_y + endpoint2_y) / 2

        # Calculate the dimensions for the freenode
        jx_1 = midpoint_x - junc_threshold
        jy_1 = midpoint_y - junc_threshold
        jx_2 = midpoint_x + junc_threshold
        jy_2 = midpoint_y + junc_threshold

        return jx_1, jy_1, jx_2, jy_2


    for i, wire1 in enumerate(wires):
        for wire2 in wires[i+1:]:

            new_junction = None
            # Skip if both wires are fully attached
            # if wire1.is_attached_to_component_left and wire1.is_attached_to_component_right:
            #     continue
            if wire1.is_attached_left and wire1.is_attached_right: continue
            
            # chk just in case
            if wire2.is_attached_left and wire2.is_attached_right: continue

            new_junction = None
            # Check for matching unattached endpoints
            if wire1.is_attached_to_component_left and not wire1.is_attached_to_component_right:
                # if wire2.is_attached_left and wire2.is_attached_right: continue

                # Check for proximity with wire2
                if wire2.is_attached_left and not wire2.is_attached_right:
                    distance = calculate_distance(wire1.get_endpoint_right()[1:], wire2.get_endpoint_left()[1:])
                    if distance < threshold:
                        new_junction = create_junction(wire1.get_endpoint_right()[1:], wire2.get_endpoint_left()[1:])
                        wire2.is_attached_right = True
                        wire2.is_attached_to_freenode_right = True
                        wire2.update_uuid_endpoint_right = new_junction.get_uuid()

                elif wire2.is_attached_right and not wire2.is_attached_left:
                    distance = calculate_distance(wire1.get_endpoint_right()[1:], wire2.get_endpoint_right()[1:])
                    if distance < threshold:
                        new_junction = create_junction(wire1.get_endpoint_right()[1:], wire2.get_endpoint_right()[1:])
                        wire2.is_attached_left = True
                        wire2.is_attached_to_freenode_left = True
                        wire2.update_uuid_endpoint_left = new_junction.get_uuid()

            elif wire1.is_attached_to_component_right and not wire1.is_attached_to_component_left:
                # Check for proximity with wire2
                if wire2.is_attached_left and not wire2.is_attached_right:
                    distance = calculate_distance(wire1.get_endpoint_left()[1:], wire2.get_endpoint_left()[1:])
                    if distance < threshold:
                        new_junction = create_junction(wire1.get_endpoint_left()[1:], wire2.get_endpoint_right()[1:])
                        wire2.is_attached_right = True
                        wire2.is_attached_to_freenode_right = True
                        wire2.update_uuid_endpoint_right = new_junction.get_uuid()

                elif wire2.is_attached_right and not wire2.is_attached_left:
                    distance = calculate_distance(wire1.get_endpoint_left()[1:], wire2.get_endpoint_right()[1:])
                    if distance < threshold:
                        new_junction = create_junction(wire1.get_endpoint_left()[1:], wire2.get_endpoint_right()[1:])
                        wire2.is_attached_left = True
                        wire2.is_attached_to_freenode_left = True
                        wire2.update_uuid_endpoint_left = new_junction.get_uuid()

                else:
                    print("how did we get here?")
                    continue
    
    # Create freenodes for wire endpoints which are unmatched
    for w in wires:
        if not w.is_attached_left:
            new_junction = create_junction(w.get_endpoint_left()[1:], w.get_endpoint_left()[1:], w.uuid)
            # new_junction = FreeNode(str(uuid.uuid4()), w.get_endpoint_left()[1:], w.get_endpoint_left()[1:])
            # new_junction.endpoints_uuid.append(w.uuid)
            # freenodes.append(new_junction)
            w.update_uuid_endpoint_left(new_junction.get_uuid())
            w.is_attached_left = True
            w.is_attached_to_freenode_left = True
        if not w.is_attached_right:
            new_junction = create_junction(w.get_endpoint_left()[1:], w.get_endpoint_left()[1:], w.uuid)
            # new_junction = FreeNode(str(uuid.uuid4()), w.get_endpoint_right()[1], w.get_endpoint_right()[2], w.get_endpoint_right()[1], w.get_endpoint_right()[2])
            # new_junction.endpoints_uuid.append(w.uuid)
            # freenodes.append(new_junction)
            w.update_uuid_endpoint_right(new_junction.get_uuid())
            w.is_attached_right = True
            w.is_attached_to_freenode_right = True

def conversion_to_freenodes(
        
        
    components: List[Component], 
    wires: List[Wire], 
    freenodes: List[FreeNode]
):
    """Convert junctions and wire to wire connections(now junctions) to form new freenodes."""
    for f in freenodes:
        
        junc_endpoint_left = f.get_uuid_endpoint_left()
        junc_endpoint_right = f.get_uuid_endpoint_right()

def connect_wires_directly(wires: List[Wire], threshold: float = 300000000):
    """
    Connect wires directly when their endpoints are close to each other,
    eliminating the need for junction/freenode components.
    """
    def update_wire_connections(wire1: Wire, wire2: Wire, endpoint1_type: str, endpoint2_type: str):
        """
        Update the connection states and UUIDs for two connecting wires.
        endpoint_type should be either 'left' or 'right'
        """
        # Get the UUID of the endpoints we're connecting
        uuid1 = wire1.uuid_endpoint_left if endpoint1_type == 'left' else wire1.uuid_endpoint_right
        uuid2 = wire2.uuid_endpoint_left if endpoint2_type == 'left' else wire2.uuid_endpoint_right
        
        # Update the connection states
        if endpoint1_type == 'left':
            wire1.is_attached_left = True
            wire1.is_attached_to_freenode_left = False
        else:
            wire1.is_attached_right = True
            wire1.is_attached_to_freenode_right = False
            
        if endpoint2_type == 'left':
            wire2.is_attached_left = True
            wire2.is_attached_to_freenode_left = False
        else:
            wire2.is_attached_right = True
            wire2.is_attached_to_freenode_right = False
        
        # Use the first wire's UUID for both endpoints to maintain the connection
        if endpoint2_type == 'left':
            wire2.uuid_endpoint_left = uuid1
        else:
            wire2.uuid_endpoint_right = uuid1

    # Check each pair of wires
    for i, wire1 in enumerate(wires):
        for wire2 in wires[i+1:]:
            # Skip if either wire is fully attached to components
            if (wire1.is_attached_to_component_left and wire1.is_attached_to_component_right) or \
               (wire2.is_attached_to_component_left and wire2.is_attached_to_component_right):
                continue

            # Get endpoints for both wires
            wire1_left = wire1.get_endpoint_left()[1:] 
            wire1_right = wire1.get_endpoint_right()[1:]
            wire2_left = wire2.get_endpoint_left()[1:]
            wire2_right = wire2.get_endpoint_right()[1:]

            # Check all possible endpoint combinations
            endpoint_combinations = [
                (wire1_left, wire2_left, 'left', 'left'),
                (wire1_left, wire2_right, 'left', 'right'),
                (wire1_right, wire2_left, 'right', 'left'),
                (wire1_right, wire2_right, 'right', 'right')
            ]

            for ep1, ep2, ep1_type, ep2_type in endpoint_combinations:
                # Calculate distance between endpoints
                distance = math.sqrt((ep1[0] - ep2[0])**2 + (ep1[1] - ep2[1])**2)
                
                # If endpoints are close enough and neither is attached to a component
                if float(distance) < float(threshold):
                    ep1_is_component = (ep1_type == 'left' and wire1.is_attached_to_component_left) or \
                                     (ep1_type == 'right' and wire1.is_attached_to_component_right)
                    ep2_is_component = (ep2_type == 'left' and wire2.is_attached_to_component_left) or \
                                     (ep2_type == 'right' and wire2.is_attached_to_component_right)
                    
                    if not ep1_is_component and not ep2_is_component:
                        update_wire_connections(wire1, wire2, ep1_type, ep2_type)
                        break

def remove_unused_freenodes(wires: List[Wire], freenodes: List[FreeNode]):
    """
    Remove freenodes that are no longer needed after direct wire connections.
    """
    # Create a set of all endpoint UUIDs still in use by wires
    active_endpoints = set()
    for wire in wires:
        active_endpoints.add(wire.uuid_endpoint_left)
        active_endpoints.add(wire.uuid_endpoint_right)
    
    # Filter out freenodes whose endpoints are no longer referenced by any wire
    return [freenode for freenode in freenodes 
            if freenode.uuid_endpoint_left in active_endpoints 
            or freenode.uuid_endpoint_right in active_endpoints]

def calculate_angle(x1, y1, x2, y2):
    """Calculate the angle between two points in degrees"""
    return math.degrees(math.atan2(y2 - y1, x2 - x1))

def merge_wires_through_freenode(wires: List[Wire], freenodes: List[FreeNode]):
    """
    Merge pairs of wires that connect through a freenode into single wires.
    Returns the new list of merged wires.
    """
    merged_wires = []
    used_wires = set()  # Keep track of wires that have been merged

    # Create a mapping of wire endpoints to wire objects
    endpoint_to_wire = {}
    for wire in wires:
        endpoint_to_wire[wire.uuid_endpoint_left] = ('left', wire)
        endpoint_to_wire[wire.uuid_endpoint_right] = ('right', wire)

    # Check each freenode for potential wire merges
    for fnode in freenodes:
        # Get wires connected to this freenode's endpoints
        connected_wires = []
        wire_endpoints = []
        
        # Check left endpoint
        if fnode.left_wireid in endpoint_to_wire:
            side, wire = endpoint_to_wire[fnode.left_wireid]
            connected_wires.append(wire)
            wire_endpoints.append(side)
            
        # Check right endpoint
        if fnode.right_wireid in endpoint_to_wire:
            side, wire = endpoint_to_wire[fnode.right_wireid]
            connected_wires.append(wire)
            wire_endpoints.append(side)
        
        # If we found two wires to merge
        if len(connected_wires) == 2 and connected_wires[0] != connected_wires[1]:
            wire1, wire2 = connected_wires
            
            # Skip if either wire has already been merged
            if wire1 in used_wires or wire2 in used_wires:
                continue
                
            # Create new merged wire
            # We'll create a new wire that spans from the non-freenode end of wire1
            # to the non-freenode end of wire2
            endpoints1 = (wire1.get_endpoint_left(), wire1.get_endpoint_right())
            endpoints2 = (wire2.get_endpoint_left(), wire2.get_endpoint_right())
            
            # Determine which endpoints to use for the new wire
            start_point = None
            end_point = None
            
            for ep in endpoints1:
                if ep[0] != fnode.left_wireid and ep[0] != fnode.right_wireid:
                    start_point = ep
                    
            for ep in endpoints2:
                if ep[0] != fnode.left_wireid and ep[0] != fnode.right_wireid:
                    end_point = ep
            
            if start_point and end_point:
                # Create new merged wire
                merged_wire = Wire(
                    angle=calculate_angle(start_point[1], start_point[2], end_point[1], end_point[2]),
                    x_top_left=start_point[1],
                    y_top_left=start_point[2],
                    x_bottom_right=end_point[1],
                    y_bottom_right=end_point[2]
                )
                
                # Transfer connection status from original wires
                if wire1.is_attached_to_component_left or wire2.is_attached_to_component_left:
                    merged_wire.is_attached_to_component_left = True
                if wire1.is_attached_to_component_right or wire2.is_attached_to_component_right:
                    merged_wire.is_attached_to_component_right = True
                    
                merged_wire.uuid_endpoint_left = start_point[0]
                merged_wire.uuid_endpoint_right = end_point[0]
                
                merged_wires.append(merged_wire)
                print("Merged wires:", wire1, wire2, "into", merged_wire)
                used_wires.add(wire1)
                used_wires.add(wire2)
            
    # Add any wires that weren't merged
    for wire in wires:
        if wire not in used_wires:
            print("Wire not merged:", wire)
            merged_wires.append(wire)
            
    return merged_wires