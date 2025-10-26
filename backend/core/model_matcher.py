"""
3D Model Path Matcher for Indoor Navigation
Maps navigation paths to 3D model coordinates
"""
from typing import Dict, List, Tuple, Any


class Point3D:
    """3D point with x, y, z coordinates"""
    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z
    
    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary for JSON serialization"""
        return {
            'x': self.x,
            'y': self.y,
            'z': self.z
        }


class ModelPathMatcher:
    """
    Maps navigation paths to 3D model coordinates
    Handles coordinate system conversion between navigation graph and 3D model
    """
    def __init__(self, model_scale: float = 1.0, floor_height: float = 4.0):
        """
        Initialize the model path matcher
        
        Args:
            model_scale: Scale factor to convert navigation coordinates to model coordinates
            floor_height: Height of each floor in model units
        """
        self.model_scale = model_scale
        self.floor_height = floor_height
        self.node_positions: Dict[str, Point3D] = {}
        
    def register_node(self, node_id: str, x: float, y: float, floor: int) -> None:
        """
        Register a navigation node with its 3D position
        
        Args:
            node_id: ID of the node
            x, y: 2D coordinates in navigation space
            floor: Floor number (0-based)
        """
        # Convert to 3D model coordinates
        model_x = x * self.model_scale
        model_y = floor * self.floor_height
        model_z = y * self.model_scale
        
        self.node_positions[node_id] = Point3D(model_x, model_y, model_z)
    
    def register_nodes_from_graph(self, graph_nodes: Dict[str, Any]) -> None:
        """
        Register multiple nodes from a navigation graph
        
        Args:
            graph_nodes: Dictionary mapping node IDs to node objects
                         Each node should have x, y, floor attributes
        """
        for node_id, node in graph_nodes.items():
            self.register_node(node_id, node.x, node.y, node.floor)
    
    def get_node_position(self, node_id: str) -> Point3D:
        """Get the 3D position of a node"""
        return self.node_positions.get(node_id)
    
    def path_to_3d_coordinates(self, path: List[str]) -> List[Dict[str, float]]:
        """
        Convert a path (list of node IDs) to 3D coordinates
        
        Args:
            path: List of node IDs representing the path
            
        Returns:
            List of 3D points as dictionaries {x, y, z}
        """
        coordinates = []
        for node_id in path:
            if node_id in self.node_positions:
                coordinates.append(self.node_positions[node_id].to_dict())
        return coordinates
    
    def generate_smooth_path(self, path: List[str], points_per_segment: int = 5) -> List[Dict[str, float]]:
        """
        Generate a smooth path with interpolated points between nodes
        
        Args:
            path: List of node IDs
            points_per_segment: Number of points to generate between each pair of nodes
            
        Returns:
            List of 3D points as dictionaries {x, y, z}
        """
        if len(path) < 2:
            return self.path_to_3d_coordinates(path)
        
        smooth_path = []
        for i in range(len(path) - 1):
            start_node_id = path[i]
            end_node_id = path[i + 1]
            
            start_pos = self.node_positions.get(start_node_id)
            end_pos = self.node_positions.get(end_node_id)
            
            if not start_pos or not end_pos:
                continue
            
            # Add the start point
            smooth_path.append(start_pos.to_dict())
            
            # Add interpolated points
            for j in range(1, points_per_segment):
                t = j / points_per_segment
                interp_x = start_pos.x + t * (end_pos.x - start_pos.x)
                interp_y = start_pos.y + t * (end_pos.y - start_pos.y)
                interp_z = start_pos.z + t * (end_pos.z - start_pos.z)
                
                smooth_path.append({
                    'x': interp_x,
                    'y': interp_y,
                    'z': interp_z
                })
        
        # Add the final point
        if path and path[-1] in self.node_positions:
            smooth_path.append(self.node_positions[path[-1]].to_dict())
        
        return smooth_path
    
    def generate_path_segments(self, path: List[str]) -> List[Dict[str, Any]]:
        """
        Generate path segments for 3D visualization
        
        Args:
            path: List of node IDs
            
        Returns:
            List of segment dictionaries with start and end points,
            and metadata like floor changes
        """
        if len(path) < 2:
            return []
        
        segments = []
        for i in range(len(path) - 1):
            start_node_id = path[i]
            end_node_id = path[i + 1]
            
            start_pos = self.node_positions.get(start_node_id)
            end_pos = self.node_positions.get(end_node_id)
            
            if not start_pos or not end_pos:
                continue
            
            # Determine if this segment crosses floors
            is_floor_change = abs(start_pos.y - end_pos.y) > 0.1
            
            segments.append({
                'start': start_pos.to_dict(),
                'end': end_pos.to_dict(),
                'is_floor_change': is_floor_change,
                'start_node_id': start_node_id,
                'end_node_id': end_node_id
            })
        
        return segments
