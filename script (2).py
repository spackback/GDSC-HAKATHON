# Create the main project structure and core files for Cherry AI Assistant

project_structure = """
cherry_ai_assistant/
├── README.md
├── requirements.txt
├── .env.example
├── config/
│   ├── __init__.py
│   ├── settings.py
│   └── gemini_config.py
├── core/
│   ├── __init__.py
│   ├── cherry_brain.py       # Main AI brain with Gemini integration
│   ├── memory_manager.py     # RAG and context management
│   ├── voice_processor.py    # Speech recognition and TTS
│   ├── vision_system.py      # Screen capture and computer vision
│   ├── desktop_controller.py # Mouse, keyboard automation
│   └── wake_word_detector.py # Voice activation system
├── interface/
│   ├── __init__.py
│   ├── gui_manager.py        # Tkinter popup interface
│   ├── system_tray.py        # Background service management
│   └── hotkey_manager.py     # Global hotkey detection
├── utils/
│   ├── __init__.py
│   ├── file_handler.py       # File operations
│   ├── web_scraper.py        # Web information retrieval
│   ├── logger.py             # Logging utilities
│   └── helpers.py            # General helper functions
├── data/
│   ├── memory/               # Vector database storage
│   ├── cache/                # Temporary files and cache
│   ├── logs/                 # Application logs
│   └── assets/               # Icons, sounds, etc.
└── main.py                   # Application entry point
"""

print("Cherry AI Assistant Project Structure:")
print(project_structure)

# Create main.py - The entry point
main_py_content = '''#!/usr/bin/env python3
"""
Cherry AI Desktop Assistant
Main application entry point
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config.settings import load_config
from core.cherry_brain import CherryBrain
from interface.system_tray import SystemTrayManager
from interface.gui_manager import GUIManager
from interface.hotkey_manager import HotkeyManager
from utils.logger import setup_logging

class CherryAssistant:
    """Main Cherry AI Assistant application"""
    
    def __init__(self):
        self.config = load_config()
        self.logger = setup_logging()
        
        # Core components
        self.brain = None
        self.gui_manager = None
        self.tray_manager = None
        self.hotkey_manager = None
        
        self.is_running = False
        
    async def initialize(self):
        """Initialize all components"""
        try:
            self.logger.info("Initializing Cherry AI Assistant...")
            
            # Initialize AI brain
            self.brain = CherryBrain(self.config)
            await self.brain.initialize()
            
            # Initialize GUI manager
            self.gui_manager = GUIManager(self.brain, self.config)
            
            # Initialize system tray
            self.tray_manager = SystemTrayManager(
                self.show_gui, 
                self.quit_application,
                self.config
            )
            
            # Initialize hotkey manager
            self.hotkey_manager = HotkeyManager(self.config)
            self.hotkey_manager.register_hotkeys({
                '<ctrl>+<alt>+c': self.show_gui,
                '<ctrl>+<alt>+q': self.quit_application
            })
            
            self.logger.info("Cherry AI Assistant initialized successfully!")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Cherry: {e}")
            return False
    
    def show_gui(self):
        """Show the Cherry GUI interface"""
        if self.gui_manager:
            self.gui_manager.show()
    
    def quit_application(self):
        """Gracefully shutdown the application"""
        self.logger.info("Shutting down Cherry AI Assistant...")
        self.is_running = False
        
        if self.hotkey_manager:
            self.hotkey_manager.stop()
        if self.tray_manager:
            self.tray_manager.stop()
        if self.gui_manager:
            self.gui_manager.destroy()
        if self.brain:
            asyncio.create_task(self.brain.cleanup())
    
    async def run(self):
        """Main application loop"""
        if not await self.initialize():
            return
        
        self.is_running = True
        self.logger.info("Cherry AI Assistant is now running in the background...")
        
        # Start system tray in separate thread
        self.tray_manager.start()
        
        # Main event loop
        try:
            while self.is_running:
                await asyncio.sleep(0.1)  # Small delay to prevent high CPU usage
                
        except KeyboardInterrupt:
            self.logger.info("Received interrupt signal")
        finally:
            self.quit_application()

def main():
    """Application entry point"""
    print("🍒 Starting Cherry AI Desktop Assistant...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required")
        sys.exit(1)
    
    # Check if running as admin (Windows)
    if os.name == 'nt':
        try:
            import ctypes
            is_admin = ctypes.windll.shell32.IsUserAnAdmin()
            if not is_admin:
                print("Warning: Running without administrator privileges")
                print("Some features may not work properly")
        except:
            pass
    
    # Create and run the assistant
    cherry = CherryAssistant()
    
    try:
        # Run the async main loop
        if sys.platform.startswith('win'):
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        asyncio.run(cherry.run())
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
'''

# Create settings.py
settings_py_content = '''"""
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
'''

# Create .env.example
env_example_content = '''# Cherry AI Desktop Assistant Configuration
# Copy this file to .env and fill in your API keys and preferences

# Gemini AI Configuration
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-1.5-flash
GEMINI_TEMPERATURE=0.7
GEMINI_MAX_TOKENS=2048

# Voice Configuration
VOICE_ENGINE=pyttsx3
TTS_RATE=200
TTS_VOLUME=1.0
SPEECH_RECOGNITION_ENGINE=whisper

# Wake Word Configuration  
WAKE_WORD=cherry
WAKE_WORD_SENSITIVITY=0.5
CONTINUOUS_LISTENING=true

# GUI Configuration
GUI_THEME=modern
GUI_POSITION=center
AUTO_HIDE_GUI=true

# Memory Configuration
MEMORY_TYPE=chromadb
MEMORY_LIMIT=1000
CONTEXT_WINDOW=10

# Desktop Control
SCREEN_CAPTURE_INTERVAL=1.0
PYAUTOGUI_FAILSAFE=true
MOUSE_MOVEMENT_SPEED=1.0

# Logging
LOG_LEVEL=INFO
LOG_FILE=data/logs/cherry.log
MAX_LOG_FILES=5

# Features (true/false)
ENABLE_WEB_SEARCH=true
ENABLE_FILE_OPERATIONS=true
ENABLE_SCREEN_ANALYSIS=true
ENABLE_SYSTEM_CONTROL=true
'''

# Save the files
with open('main.py', 'w') as f:
    f.write(main_py_content)

with open('config_settings.py', 'w') as f:
    f.write(settings_py_content)
    
with open('.env.example', 'w') as f:
    f.write(env_example_content)

print("Created main application files:")
print("✓ main.py - Application entry point")
print("✓ config_settings.py - Configuration management")  
print("✓ .env.example - Environment variables template")
print("\nNext, I'll create the core AI brain module...")