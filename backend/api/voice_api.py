"""
Voice API handler for Indoor Navigation System
Handles speech-to-text and text-to-speech operations
"""
import json
import base64
import requests
from typing import Dict, Any, Optional

# Configuration (would normally be in config.py)
VOICE_API_CONFIG = {
    'baidu': {
        'app_id': '7159323',
        'api_key': 'NpzaF6XRHvhFzxaxFBhIs0Ms',
        'secret_key': '61SbNvUHNXQ9NDt8HXmtqIriRCFUyqTZ',
        'stt_url': 'https://vop.baidu.com/server_api',
        'tts_url': 'https://tsn.baidu.com/text2audio'
    },
    'tencent': {
        'app_id': 'YOUR_TENCENT_APP_ID',
        'app_key': 'YOUR_TENCENT_APP_KEY',
        'stt_url': 'https://aai.qcloud.com/asr/v1/',
        'tts_url': 'https://tts.cloud.tencent.com/stream'
    }
}

# Default provider
DEFAULT_PROVIDER = 'baidu'


class VoiceAPIClient:
    """Base class for voice API clients"""
    def __init__(self, provider: str = DEFAULT_PROVIDER):
        self.provider = provider
        self.config = VOICE_API_CONFIG.get(provider, {})
    
    def speech_to_text(self, audio_data: bytes, format: str = 'wav', 
                       sample_rate: int = 16000) -> Dict[str, Any]:
        """
        Convert speech to text
        
        Args:
            audio_data: Binary audio data
            format: Audio format (wav, mp3, etc.)
            sample_rate: Audio sample rate in Hz
            
        Returns:
            Dictionary with recognition results
        """
        if self.provider == 'baidu':
            return self._baidu_speech_to_text(audio_data, format, sample_rate)
        elif self.provider == 'tencent':
            return self._tencent_speech_to_text(audio_data, format, sample_rate)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
    
    def text_to_speech(self, text: str, voice_id: str = '0', 
                       output_format: str = 'mp3') -> Optional[bytes]:
        """
        Convert text to speech
        
        Args:
            text: Text to convert to speech
            voice_id: Voice ID to use
            output_format: Output audio format
            
        Returns:
            Binary audio data or None if failed
        """
        if self.provider == 'baidu':
            return self._baidu_text_to_speech(text, voice_id, output_format)
        elif self.provider == 'tencent':
            return self._tencent_text_to_speech(text, voice_id, output_format)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
    
    def _baidu_speech_to_text(self, audio_data: bytes, format: str, 
                             sample_rate: int) -> Dict[str, Any]:
        """Baidu speech-to-text implementation"""
        try:
            # Get access token (simplified - in production, cache this token)
            token_url = f"https://aip.baidubce.com/oauth/2.0/token"
            token_params = {
                'grant_type': 'client_credentials',
                'client_id': self.config['api_key'],
                'client_secret': self.config['secret_key']
            }
            token_response = requests.post(token_url, params=token_params)
            token = token_response.json().get('access_token', '')
            
            if not token:
                return {'success': False, 'error': 'Failed to get access token'}
            
            # Prepare API request
            headers = {
                'Content-Type': 'application/json'
            }
            
            params = {
                'format': format,
                'rate': sample_rate,
                'channel': 1,
                'cuid': 'indoor_navigation_system',
                'token': token,
                'dev_pid': 1537  # Mandarin with punctuation
            }
            
            data = {
                'speech': base64.b64encode(audio_data).decode('utf-8'),
                'len': len(audio_data)
            }
            
            # Make API request
            response = requests.post(
                self.config['stt_url'], 
                params=params,
                headers=headers,
                json=data
            )
            
            result = response.json()
            
            if 'result' in result and result['result']:
                return {
                    'success': True,
                    'text': result['result'][0],
                    'raw_response': result
                }
            else:
                return {
                    'success': False,
                    'error': result.get('err_msg', 'Unknown error'),
                    'raw_response': result
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _tencent_speech_to_text(self, audio_data: bytes, format: str, 
                               sample_rate: int) -> Dict[str, Any]:
        """Tencent speech-to-text implementation"""
        try:
            # This is a simplified implementation
            # In production, you would need to handle authentication properly
            
            # Prepare API request
            headers = {
                'Content-Type': 'application/octet-stream',
                'Authorization': f"App {self.config['app_id']}"
            }
            
            params = {
                'engine_type': '16k_zh',
                'voice_format': 1 if format == 'wav' else 4,
                'speaker_diarization': 0,
                'hotword_id': 'indoor_navigation'
            }
            
            # Make API request
            response = requests.post(
                f"{self.config['stt_url']}{self.config['app_id']}",
                params=params,
                headers=headers,
                data=audio_data
            )
            
            result = response.json()
            
            if 'result' in result:
                return {
                    'success': True,
                    'text': result['result'],
                    'raw_response': result
                }
            else:
                return {
                    'success': False,
                    'error': result.get('message', 'Unknown error'),
                    'raw_response': result
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _baidu_text_to_speech(self, text: str, voice_id: str, 
                             output_format: str) -> Optional[bytes]:
        """Baidu text-to-speech implementation"""
        try:
            # Get access token (simplified - in production, cache this token)
            token_url = f"https://aip.baidubce.com/oauth/2.0/token"
            token_params = {
                'grant_type': 'client_credentials',
                'client_id': self.config['api_key'],
                'client_secret': self.config['secret_key']
            }
            token_response = requests.post(token_url, params=token_params)
            token = token_response.json().get('access_token', '')
            
            if not token:
                return None
            
            # Prepare API request
            params = {
                'tex': text,
                'tok': token,
                'cuid': 'indoor_navigation_system',
                'ctp': 1,
                'lan': 'zh',
                'spd': 5,  # Speed: 0-15, 5 is normal
                'pit': 5,  # Pitch: 0-15, 5 is normal
                'vol': 15,  # Volume: 0-15, 15 is max
                'per': int(voice_id),  # Voice: 0-female, 1-male, 3-male, 4-female
                'aue': 3 if output_format == 'mp3' else 6  # 3=mp3, 6=wav
            }
            
            # Make API request
            response = requests.get(self.config['tts_url'], params=params)
            
            # Check if response is audio data
            content_type = response.headers.get('Content-Type', '')
            if 'audio' in content_type:
                return response.content
            else:
                # Error response
                print(f"TTS Error: {response.text}")
                return None
                
        except Exception as e:
            print(f"TTS Exception: {str(e)}")
            return None
    
    def _tencent_text_to_speech(self, text: str, voice_id: str, 
                               output_format: str) -> Optional[bytes]:
        """Tencent text-to-speech implementation"""
        try:
            # This is a simplified implementation
            # In production, you would need to handle authentication properly
            
            # Prepare API request
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f"App {self.config['app_id']}"
            }
            
            data = {
                'text': text,
                'voice_type': int(voice_id),
                'speed': 0,  # -2 to 2, 0 is normal
                'volume': 0,  # -2 to 2, 0 is normal
                'sample_rate': 16000,
                'codec': 'mp3' if output_format == 'mp3' else 'pcm'
            }
            
            # Make API request
            response = requests.post(
                self.config['tts_url'],
                headers=headers,
                json=data
            )
            
            # Check if response is audio data
            content_type = response.headers.get('Content-Type', '')
            if 'audio' in content_type:
                return response.content
            else:
                # Error response
                print(f"TTS Error: {response.text}")
                return None
                
        except Exception as e:
            print(f"TTS Exception: {str(e)}")
            return None


def handle_speech_to_text(event, context):
    """
    Handle speech-to-text request from WeChat Mini Program
    
    Expected request format:
    {
        "audio_data": "base64_encoded_audio_data",
        "format": "wav",
        "sample_rate": 16000,
        "provider": "baidu"  // Optional
    }
    """
    try:
        # Parse request data
        data = json.loads(event['body'])
        audio_data = base64.b64decode(data['audio_data'])
        format = data.get('format', 'wav')
        sample_rate = data.get('sample_rate', 16000)
        provider = data.get('provider', DEFAULT_PROVIDER)
        
        # Initialize voice API client
        client = VoiceAPIClient(provider)
        
        # Convert speech to text
        result = client.speech_to_text(audio_data, format, sample_rate)
        
        if result['success']:
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'text': result['text']
                })
            }
        else:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': result['error']
                })
            }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }


def handle_text_to_speech(event, context):
    """
    Handle text-to-speech request from WeChat Mini Program
    
    Expected request format:
    {
        "text": "要转换为语音的文本",
        "voice_id": "0",  // Optional
        "output_format": "mp3",  // Optional
        "provider": "baidu"  // Optional
    }
    """
    try:
        # Parse request data
        data = json.loads(event['body'])
        text = data['text']
        voice_id = data.get('voice_id', '0')
        output_format = data.get('output_format', 'mp3')
        provider = data.get('provider', DEFAULT_PROVIDER)
        
        # Initialize voice API client
        client = VoiceAPIClient(provider)
        
        # Convert text to speech
        audio_data = client.text_to_speech(text, voice_id, output_format)
        
        if audio_data:
            # Return audio data as base64
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'audio_data': audio_base64,
                    'format': output_format
                })
            }
        else:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': '语音合成失败'
                })
            }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }


def handle_wake_word_detection(event, context):
    """
    Handle wake word detection request from WeChat Mini Program
    
    Expected request format:
    {
        "audio_data": "base64_encoded_audio_data",
        "wake_word": "小导小导",
        "confidence_threshold": 0.7  // Optional
    }
    
    Note: This is a simplified implementation that just checks if the
    speech-to-text result contains the wake word. In a production system,
    you would use a dedicated wake word detection service.
    """
    try:
        # Parse request data
        data = json.loads(event['body'])
        audio_data = base64.b64decode(data['audio_data'])
        wake_word = data['wake_word']
        confidence_threshold = data.get('confidence_threshold', 0.7)
        
        # Initialize voice API client
        client = VoiceAPIClient()
        
        # Convert speech to text
        result = client.speech_to_text(audio_data, 'wav', 16000)
        
        if result['success']:
            text = result['text'].lower()
            detected = wake_word.lower() in text
            
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'detected': detected,
                    'text': text,
                    'confidence': 0.9 if detected else 0.1  # Simplified confidence
                })
            }
        else:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': result['error'],
                    'detected': False
                })
            }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'detected': False
            })
        }
