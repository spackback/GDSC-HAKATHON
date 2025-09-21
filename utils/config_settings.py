"""
Configuration settings for Cherry AI Assistant
"""

import os
from pathlib import Path
from dotenv import load_dotenv

def load_config():
    """Load configuration from environment variables and defaults"""

    # Load environment variables from .env file
    env_path = Path(__file__).parent.parent / '.env'
    load_dotenv(env_path)

    config = {
        # Gemini API Configuration
        'GEMINI_API_KEY': os.getenv('GEMINI_API_KEY', ''),
        'GEMINI_MODEL': os.getenv('GEMINI_MODEL', 'gemini-1.5-flash'),
        'GEMINI_TEMPERATURE': float(os.getenv('GEMINI_TEMPERATURE', '0.7')),
        'GEMINI_MAX_TOKENS': int(os.getenv('GEMINI_MAX_TOKENS', '2048')),

        # Voice Configuration
        'VOICE_ENGINE': os.getenv('VOICE_ENGINE', 'pyttsx3'),  # pyttsx3 or gtts
        'TTS_RATE': int(os.getenv('TTS_RATE', '200')),
        'TTS_VOLUME': float(os.getenv('TTS_VOLUME', '1.0')),
        'SPEECH_RECOGNITION_ENGINE': os.getenv('SPEECH_RECOGNITION_ENGINE', 'whisper'),  # whisper, vosk, or google

        # Wake Word Configuration
        'WAKE_WORD': os.getenv('WAKE_WORD', 'cherry'),
        'WAKE_WORD_SENSITIVITY': float(os.getenv('WAKE_WORD_SENSITIVITY', '0.5')),
        'CONTINUOUS_LISTENING': os.getenv('CONTINUOUS_LISTENING', 'true').lower() == 'true',

        # GUI Configuration
        'GUI_THEME': os.getenv('GUI_THEME', 'modern'),
        'GUI_POSITION': os.getenv('GUI_POSITION', 'center'),  # center, top-right, etc.
        'AUTO_HIDE_GUI': os.getenv('AUTO_HIDE_GUI', 'true').lower() == 'true',

        # Memory Configuration
        'MEMORY_TYPE': os.getenv('MEMORY_TYPE', 'chromadb'),  # chromadb, faiss
        'MEMORY_LIMIT': int(os.getenv('MEMORY_LIMIT', '1000')),  # Number of conversations to remember
        'CONTEXT_WINDOW': int(os.getenv('CONTEXT_WINDOW', '10')),  # Number of recent interactions

        # Desktop Control Configuration
        'SCREEN_CAPTURE_INTERVAL': float(os.getenv('SCREEN_CAPTURE_INTERVAL', '1.0')),
        'PYAUTOGUI_FAILSAFE': os.getenv('PYAUTOGUI_FAILSAFE', 'true').lower() == 'true',
        'MOUSE_MOVEMENT_SPEED': float(os.getenv('MOUSE_MOVEMENT_SPEED', '1.0')),

        # Logging Configuration
        'LOG_LEVEL': os.getenv('LOG_LEVEL', 'INFO'),
        'LOG_FILE': os.getenv('LOG_FILE', 'data/logs/cherry.log'),
        'MAX_LOG_FILES': int(os.getenv('MAX_LOG_FILES', '5')),

        # Application Paths
        'DATA_DIR': Path(__file__).parent.parent / 'data',
        'MEMORY_DIR': Path(__file__).parent.parent / 'data' / 'memory',
        'CACHE_DIR': Path(__file__).parent.parent / 'data' / 'cache',
        'LOGS_DIR': Path(__file__).parent.parent / 'data' / 'logs',
        'ASSETS_DIR': Path(__file__).parent.parent / 'data' / 'assets',

        # Feature Flags
        'ENABLE_WEB_SEARCH': os.getenv('ENABLE_WEB_SEARCH', 'true').lower() == 'true',
        'ENABLE_FILE_OPERATIONS': os.getenv('ENABLE_FILE_OPERATIONS', 'true').lower() == 'true',
        'ENABLE_SCREEN_ANALYSIS': os.getenv('ENABLE_SCREEN_ANALYSIS', 'true').lower() == 'true',
        'ENABLE_SYSTEM_CONTROL': os.getenv('ENABLE_SYSTEM_CONTROL', 'true').lower() == 'true',
    }

    # Validate required configuration
    if not config['GEMINI_API_KEY']:
        raise ValueError("GEMINI_API_KEY is required. Please set it in your .env file.")

    # Create necessary directories
    for dir_key in ['DATA_DIR', 'MEMORY_DIR', 'CACHE_DIR', 'LOGS_DIR', 'ASSETS_DIR']:
        config[dir_key].mkdir(parents=True, exist_ok=True)

    return config

# Default hotkey mappings
DEFAULT_HOTKEYS = {
    'activate_cherry': '<ctrl>+<alt>+c',
    'quit_application': '<ctrl>+<alt>+q',
    'toggle_listening': '<ctrl>+<alt>+l',
    'screenshot_analyze': '<ctrl>+<alt>+s',
}

# Default voice commands
DEFAULT_VOICE_COMMANDS = {
    'screenshot': ['take a screenshot', 'capture screen', 'screenshot'],
    'web_search': ['search for', 'look up', 'find information about'],
    'file_create': ['create file', 'make document', 'new file'],
    'system_info': ['system information', 'computer status', 'system stats'],
    'help': ['help', 'what can you do', 'commands'],
}
