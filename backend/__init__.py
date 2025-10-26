"""
Indoor Navigation System Backend
"""
import os
import sys

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import core modules
from .core.path_finder import PathFinder, BuildingGraph
from .core.instruction_parser import InstructionParser
from .core.congestion_processor import CongestionProcessor
from .core.model_matcher import ModelPathMatcher

# Import database operations
from .db.operations import (
    NavigationGraphOperations, UserOperations,
    building_ops, node_ops, edge_ops, congestion_ops
)

# Import API handlers
from .api.main import (
    handle_navigation_request, handle_congestion_update,
    handle_user_settings, handle_favorite_destinations,
    handle_navigation_history
)

from .api.voice_api import (
    handle_speech_to_text, handle_text_to_speech,
    handle_wake_word_detection
)

# Import configuration
from .config import (
    VOICE_API_CONFIG, DEFAULT_VOICE_PROVIDER,
    DB_CONFIG, DEFAULT_BUILDING_ID,
    PATH_FINDING_CONFIG, CONGESTION_CONFIG,
    MODEL_CONFIG
)
