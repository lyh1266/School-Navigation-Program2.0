"""
Congestion Processor for Indoor Navigation
Processes accelerometer data to determine congestion levels
"""
import time
from typing import Dict, List, Tuple, Any
import numpy as np
from datetime import datetime, timedelta


class AccelerometerData:
    """Class to represent accelerometer data from user's device"""
    def __init__(self, x: float, y: float, z: float, timestamp: float, user_id: str, location_id: str):
        self.x = x
        self.y = y
        self.z = z
        self.timestamp = timestamp
        self.user_id = user_id
        self.location_id = location_id
    
    @property
    def magnitude(self) -> float:
        """Calculate the magnitude of acceleration"""
        return (self.x**2 + self.y**2 + self.z**2)**0.5


class CongestionProcessor:
    """
    Processes accelerometer data to determine congestion levels
    Uses step pattern detection and user density to estimate congestion
    """
    def __init__(self, expiry_time: int = 300):
        """
        Initialize the congestion processor
        
        Args:
            expiry_time: Time in seconds after which data is considered expired
        """
        self.data_cache: Dict[str, List[AccelerometerData]] = {}  # location_id -> list of data points
        self.congestion_cache: Dict[str, Tuple[float, float]] = {}  # location_id -> (congestion_rate, timestamp)
        self.expiry_time = expiry_time
        
        # Thresholds for step detection
        self.step_threshold = 1.2  # Magnitude threshold for step detection
        self.step_cooldown = 0.5   # Minimum time (seconds) between steps
    
    def add_data_point(self, data: AccelerometerData) -> None:
        """Add a new accelerometer data point to the cache"""
        location_id = data.location_id
        if location_id not in self.data_cache:
            self.data_cache[location_id] = []
        
        self.data_cache[location_id].append(data)
        
        # Clean up old data
        self._clean_expired_data(location_id)
    
    def _clean_expired_data(self, location_id: str) -> None:
        """Remove expired data points for a location"""
        if location_id not in self.data_cache:
            return
        
        current_time = time.time()
        self.data_cache[location_id] = [
            data for data in self.data_cache[location_id]
            if current_time - data.timestamp < self.expiry_time
        ]
    
    def calculate_congestion(self, location_id: str) -> float:
        """
        Calculate congestion rate for a location
        
        Args:
            location_id: ID of the location to calculate congestion for
            
        Returns:
            Congestion rate between 0.0 and 1.0
            0.0 means no congestion, 1.0 means maximum congestion
        """
        # Check if we have cached congestion data that's still valid
        if location_id in self.congestion_cache:
            congestion_rate, timestamp = self.congestion_cache[location_id]
            if time.time() - timestamp < 60:  # Cache for 1 minute
                return congestion_rate
        
        # Clean up expired data
        self._clean_expired_data(location_id)
        
        # If no data for this location, assume no congestion
        if location_id not in self.data_cache or not self.data_cache[location_id]:
            return 0.0
        
        # Get data for this location
        location_data = self.data_cache[location_id]
        
        # Calculate congestion based on:
        # 1. Number of unique users in the area
        # 2. Average walking speed (steps per minute)
        # 3. Variance in acceleration (indicates stop-and-go movement)
        
        # Count unique users
        unique_users = len(set(data.user_id for data in location_data))
        
        # Calculate average walking speed for each user
        user_speeds = {}
        for user_id in set(data.user_id for data in location_data):
            user_data = [data for data in location_data if data.user_id == user_id]
            user_data.sort(key=lambda x: x.timestamp)
            
            # Detect steps using peaks in acceleration magnitude
            steps = 0
            last_step_time = 0
            for data in user_data:
                if (data.magnitude > self.step_threshold and 
                    data.timestamp - last_step_time > self.step_cooldown):
                    steps += 1
                    last_step_time = data.timestamp
            
            # Calculate time span in minutes
            time_span = (user_data[-1].timestamp - user_data[0].timestamp) / 60
            if time_span > 0:
                steps_per_minute = steps / time_span
                user_speeds[user_id] = steps_per_minute
        
        # Calculate average speed across users
        if user_speeds:
            avg_speed = sum(user_speeds.values()) / len(user_speeds)
        else:
            avg_speed = 0
        
        # Normal walking speed is around 100 steps per minute
        # Slower speeds indicate congestion
        speed_factor = max(0, min(1, 1 - (avg_speed / 100)))
        
        # Calculate acceleration variance (high variance indicates stop-and-go)
        magnitudes = [data.magnitude for data in location_data]
        if len(magnitudes) > 1:
            variance = np.var(magnitudes)
            # Normalize variance to 0-1 range (empirical values)
            variance_factor = min(1, variance / 5)
        else:
            variance_factor = 0
        
        # User density factor (assuming max 20 users in an area is crowded)
        density_factor = min(1, unique_users / 20)
        
        # Combine factors with weights
        congestion_rate = (
            0.5 * speed_factor +
            0.3 * variance_factor +
            0.2 * density_factor
        )
        
        # Cache the result
        self.congestion_cache[location_id] = (congestion_rate, time.time())
        
        return congestion_rate
    
    def get_all_congestion_rates(self) -> Dict[str, float]:
        """Get congestion rates for all locations with recent data"""
        result = {}
        for location_id in list(self.data_cache.keys()):
            self._clean_expired_data(location_id)
            if self.data_cache[location_id]:  # If there's still data after cleaning
                result[location_id] = self.calculate_congestion(location_id)
        return result
    
    def get_congestion_between_nodes(self, node1_id: str, node2_id: str) -> float:
        """
        Get congestion rate for a path between two nodes
        
        Args:
            node1_id: ID of the first node
            node2_id: ID of the second node
            
        Returns:
            Congestion rate between 0.0 and 1.0
        """
        # Create a path ID that's consistent regardless of order
        path_id = f"path_{min(node1_id, node2_id)}_{max(node1_id, node2_id)}"
        return self.calculate_congestion(path_id)
    
    def process_accelerometer_batch(self, batch_data: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Process a batch of accelerometer data from multiple users
        
        Args:
            batch_data: List of dictionaries with accelerometer data
                Each dict should have: x, y, z, timestamp, user_id, location_id
                
        Returns:
            Dictionary mapping location_ids to congestion rates
        """
        for data_point in batch_data:
            accel_data = AccelerometerData(
                x=data_point['x'],
                y=data_point['y'],
                z=data_point['z'],
                timestamp=data_point['timestamp'],
                user_id=data_point['user_id'],
                location_id=data_point['location_id']
            )
            self.add_data_point(accel_data)
        
        # Return updated congestion rates
        return self.get_all_congestion_rates()


def classify_congestion(rate: float) -> str:
    """
    Classify congestion rate into human-readable description
    
    Args:
        rate: Congestion rate between 0.0 and 1.0
        
    Returns:
        String description of congestion level
    """
    if rate < 0.2:
        return "通畅"
    elif rate < 0.4:
        return "轻微拥堵"
    elif rate < 0.6:
        return "中度拥堵"
    elif rate < 0.8:
        return "拥堵"
    else:
        return "严重拥堵"
