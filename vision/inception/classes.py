from uuid import uuid4
import math

# def calc_attach(x_top_left, y_top_left, x_bottom_right, y_bottom_right, flag):
#     center_x = (x_top_left + x_bottom_right) / 2
#     center_y = (y_top_left + y_bottom_right) / 2

#     x_offset = (x_top_left - x_bottom_right) * 0.05
    
#     return (center_x + x_offset, center_y) if flag else (center_x - x_offset, center_y)

# inicial repr

# class FreeNode:
#     def __init__(self, freenode_uuid, x, y):
#         self.x = x
#         self.y = y
#         self.uuid = freenode_uuid
#         self.uuid_endpoint_left = str(uuid.uuid4())
#         self.uuid_endpoint_right = str(uuid.uuid4())
#         self.is_attached_left = False
#         self.is_attached_right = False
#         self.is_attached_to_component_left = False
#         self.is_attached_to_component_right = False
#         self.left_wireid = None
#         self.right_wireid = None

#     def update_left_wireid(self, wireid):
#         self.left_wireid = wireid
    
#     def update_right_wireid(self, wireid):
#         self.right_wireid = wireid
        
#     def get_uuid_endpoint_left(self):
#         return self.uuid_endpoint_left
    
#     def get_uuid_endpoint_right(self):
#         return self.uuid_endpoint_right

#     def get_distance_wire_to_freenode(self, x, y):
#         return math.sqrt((self.x - x) ** 2 + (self.y - y) ** 2)
    
#     def __str__(self):
#         return f"FreeNode {self.uuid} at ({self.x}, {self.y})"

    

# Base Class
class Comp:
    def __init__(self, component_uuid, x_top_left, y_top_left, x_bottom_right, y_bottom_right, class_component):
        self.uuid = component_uuid
        self.x_top_left = x_top_left
        self.y_top_left = y_top_left
        self.x_bottom_right = x_bottom_right
        self.y_bottom_right = y_bottom_right
        self.class_component = class_component # string
    

    def get_area(self):
        return (self.x_bottom_right - self.x_top_left) * (self.y_bottom_right - self.y_top_left)
    
    def __str__(self):
        return f"Component {self.uuid} at ({self.x_top_left}, {self.y_top_left}) to ({self.x_bottom_right}, {self.y_bottom_right})"
    
    # calculates distance wrt wire endpoint(left/right)
    def get_distance_wire_to_component(self, x, y):
        # Calculate the horizontal distance
        if x < self.x_top_left:
            dist_x = self.x_top_left - x
        elif x > self.x_bottom_right:
            dist_x = x - self.x_bottom_right
        else:
            dist_x = 0
        
        # Calculate the vertical distance
        if y < self.y_top_left:
            dist_y = self.y_top_left - y
        elif y > self.y_bottom_right:
            dist_y = y - self.y_bottom_right
        else:
            dist_y = 0
        
        # The minimum distance to the component is the Euclidean distance
        return math.sqrt(dist_x ** 2 + dist_y ** 2)
    

# Component class inheriting from Base Component, with endpoints
class Component(Comp):
    def __init__(self, uuid, x_top_left, y_top_left, x_bottom_right, y_bottom_right, type):
        # Call parent constructor with type as class_component
        super().__init__(uuid, x_top_left, y_top_left, x_bottom_right, y_bottom_right, type)
        self.type = type  # Keep type separately for the Component class
        self.uuid_endpoint_left = str(uuid4())
        self.uuid_endpoint_right = str(uuid4())
        
        # Attachment flags
        self.is_attached_left = False
        self.is_attached_right = False
        self.is_attached_to_component_left = False
        self.is_attached_to_component_right = False

    # Explicitly add get_area method to ensure it's available
    def get_area(self):
        return abs(self.x_bottom_right - self.x_top_left) * abs(self.y_bottom_right - self.y_top_left)

    def __repr__(self):
        return f"Component({self.uuid}, {self.type}, {self.uuid_endpoint_left}, {self.uuid_endpoint_right})"

# Freenode class inheriting from Base Component with dynamic endpoints
class FreeNode(Comp):
    def __init__(self, component_uuid, x_top_left, y_top_left, x_bottom_right, y_bottom_right, class_name="junction", endpoints=None):
        # Call the parent class constructor (Subcomponent)
        super().__init__(component_uuid, x_top_left, y_top_left, x_bottom_right, y_bottom_right, class_name)
        
        # If provided, use the custom number of endpoints, else default to an empty list
        self.endpoints_uuid = endpoints if endpoints else []
        
        # For each new endpoint, create a new UUID
        # while len(self.endpoints) < 2:  # Ensure at least 2 endpoints by default
        #     self.endpoints.append(str(uuid.uuid4()))

    
    def __repr__(self):
        return f"Freenode({self.uuid}, {self.class_component}, {len(self.endpoints)} endpoints)"

    # def attach_endpoint(self, endpoint_index):
    #     """ Attach a given endpoint by index """
    #     if endpoint_index < len(self.endpoints):
    #         if endpoint_index == 0:
    #             self.is_attached_left = True
    #             self.is_attached_to_component_left = True
    #         elif endpoint_index == 1:
    #             self.is_attached_right = True
    #             self.is_attached_to_component_right = True


    def get_uuid(self):
        return self.uuid
    
    def get_endpoints(self):
        """ Return all UUIDs of the endpoints """
        return self.endpoints
        
    # def get_area(self):
    #     return (self.x_bottom_right - self.x_top_left) * (self.y_bottom_right - self.y_top_left)
    
    # calculates distance wrt wire endpoint(left/right)
    # def get_distance_wire_to_component(self, x, y):
    #     # Calculate the horizontal distance
    #     if x < self.x_top_left:
    #         dist_x = self.x_top_left - x
    #     elif x > self.x_bottom_right:
    #         dist_x = x - self.x_bottom_right
    #     else:
    #         dist_x = 0
        
    #     # Calculate the vertical distance
    #     if y < self.y_top_left:
    #         dist_y = self.y_top_left - y
    #     elif y > self.y_bottom_right:
    #         dist_y = y - self.y_bottom_right
    #     else:
    #         dist_y = 0
        
    #     # The minimum distance to the component is the Euclidean distance
    #     return math.sqrt(dist_x ** 2 + dist_y ** 2) 

class Wire:
    def __init__(self, angle, x_top_left, y_top_left, x_bottom_right, y_bottom_right):
        self.uuid = str(uuid4())
        self.angle = angle
        self.x_top_left = x_top_left
        self.y_top_left = y_top_left
        self.x_bottom_right = x_bottom_right
        self.y_bottom_right = y_bottom_right
        self.uuid_endpoint_left = str(uuid4())
        self.uuid_endpoint_right = str(uuid4())
        self.is_attached_left = False
        self.is_attached_right = False
        self.is_attached_to_component_left = False
        self.is_attached_to_component_right = False
        self.is_attached_to_freenode_left = False # True if attached to a freenode and left endpoint of wire
        self.is_attached_to_freenode_right = False # True if attached to a freenode and right endpoint of wire
        

    def is_longest_side(self):
        width = abs(self.x_bottom_right - self.x_top_left)
        height = abs(self.y_bottom_right - self.y_top_left)
        return width >= height  # Returns True if horizontal, False if vertical
    
    def update_uuid_endpoint_left(self, uuid):
        self.uuid_endpoint_left = uuid
    
    def update_uuid_endpoint_right(self, uuid):
        self.uuid_endpoint_right = uuid

    # Calculate the diagonal length (hypotenuse) of the bounding box
    def get_diagonal_radius(self):
        width = abs(self.x_bottom_right - self.x_top_left) / 2
        height = abs(self.y_bottom_right - self.y_top_left) / 2
        return math.sqrt(width**2 + height**2)

    # Calculate the left endpoint based on the hypotenuse adjustment
    def get_endpoint_left(self):
        center_x = (self.x_top_left + self.x_bottom_right) / 2
        center_y = (self.y_top_left + self.y_bottom_right) / 2
        radius = self.get_diagonal_radius()

        angle_rad = math.radians(self.angle)
        cos_angle = math.cos(angle_rad)
        sin_angle = math.sin(angle_rad)

        # Adjust left endpoint based on the hypotenuse
        x_left = center_x - radius * cos_angle
        y_left = center_y - radius * sin_angle

        return (self.uuid_endpoint_left, x_left, y_left)

    # Calculate the right endpoint based on the hypotenuse adjustment
    def get_endpoint_right(self):
        center_x = (self.x_top_left + self.x_bottom_right) / 2
        center_y = (self.y_top_left + self.y_bottom_right) / 2
        radius = self.get_diagonal_radius()

        angle_rad = math.radians(self.angle)
        cos_angle = math.cos(angle_rad)
        sin_angle = math.sin(angle_rad)

        # Adjust right endpoint based on the hypotenuse
        x_right = center_x + radius * cos_angle
        y_right = center_y + radius * sin_angle

        return (self.uuid_endpoint_right, x_right, y_right)

    def __str__(self):
        return f"Wire at ({self.x_top_left}, {self.y_top_left}) to ({self.x_bottom_right}, {self.y_bottom_right}) of angle {self.angle}"