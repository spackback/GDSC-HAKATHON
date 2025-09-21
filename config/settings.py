import os
from pathlib import Path

def load_config():
    """
    Loads and returns the enhanced application configuration with extended timing and MCP support.
    """
    # Base directory of the project
    BASE_DIR = Path(__file__).parent.parent

    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass  # python-dotenv is not required

    config = {
        # Gemini API Configuration
        'GEMINI_API_KEY': os.getenv('GEMINI_API_KEY', ''),
        'GEMINI_MODEL': os.getenv('GEMINI_MODEL', 'gemini-1.5-flash'),
        'GEMINI_TEMPERATURE': float(os.getenv('GEMINI_TEMPERATURE', '0.7')),
        'GEMINI_MAX_TOKENS': int(float(os.getenv('GEMINI_MAX_TOKENS', '2048'))),

        # Enhanced Action Timing Configuration
        'ACTION_TIMEOUT': int(os.getenv('ACTION_TIMEOUT', '60')),  # 60 seconds per action
        'MAX_EXECUTION_TIME': int(os.getenv('MAX_EXECUTION_TIME', '900')),  # 15 minutes total
        'ACTION_DELAY': float(os.getenv('ACTION_DELAY', '2.0')),  # Delay between actions
        'SCREEN_ANALYSIS_DELAY': float(os.getenv('SCREEN_ANALYSIS_DELAY', '3.0')),  # Screen update wait

        # MCP (Model Context Protocol) Configuration
        'ENABLE_MCP': os.getenv('ENABLE_MCP', 'true').lower() == 'true',
        'WORKSPACE_DIR': Path(os.getenv('WORKSPACE_DIR', str(BASE_DIR))),
        'MCP_TIMEOUT': int(os.getenv('MCP_TIMEOUT', '30')),  # MCP operation timeout

        # Voice Configuration
        'VOICE_ENGINE': os.getenv('VOICE_ENGINE', 'pyttsx3'),
        'TTS_RATE': int(float(os.getenv('TTS_RATE', '200'))),
        'TTS_VOLUME': float(os.getenv('TTS_VOLUME', '1.0')),
        'SPEECH_RECOGNITION_ENGINE': os.getenv('SPEECH_RECOGNITION_ENGINE', 'google_cloud'),
        'GCP_CREDENTIALS_PATH': os.getenv('GCP_CREDENTIALS_PATH', str(BASE_DIR / 'config' / 'swift-seeker-296907-0704a84f33f1.json')),

        # Wake Word Configuration
        'WAKE_WORD': os.getenv('WAKE_WORD', 'cherry'),
        'WAKE_WORD_SENSITIVITY': float(os.getenv('WAKE_WORD_SENSITIVITY', '0.5')),
        'WAKE_WORD_ENABLED': os.getenv('WAKE_WORD_ENABLED', 'true').lower() == 'true',
        'CONTINUOUS_LISTENING': os.getenv('CONTINUOUS_LISTENING', 'true').lower() == 'true',

        # GUI Configuration
        'GUI_THEME': os.getenv('GUI_THEME', 'modern'),
        'GUI_POSITION': os.getenv('GUI_POSITION', 'center'),
        'AUTO_HIDE_GUI': os.getenv('AUTO_HIDE_GUI', 'true').lower() == 'true',

        # Memory Configuration
        'MEMORY_TYPE': os.getenv('MEMORY_TYPE', 'chromadb'),
        'MEMORY_LIMIT': int(float(os.getenv('MEMORY_LIMIT', '1000'))),
        'CONTEXT_WINDOW': int(float(os.getenv('CONTEXT_WINDOW', '10'))),
        'MEMORY_DIR': Path(os.getenv('MEMORY_DIR', str(BASE_DIR / 'data' / 'memory'))),

        # Desktop Control - Enhanced Mouse Settings
        'SCREEN_CAPTURE_INTERVAL': float(os.getenv('SCREEN_CAPTURE_INTERVAL', '1.0')),
        'PYAUTOGUI_FAILSAFE': os.getenv('PYAUTOGUI_FAILSAFE', 'true').lower() == 'true',
        'MOUSE_MOVEMENT_SPEED': float(os.getenv('MOUSE_MOVEMENT_SPEED', '1.0')),
        'SMOOTH_MOUSE_MOVEMENT': os.getenv('SMOOTH_MOUSE_MOVEMENT', 'true').lower() == 'true',
        'MOUSE_CLICK_DELAY': float(os.getenv('MOUSE_CLICK_DELAY', '0.1')),
        'CURSOR_ACCURACY_THRESHOLD': int(os.getenv('CURSOR_ACCURACY_THRESHOLD', '5')),

        # Assets and Data
        'ASSETS_DIR': Path(os.getenv('ASSETS_DIR', str(BASE_DIR / 'data' / 'assets'))),
        'LOGS_DIR': Path(os.getenv('LOGS_DIR', str(BASE_DIR / 'data' / 'logs'))),

        # Logging
        'LOG_LEVEL': os.getenv('LOG_LEVEL', 'INFO'),
        'LOG_FILE': os.getenv('LOG_FILE', 'data/logs/cherry.log'),
        'MAX_LOG_FILES': int(float(os.getenv('MAX_LOG_FILES', '5'))),

        # Features (true/false)
        'ENABLE_WEB_SEARCH': os.getenv('ENABLE_WEB_SEARCH', 'true').lower() == 'true',
        'ENABLE_FILE_OPERATIONS': os.getenv('ENABLE_FILE_OPERATIONS', 'true').lower() == 'true',
        'ENABLE_SCREEN_ANALYSIS': os.getenv('ENABLE_SCREEN_ANALYSIS', 'true').lower() == 'true',
        'ENABLE_SYSTEM_CONTROL': os.getenv('ENABLE_SYSTEM_CONTROL', 'true').lower() == 'true',
    }

    # Ensure directories exist
    config['MEMORY_DIR'].mkdir(parents=True, exist_ok=True)
    config['ASSETS_DIR'].mkdir(parents=True, exist_ok=True)
    config['LOGS_DIR'].mkdir(parents=True, exist_ok=True)
    config['WORKSPACE_DIR'].mkdir(parents=True, exist_ok=True)

    return config