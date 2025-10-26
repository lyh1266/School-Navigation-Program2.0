"""
Database operations for Indoor Navigation System
Uses cloud database for WeChat Mini Program
"""
import json
import uuid
from typing import Dict, List, Any, Optional, Type, TypeVar, Generic
from datetime import datetime

# Import models
from .models import (
    BaseModel, Building, Floor, Room, NavigationNode, NavigationEdge,
    User, NavigationHistory, FavoriteDestination, CongestionData
)

# Type variable for generic operations
T = TypeVar('T', bound=BaseModel)


class CloudDBOperations(Generic[T]):
    """
    Generic operations for cloud database
    Handles CRUD operations for any model type
    """
    def __init__(self, model_class: Type[T], collection_name: str):
        self.model_class = model_class
        self.collection_name = collection_name
    
    def create(self, data: Dict[str, Any]) -> str:
        """
        Create a new document in the collection
        
        Args:
            data: Dictionary with model data
            
        Returns:
            ID of the created document
        """
        # In a real implementation, this would call the cloud database API
        # For now, we'll simulate the behavior
        
        # Generate ID if not provided
        if '_id' not in data:
            data['_id'] = str(uuid.uuid4())
        
        # Add timestamps
        now = datetime.now().isoformat()
        data['created_at'] = now
        data['updated_at'] = now
        
        print(f"[CloudDB] Created {self.collection_name}: {data['_id']}")
        return data['_id']
    
    def get(self, doc_id: str) -> Optional[T]:
        """
        Get a document by ID
        
        Args:
            doc_id: Document ID
            
        Returns:
            Model instance or None if not found
        """
        # In a real implementation, this would call the cloud database API
        # For now, we'll simulate the behavior
        print(f"[CloudDB] Get {self.collection_name}: {doc_id}")
        
        # This would normally fetch from the database
        # Return None to simulate not found
        return None
    
    def update(self, doc_id: str, data: Dict[str, Any]) -> bool:
        """
        Update a document by ID
        
        Args:
            doc_id: Document ID
            data: Dictionary with fields to update
            
        Returns:
            True if successful, False otherwise
        """
        # In a real implementation, this would call the cloud database API
        # For now, we'll simulate the behavior
        
        # Update timestamp
        data['updated_at'] = datetime.now().isoformat()
        
        print(f"[CloudDB] Updated {self.collection_name}: {doc_id}")
        return True
    
    def delete(self, doc_id: str) -> bool:
        """
        Delete a document by ID
        
        Args:
            doc_id: Document ID
            
        Returns:
            True if successful, False otherwise
        """
        # In a real implementation, this would call the cloud database API
        # For now, we'll simulate the behavior
        print(f"[CloudDB] Deleted {self.collection_name}: {doc_id}")
        return True
    
    def query(self, query: Dict[str, Any], limit: int = 100) -> List[T]:
        """
        Query documents in the collection
        
        Args:
            query: Query dictionary
            limit: Maximum number of results
            
        Returns:
            List of model instances
        """
        # In a real implementation, this would call the cloud database API
        # For now, we'll simulate the behavior
        print(f"[CloudDB] Query {self.collection_name}: {query}")
        
        # This would normally query the database
        # Return empty list to simulate no results
        return []


# Create operations instances for each model
building_ops = CloudDBOperations(Building, 'buildings')
floor_ops = CloudDBOperations(Floor, 'floors')
room_ops = CloudDBOperations(Room, 'rooms')
node_ops = CloudDBOperations(NavigationNode, 'navigation_nodes')
edge_ops = CloudDBOperations(NavigationEdge, 'navigation_edges')
user_ops = CloudDBOperations(User, 'users')
history_ops = CloudDBOperations(NavigationHistory, 'navigation_history')
favorite_ops = CloudDBOperations(FavoriteDestination, 'favorite_destinations')
congestion_ops = CloudDBOperations(CongestionData, 'congestion_data')


class NavigationGraphOperations:
    """Operations for the navigation graph"""
    @staticmethod
    def get_building_graph(building_id: str) -> Dict[str, Any]:
        """
        Get the complete navigation graph for a building
        
        Args:
            building_id: Building ID
            
        Returns:
            Dictionary with nodes and edges
        """
        # Query all nodes for the building
        nodes = node_ops.query({'building_id': building_id})
        
        # Query all edges for the building's nodes
        node_ids = [node.node_id for node in nodes]
        edges = []
        
        # In a real implementation, we would query the database
        # For now, we'll return an empty graph
        
        return {
            'nodes': [node.to_dict() for node in nodes],
            'edges': [edge.to_dict() for edge in edges]
        }
    
    @staticmethod
    def get_congestion_data(building_id: str) -> Dict[str, float]:
        """
        Get current congestion data for a building
        
        Args:
            building_id: Building ID
            
        Returns:
            Dictionary mapping edge IDs to congestion rates
        """
        # Query recent congestion data
        # In a real implementation, we would query the database
        
        # For now, return empty congestion data
        return {}


class UserOperations:
    """Operations for user data"""
    @staticmethod
    def get_or_create_user(open_id: str) -> User:
        """
        Get a user by OpenID or create if not exists
        
        Args:
            open_id: WeChat OpenID
            
        Returns:
            User instance
        """
        # Query user by OpenID
        users = user_ops.query({'open_id': open_id})
        
        if users:
            return users[0]
        
        # Create new user
        user = User(user_id=str(uuid.uuid4()), open_id=open_id)
        user_ops.create(user.to_dict())
        return user
    
    @staticmethod
    def add_navigation_history(user_id: str, start_node_id: str, 
                               end_node_id: str, path: List[str]) -> str:
        """
        Add a navigation history entry for a user
        
        Args:
            user_id: User ID
            start_node_id: Starting node ID
            end_node_id: Destination node ID
            path: List of node IDs in the path
            
        Returns:
            History entry ID
        """
        history = NavigationHistory(
            history_id=str(uuid.uuid4()),
            user_id=user_id,
            start_node_id=start_node_id,
            end_node_id=end_node_id,
            start_time=datetime.now().isoformat(),
            path=path
        )
        
        return history_ops.create(history.to_dict())
    
    @staticmethod
    def get_navigation_history(user_id: str, limit: int = 10) -> List[NavigationHistory]:
        """
        Get navigation history for a user
        
        Args:
            user_id: User ID
            limit: Maximum number of entries
            
        Returns:
            List of navigation history entries
        """
        return history_ops.query({'user_id': user_id}, limit=limit)
    
    @staticmethod
    def add_favorite_destination(user_id: str, node_id: str, name: str) -> str:
        """
        Add a favorite destination for a user
        
        Args:
            user_id: User ID
            node_id: Node ID
            name: Custom name for the destination
            
        Returns:
            Favorite entry ID
        """
        favorite = FavoriteDestination(
            favorite_id=str(uuid.uuid4()),
            user_id=user_id,
            node_id=node_id,
            name=name
        )
        
        return favorite_ops.create(favorite.to_dict())
    
    @staticmethod
    def get_favorite_destinations(user_id: str) -> List[FavoriteDestination]:
        """
        Get favorite destinations for a user
        
        Args:
            user_id: User ID
            
        Returns:
            List of favorite destinations
        """
        return favorite_ops.query({'user_id': user_id})
    
    @staticmethod
    def update_user_settings(user_id: str, settings: Dict[str, Any]) -> bool:
        """
        Update user settings
        
        Args:
            user_id: User ID
            settings: Dictionary with settings to update
            
        Returns:
            True if successful, False otherwise
        """
        user = user_ops.get(user_id)
        if not user:
            return False
        
        user.update_settings(settings)
        return user_ops.update(user_id, {'settings': user.settings})
