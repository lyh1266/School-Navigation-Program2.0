"""
Configuration settings for Indoor Navigation System
"""
import os

# API Configuration
VOICE_API_CONFIG = {
    'baidu': {
        'app_id': os.environ.get('BAIDU_APP_ID', 'YOUR_BAIDU_APP_ID'),
        'api_key': os.environ.get('BAIDU_API_KEY', 'YOUR_BAIDU_API_KEY'),
        'secret_key': os.environ.get('BAIDU_SECRET_KEY', 'YOUR_BAIDU_SECRET_KEY'),
        'stt_url': 'https://vop.baidu.com/server_api',
        'tts_url': 'https://tsn.baidu.com/text2audio'
    },
    'tencent': {
        'app_id': os.environ.get('TENCENT_APP_ID', 'YOUR_TENCENT_APP_ID'),
        'app_key': os.environ.get('TENCENT_APP_KEY', 'YOUR_TENCENT_APP_KEY'),
        'stt_url': 'https://aai.qcloud.com/asr/v1/',
        'tts_url': 'https://tts.cloud.tencent.com/stream'
    }
}

# Default voice API provider
DEFAULT_VOICE_PROVIDER = os.environ.get('DEFAULT_VOICE_PROVIDER', 'baidu')

# Database Configuration
DB_CONFIG = {
    'cloud_env': os.environ.get('CLOUD_ENV', 'your-cloud-env-id')
}

# Building Configuration
DEFAULT_BUILDING_ID = os.environ.get('BUILDING_ID', 'building123')

# Path Finding Configuration
PATH_FINDING_CONFIG = {
    'floor_height': 5.0,  # Height of each floor in meters
    'congestion_weight': 2.0,  # Weight factor for congestion in path finding
    'stair_penalty': 10.0,  # Penalty for using stairs (to prefer same floor when possible)
    'elevator_penalty': 5.0  # Penalty for using elevators
}

# Congestion Configuration
CONGESTION_CONFIG = {
    'data_expiry_time': 300,  # Time in seconds after which congestion data is considered expired
    'step_threshold': 1.2,  # Magnitude threshold for step detection
    'step_cooldown': 0.5,  # Minimum time (seconds) between steps
    'max_users_per_area': 20,  # Maximum number of users in an area for congestion calculation
    'upload_batch_size': 50,  # Number of data points to batch before uploading
    'upload_interval': 10  # Minimum time (seconds) between uploads
}

# 3D Model Configuration
MODEL_CONFIG = {
    'model_scale': 1.0,  # Scale factor to convert navigation coordinates to model coordinates
    'points_per_segment': 5  # Number of points to generate between each pair of nodes for smooth path
}
