"""
Path Finding Algorithm for Indoor Navigation
Converted from C++ to Python
"""
import heapq
from typing import Dict, List, Tuple, Set


class Node:
    """Represents a navigation node in the building (room, corridor junction, etc.)"""
    def __init__(self, node_id: str, x: float, y: float, floor: int):
        self.id = node_id
        self.x = x
        self.y = y
        self.floor = floor
        self.neighbors: Dict[str, float] = {}  # neighbor_id -> distance
    
    def add_neighbor(self, neighbor_id: str, distance: float):
        self.neighbors[neighbor_id] = distance


class BuildingGraph:
    """Represents the navigation graph of the building"""
    def __init__(self):
        self.nodes: Dict[str, Node] = {}
        self.special_locations: Dict[str, str] = {}  # name -> node_id
    
    def add_node(self, node_id: str, x: float, y: float, floor: int) -> Node:
        node = Node(node_id, x, y, floor)
        self.nodes[node_id] = node
        return node
    
    def add_edge(self, node1_id: str, node2_id: str, distance: float):
        """Add bidirectional edge between two nodes"""
        if node1_id in self.nodes and node2_id in self.nodes:
            self.nodes[node1_id].add_neighbor(node2_id, distance)
            self.nodes[node2_id].add_neighbor(node1_id, distance)
    
    def add_special_location(self, name: str, node_id: str):
        """Add a named location (e.g., '3楼302教室')"""
        self.special_locations[name] = node_id
    
    def get_node_by_location(self, location_name: str) -> Node:
        """Get node by location name"""
        if location_name in self.special_locations:
            node_id = self.special_locations[location_name]
            return self.nodes[node_id]
        return None


class PathFinder:
    """Implements A* algorithm for finding the optimal path"""
    def __init__(self, graph: BuildingGraph):
        self.graph = graph
    
    def find_path(self, start_id: str, end_id: str, 
                  congestion_data: Dict[Tuple[str, str], float] = None) -> List[str]:
        """
        Find the optimal path from start to end node
        
        Args:
            start_id: Starting node ID
            end_id: Destination node ID
            congestion_data: Dictionary mapping (node1_id, node2_id) to congestion rate (0.0-1.0)
                             where 0.0 is no congestion and 1.0 is completely congested
        
        Returns:
            List of node IDs representing the path
        """
        if start_id not in self.graph.nodes or end_id not in self.graph.nodes:
            return []
        
        # Default congestion data if none provided
        if congestion_data is None:
            congestion_data = {}
        
        # A* algorithm
        open_set: List[Tuple[float, str]] = [(0, start_id)]  # (f_score, node_id)
        closed_set: Set[str] = set()
        
        # g_score[node_id] = cost from start to node
        g_score: Dict[str, float] = {start_id: 0}
        
        # f_score[node_id] = g_score + heuristic to end
        f_score: Dict[str, float] = {start_id: self._heuristic(start_id, end_id)}
        
        # came_from[node_id] = previous node in optimal path
        came_from: Dict[str, str] = {}
        
        while open_set:
            _, current_id = heapq.heappop(open_set)
            
            if current_id == end_id:
                return self._reconstruct_path(came_from, current_id)
            
            closed_set.add(current_id)
            current_node = self.graph.nodes[current_id]
            
            for neighbor_id, base_distance in current_node.neighbors.items():
                if neighbor_id in closed_set:
                    continue
                
                # Apply congestion factor to distance
                congestion_factor = 1.0
                edge = (current_id, neighbor_id)
                reverse_edge = (neighbor_id, current_id)
                
                if edge in congestion_data:
                    congestion_factor = 1.0 + congestion_data[edge] * 2  # Increase distance by up to 3x
                elif reverse_edge in congestion_data:
                    congestion_factor = 1.0 + congestion_data[reverse_edge] * 2
                
                distance = base_distance * congestion_factor
                tentative_g_score = g_score[current_id] + distance
                
                if neighbor_id not in g_score or tentative_g_score < g_score[neighbor_id]:
                    came_from[neighbor_id] = current_id
                    g_score[neighbor_id] = tentative_g_score
                    f_score[neighbor_id] = tentative_g_score + self._heuristic(neighbor_id, end_id)
                    
                    # Add to open set with priority = f_score
                    heapq.heappush(open_set, (f_score[neighbor_id], neighbor_id))
        
        return []  # No path found
    
    def _heuristic(self, node1_id: str, node2_id: str) -> float:
        """
        Calculate heuristic distance between two nodes
        Uses 3D Euclidean distance
        """
        node1 = self.graph.nodes[node1_id]
        node2 = self.graph.nodes[node2_id]
        
        # Calculate horizontal distance
        dx = node1.x - node2.x
        dy = node1.y - node2.y
        horizontal_dist = (dx**2 + dy**2)**0.5
        
        # Calculate vertical distance (floors)
        floor_dist = abs(node1.floor - node2.floor) * 5  # Assume each floor is 5 units high
        
        # Combined 3D distance
        return (horizontal_dist**2 + floor_dist**2)**0.5
    
    def _reconstruct_path(self, came_from: Dict[str, str], current_id: str) -> List[str]:
        """Reconstruct the path from came_from map"""
        path = [current_id]
        while current_id in came_from:
            current_id = came_from[current_id]
            path.append(current_id)
        return path[::-1]  # Reverse to get start->end


def generate_navigation_instructions(path: List[str], graph: BuildingGraph) -> List[str]:
    """
    Generate human-readable navigation instructions from a path
    
    Args:
        path: List of node IDs
        graph: Building graph
    
    Returns:
        List of instruction strings
    """
    if not path or len(path) < 2:
        return ["无法生成导航指令，路径不完整"]
    
    instructions = []
    for i in range(len(path) - 1):
        current_node = graph.nodes[path[i]]
        next_node = graph.nodes[path[i + 1]]
        
        # Calculate direction
        dx = next_node.x - current_node.x
        dy = next_node.y - current_node.y
        
        # Calculate distance
        distance = ((dx**2 + dy**2)**0.5)
        distance_str = f"{distance:.1f}米"
        
        # Floor change
        if current_node.floor < next_node.floor:
            instructions.append(f"向前走{distance_str}，然后上楼梯到{next_node.floor}楼")
        elif current_node.floor > next_node.floor:
            instructions.append(f"向前走{distance_str}，然后下楼梯到{next_node.floor}楼")
        else:
            # Same floor, determine direction
            if abs(dx) > abs(dy):
                # Primarily east-west movement
                if dx > 0:
                    instructions.append(f"向东走{distance_str}")
                else:
                    instructions.append(f"向西走{distance_str}")
            else:
                # Primarily north-south movement
                if dy > 0:
                    instructions.append(f"向北走{distance_str}")
                else:
                    instructions.append(f"向南走{distance_str}")
    
    return instructions
