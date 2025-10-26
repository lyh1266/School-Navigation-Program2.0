"""
Main API handler for Indoor Navigation System
Cloud Functions for WeChat Mini Program
"""
import json
from typing import Dict, List, Any

# Import core modules
from ..core.path_finder import PathFinder, BuildingGraph, generate_navigation_instructions
from ..core.instruction_parser import InstructionParser
from ..core.congestion_processor import CongestionProcessor, classify_congestion
from ..core.model_matcher import ModelPathMatcher

# Import database operations
from ..db.operations import (
    NavigationGraphOperations, UserOperations,
    building_ops, node_ops, edge_ops, congestion_ops
)

# Initialize core components
instruction_parser = InstructionParser()
congestion_processor = CongestionProcessor()


def initialize_building_graph(building_id: str) -> BuildingGraph:
    """
    Initialize the building graph from the database
    
    Args:
        building_id: Building ID
        
    Returns:
        BuildingGraph instance
    """
    graph_data = NavigationGraphOperations.get_building_graph(building_id)
    
    graph = BuildingGraph()
    
    # Add nodes
    for node_data in graph_data['nodes']:
        node = graph.add_node(
            node_data['node_id'],
            node_data['x'],
            node_data['y'],
            node_data['floor_number']
        )
        
        # Add special locations (rooms, etc.)
        if node_data['node_type'] == 'room' and 'name' in node_data:
            graph.add_special_location(node_data['name'], node_data['node_id'])
    
    # Add edges
    for edge_data in graph_data['edges']:
        graph.add_edge(
            edge_data['node1_id'],
            edge_data['node2_id'],
            edge_data['distance']
        )
    
    return graph


def handle_navigation_request(event, context):
    """
    Handle navigation request from WeChat Mini Program
    
    Expected request format:
    {
        "user_id": "user123",
        "current_location": "1楼大厅",
        "destination": "3楼302教室",
        "building_id": "building123"
    }
    
    OR
    
    {
        "user_id": "user123",
        "voice_command": "去三楼302教室",
        "current_location": "1楼大厅",
        "building_id": "building123"
    }
    """
    try:
        # Parse request data
        data = json.loads(event['body'])
        user_id = data['user_id']
        building_id = data['building_id']
        current_location = data['current_location']
        
        # Process voice command if provided
        if 'voice_command' in data:
            parsed_command = instruction_parser.parse(data['voice_command'])
            if parsed_command['command_type'] == 'navigate' and parsed_command['destination']:
                destination = parsed_command['destination']
            else:
                return {
                    'statusCode': 400,
                    'body': json.dumps({
                        'error': '无法理解语音指令',
                        'parsed_command': parsed_command
                    })
                }
        else:
            destination = data['destination']
        
        # Initialize building graph
        graph = initialize_building_graph(building_id)
        
        # Get start and end nodes
        start_node = graph.get_node_by_location(current_location)
        end_node = graph.get_node_by_location(destination)
        
        if not start_node or not end_node:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': '无法找到起点或终点位置',
                    'start_found': start_node is not None,
                    'end_found': end_node is not None
                })
            }
        
        # Get congestion data
        congestion_data = NavigationGraphOperations.get_congestion_data(building_id)
        
        # Find path
        path_finder = PathFinder(graph)
        path = path_finder.find_path(start_node.id, end_node.id, congestion_data)
        
        if not path:
            return {
                'statusCode': 404,
                'body': json.dumps({
                    'error': '无法找到从起点到终点的路径'
                })
            }
        
        # Generate navigation instructions
        instructions = generate_navigation_instructions(path, graph)
        
        # Create model matcher for 3D visualization
        model_matcher = ModelPathMatcher()
        model_matcher.register_nodes_from_graph(graph.nodes)
        
        # Generate 3D path data
        path_3d = model_matcher.generate_smooth_path(path)
        path_segments = model_matcher.generate_path_segments(path)
        
        # Save navigation history
        UserOperations.add_navigation_history(user_id, start_node.id, end_node.id, path)
        
        # Prepare response
        response = {
            'path': path,
            'instructions': instructions,
            'path_3d': path_3d,
            'path_segments': path_segments,
            'estimated_time': len(path) * 10,  # Simple estimation: 10 seconds per node
            'congestion_info': {
                segment['start_node_id'] + '_' + segment['end_node_id']: 
                classify_congestion(congestion_data.get((segment['start_node_id'], segment['end_node_id']), 0))
                for segment in path_segments
            }
        }
        
        return {
            'statusCode': 200,
            'body': json.dumps(response)
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }


def handle_congestion_update(event, context):
    """
    Handle congestion data update from WeChat Mini Program
    
    Expected request format:
    {
        "user_id": "user123",
        "building_id": "building123",
        "accelerometer_data": [
            {
                "x": 0.1,
                "y": 0.2,
                "z": 9.8,
                "timestamp": 1602345678.123,
                "location_id": "path_node1_node2"
            },
            ...
        ]
    }
    """
    try:
        # Parse request data
        data = json.loads(event['body'])
        user_id = data['user_id']
        building_id = data['building_id']
        accelerometer_data = data['accelerometer_data']
        
        # Add user_id to each data point
        for point in accelerometer_data:
            point['user_id'] = user_id
        
        # Process accelerometer data
        congestion_rates = congestion_processor.process_accelerometer_batch(accelerometer_data)
        
        # Update congestion data in database
        for location_id, rate in congestion_rates.items():
            if location_id.startswith('path_'):
                # Extract node IDs from path_node1_node2 format
                parts = location_id.split('_')
                if len(parts) == 3:
                    node1_id = parts[1]
                    node2_id = parts[2]
                    
                    congestion_data = {
                        'node1_id': node1_id,
                        'node2_id': node2_id,
                        'congestion_rate': rate,
                        'building_id': building_id
                    }
                    
                    congestion_ops.create(congestion_data)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'success': True,
                'updated_locations': len(congestion_rates)
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }


def handle_user_settings(event, context):
    """
    Handle user settings update from WeChat Mini Program
    
    Expected request format:
    {
        "user_id": "user123",
        "settings": {
            "voice_volume": 80,
            "wake_word": "小导小导",
            "favorite_destinations": [
                {"node_id": "node123", "name": "我的教室"}
            ]
        }
    }
    """
    try:
        # Parse request data
        data = json.loads(event['body'])
        user_id = data['user_id']
        settings = data['settings']
        
        # Update user settings
        success = UserOperations.update_user_settings(user_id, settings)
        
        if success:
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'success': True
                })
            }
        else:
            return {
                'statusCode': 404,
                'body': json.dumps({
                    'error': '用户不存在'
                })
            }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }


def handle_favorite_destinations(event, context):
    """
    Handle favorite destinations operations from WeChat Mini Program
    
    Expected request format for adding:
    {
        "operation": "add",
        "user_id": "user123",
        "node_id": "node123",
        "name": "我的教室"
    }
    
    Expected request format for listing:
    {
        "operation": "list",
        "user_id": "user123"
    }
    """
    try:
        # Parse request data
        data = json.loads(event['body'])
        user_id = data['user_id']
        operation = data['operation']
        
        if operation == 'add':
            node_id = data['node_id']
            name = data['name']
            
            favorite_id = UserOperations.add_favorite_destination(user_id, node_id, name)
            
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'success': True,
                    'favorite_id': favorite_id
                })
            }
        
        elif operation == 'list':
            favorites = UserOperations.get_favorite_destinations(user_id)
            
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'favorites': [favorite.to_dict() for favorite in favorites]
                })
            }
        
        else:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': '不支持的操作'
                })
            }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }


def handle_navigation_history(event, context):
    """
    Handle navigation history listing from WeChat Mini Program
    
    Expected request format:
    {
        "user_id": "user123",
        "limit": 10
    }
    """
    try:
        # Parse request data
        data = json.loads(event['body'])
        user_id = data['user_id']
        limit = data.get('limit', 10)
        
        # Get navigation history
        history = UserOperations.get_navigation_history(user_id, limit)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'history': [entry.to_dict() for entry in history]
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }
