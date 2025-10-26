"""
Instruction Parser for Indoor Navigation
Processes user voice commands and extracts destination information
"""
import re
from typing import Dict, Optional, Tuple


class InstructionParser:
    """
    Parser for user navigation instructions
    Converts natural language instructions to structured commands
    """
    def __init__(self):
        # Dictionary of common location patterns and their standardized names
        self.location_patterns = {
            r'(一|1)楼': '1楼',
            r'(二|2)楼': '2楼',
            r'(三|3)楼': '3楼',
            r'(四|4)楼': '4楼',
            r'(五|5)楼': '5楼',
            r'(六|6)楼': '6楼',
            r'大厅': '大厅',
            r'(实验室|试验室)': '实验室',
            r'(办公室|办公区)': '办公室',
            r'(教室|课室)': '教室',
            r'(洗手间|卫生间|厕所)': '洗手间',
            r'(楼梯|阶梯)': '楼梯',
            r'电梯': '电梯',
            r'出口': '出口',
            r'入口': '入口',
        }
        
        # Patterns for room numbers
        self.room_number_pattern = r'(\d{3,4})(室|房间|教室)?'
        
        # Command patterns
        self.go_to_patterns = [
            r'(去|到|前往|带我去|带我到|去往|导航到|导航去|带路到|带路去)',
            r'(怎么走|怎么去|如何去|如何到达)',
            r'(找|寻找|查找)'
        ]
        
    def parse(self, text: str) -> Dict[str, str]:
        """
        Parse user instruction text
        
        Args:
            text: User instruction text (from STT)
            
        Returns:
            Dictionary with parsed information:
            {
                'command_type': 'navigate', 'search', etc.
                'destination': Destination location (if found)
                'floor': Floor number (if found)
                'room_number': Room number (if found)
            }
        """
        result = {
            'command_type': None,
            'destination': None,
            'floor': None,
            'room_number': None
        }
        
        # Normalize text
        text = text.lower().strip()
        
        # Determine command type
        if any(re.search(pattern, text) for pattern in self.go_to_patterns):
            result['command_type'] = 'navigate'
        elif '在哪' in text or '在哪里' in text or '位置' in text:
            result['command_type'] = 'search'
        else:
            result['command_type'] = 'unknown'
        
        # Extract floor information
        floor = self._extract_floor(text)
        if floor:
            result['floor'] = floor
        
        # Extract room number
        room_match = re.search(self.room_number_pattern, text)
        if room_match:
            result['room_number'] = room_match.group(1)
        
        # Extract destination type
        for pattern, location_type in self.location_patterns.items():
            if re.search(pattern, text):
                result['destination'] = location_type
                break
        
        # Combine floor and room number if both exist
        if result['floor'] and result['room_number']:
            result['destination'] = f"{result['floor']}{result['room_number']}教室"
        elif result['floor'] and result['destination'] and result['destination'] not in ['楼梯', '电梯', '出口', '入口']:
            result['destination'] = f"{result['floor']}{result['destination']}"
        
        return result
    
    def _extract_floor(self, text: str) -> Optional[str]:
        """Extract floor number from text"""
        # Check for Chinese numerals or Arabic numerals followed by floor indicator
        floor_match = re.search(r'(一|二|三|四|五|六|七|八|九|十|1|2|3|4|5|6|7|8|9|10)\s*(层|楼)', text)
        if floor_match:
            # Convert Chinese numerals to Arabic if needed
            numeral = floor_match.group(1)
            numeral_map = {
                '一': '1', '二': '2', '三': '3', '四': '4', '五': '5',
                '六': '6', '七': '7', '八': '8', '九': '9', '十': '10'
            }
            floor_num = numeral_map.get(numeral, numeral)
            return f"{floor_num}楼"
        return None
    
    def standardize_location(self, location_text: str) -> str:
        """
        Convert various location descriptions to standard format
        E.g., "3楼302" -> "3楼302教室"
        """
        if not location_text:
            return None
        
        # Extract floor and room number if present
        floor = self._extract_floor(location_text)
        room_match = re.search(self.room_number_pattern, location_text)
        
        if floor and room_match:
            room_number = room_match.group(1)
            # Check if the room number already includes the floor number
            if room_number.startswith(floor[0]):
                return f"{floor}{room_number[1:]}教室"
            return f"{floor}{room_number}教室"
        
        # If only floor is specified
        if floor:
            for pattern, location_type in self.location_patterns.items():
                if re.search(pattern, location_text) and location_type not in ['楼梯', '电梯', '出口', '入口']:
                    return f"{floor}{location_type}"
            return f"{floor}大厅"  # Default to floor lobby if no specific location
        
        return location_text  # Return as is if we can't standardize
