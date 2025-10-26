"""
Database models for Indoor Navigation System
"""
from typing import Dict, List, Any, Optional
import json
from datetime import datetime


class BaseModel:
    """Base class for all models"""
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary for JSON serialization"""
        return self.__dict__
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseModel':
        """Create model instance from dictionary"""
        instance = cls()
        for key, value in data.items():
            setattr(instance, key, value)
        return instance


class Building(BaseModel):
    """Represents a building in the system"""
    def __init__(self, building_id: str = None, name: str = None, 
                 floors: int = None, description: str = None):
        self.building_id = building_id
        self.name = name
        self.floors = floors
        self.description = description
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at


class Floor(BaseModel):
    """Represents a floor in a building"""
    def __init__(self, floor_id: str = None, building_id: str = None,
                 floor_number: int = None, name: str = None,
                 map_url: str = None):
        self.floor_id = floor_id
        self.building_id = building_id
        self.floor_number = floor_number
        self.name = name
        self.map_url = map_url
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at


class Room(BaseModel):
    """Represents a room on a floor"""
    def __init__(self, room_id: str = None, floor_id: str = None,
                 name: str = None, room_number: str = None,
                 room_type: str = None, x: float = None, y: float = None):
        self.room_id = room_id
        self.floor_id = floor_id
        self.name = name
        self.room_number = room_number
        self.room_type = room_type  # classroom, office, lab, etc.
        self.x = x  # X coordinate on floor map
        self.y = y  # Y coordinate on floor map
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at


class NavigationNode(BaseModel):
    """Represents a node in the navigation graph"""
    def __init__(self, node_id: str = None, building_id: str = None,
                 floor_id: str = None, x: float = None, y: float = None,
                 node_type: str = None, name: str = None):
        self.node_id = node_id
        self.building_id = building_id
        self.floor_id = floor_id
        self.x = x
        self.y = y
        self.node_type = node_type  # room, junction, stairs, elevator, etc.
        self.name = name
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at


class NavigationEdge(BaseModel):
    """Represents an edge between two navigation nodes"""
    def __init__(self, edge_id: str = None, node1_id: str = None,
                 node2_id: str = None, distance: float = None,
                 edge_type: str = None):
        self.edge_id = edge_id
        self.node1_id = node1_id
        self.node2_id = node2_id
        self.distance = distance
        self.edge_type = edge_type  # hallway, stairs, elevator, etc.
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at


class User(BaseModel):
    """Represents a user of the navigation system"""
    def __init__(self, user_id: str = None, open_id: str = None,
                 nickname: str = None, avatar_url: str = None):
        self.user_id = user_id
        self.open_id = open_id  # WeChat OpenID
        self.nickname = nickname
        self.avatar_url = avatar_url
        self.settings = {
            'voice_volume': 80,  # 0-100
            'wake_word': '小导小导',
            'favorite_destinations': []
        }
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at
    
    def update_settings(self, new_settings: Dict[str, Any]) -> None:
        """Update user settings"""
        self.settings.update(new_settings)
        self.updated_at = datetime.now().isoformat()


class NavigationHistory(BaseModel):
    """Represents a navigation history entry"""
    def __init__(self, history_id: str = None, user_id: str = None,
                 start_node_id: str = None, end_node_id: str = None,
                 start_time: str = None, end_time: str = None,
                 path: List[str] = None):
        self.history_id = history_id
        self.user_id = user_id
        self.start_node_id = start_node_id
        self.end_node_id = end_node_id
        self.start_time = start_time or datetime.now().isoformat()
        self.end_time = end_time
        self.path = path or []  # List of node IDs in the path
        self.created_at = datetime.now().isoformat()


class FavoriteDestination(BaseModel):
    """Represents a user's favorite destination"""
    def __init__(self, favorite_id: str = None, user_id: str = None,
                 node_id: str = None, name: str = None):
        self.favorite_id = favorite_id
        self.user_id = user_id
        self.node_id = node_id
        self.name = name
        self.created_at = datetime.now().isoformat()


class CongestionData(BaseModel):
    """Represents congestion data for a path segment"""
    def __init__(self, congestion_id: str = None, node1_id: str = None,
                 node2_id: str = None, congestion_rate: float = None,
                 timestamp: str = None):
        self.congestion_id = congestion_id
        self.node1_id = node1_id
        self.node2_id = node2_id
        self.congestion_rate = congestion_rate  # 0.0 to 1.0
        self.timestamp = timestamp or datetime.now().isoformat()
    
    @property
    def is_congested(self) -> bool:
        """Check if the path is congested (rate > 0.5)"""
        return self.congestion_rate > 0.5
