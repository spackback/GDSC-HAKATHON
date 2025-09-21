# Create installation script and final project files

# install.py - Installation and setup script
install_script = '''#!/usr/bin/env python3
"""
Cherry AI Desktop Assistant - Installation Script
Automates the setup process for new users
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def print_banner():
    """Print Cherry installation banner"""
    banner = """
    🍒====================================🍒
           Cherry AI Desktop Assistant
              Installation Script
    🍒====================================🍒
    """
    print(banner)

def check_python_version():
    """Check if Python version is compatible"""
    print("🔍 Checking Python version...")
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    else:
        print(f"✅ Python {sys.version.split()[0]} - OK")
        return True

def install_requirements():
    """Install required packages"""
    print("📦 Installing required packages...")
    
    try:
        # Upgrade pip first
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        
        # Install requirements
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        
        print("✅ All packages installed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing packages: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    print("📁 Creating directories...")
    
    directories = [
        "config",
        "core", 
        "interface",
        "utils",
        "data",
        "data/memory",
        "data/cache", 
        "data/logs",
        "data/assets"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✅ Directories created")
    return True

def setup_environment():
    """Setup environment configuration"""
    print("⚙️ Setting up environment...")
    
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists() and env_example.exists():
        # Copy example to .env
        with open(env_example, 'r') as src, open(env_file, 'w') as dst:
            dst.write(src.read())
        print("✅ Created .env file from template")
    
    # Prompt for API key
    api_key = input("\\n🔑 Enter your Gemini API Key (or press Enter to skip): ").strip()
    
    if api_key:
        # Update .env file with API key
        try:
            with open(env_file, 'r') as f:
                content = f.read()
            
            # Replace the API key line
            content = content.replace(
                "GEMINI_API_KEY=your_gemini_api_key_here",
                f"GEMINI_API_KEY={api_key}"
            )
            
            with open(env_file, 'w') as f:
                f.write(content)
            
            print("✅ API key configured")
            
        except Exception as e:
            print(f"⚠️ Warning: Could not update API key: {e}")
    else:
        print("⚠️ Skipped API key setup - you can add it later in .env file")
    
    return True

def check_system_requirements():
    """Check system-specific requirements"""
    print("🖥️ Checking system requirements...")
    
    system = platform.system()
    
    if system == "Windows":
        print("✅ Windows detected")
        print("ℹ️ Note: Cherry works best with administrator privileges on Windows")
        
    elif system == "Darwin":  # macOS
        print("✅ macOS detected")
        print("ℹ️ Note: You may need to grant accessibility permissions to Python")
        
    elif system == "Linux":
        print("✅ Linux detected")
        print("ℹ️ Note: You may need to install additional packages:")
        print("   sudo apt-get install espeak espeak-data libespeak1 libespeak-dev")
        print("   sudo apt-get install python3-tk python3-dev python3-xlib")
        
    else:
        print(f"⚠️ Unknown system: {system}")
    
    return True

def create_init_files():
    """Create __init__.py files for packages"""
    print("📝 Creating package files...")
    
    init_dirs = ["config", "core", "interface", "utils"]
    
    for directory in init_dirs:
        init_file = Path(directory) / "__init__.py"
        if not init_file.exists():
            init_file.touch()
    
    print("✅ Package files created")
    return True

def test_installation():
    """Test if installation works"""
    print("🧪 Testing installation...")
    
    try:
        # Test imports
        import google.genai
        import speech_recognition
        import pyttsx3
        import pyautogui
        import pystray
        import cv2
        import chromadb
        
        print("✅ All core modules can be imported")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def main():
    """Main installation function"""
    print_banner()
    
    # Installation steps
    steps = [
        ("Checking Python version", check_python_version),
        ("Creating directories", create_directories),
        ("Creating package files", create_init_files),
        ("Installing requirements", install_requirements),
        ("Setting up environment", setup_environment),
        ("Checking system requirements", check_system_requirements),
        ("Testing installation", test_installation),
    ]
    
    success_count = 0
    
    for step_name, step_function in steps:
        print(f"\\n{'='*50}")
        print(f"Step: {step_name}")
        print('='*50)
        
        if step_function():
            success_count += 1
        else:
            print(f"❌ Failed: {step_name}")
            break
    
    # Installation summary
    print(f"\\n{'='*50}")
    print("INSTALLATION SUMMARY")
    print('='*50)
    
    if success_count == len(steps):
        print("🎉 Installation completed successfully!")
        print("\\n🚀 Next steps:")
        print("1. Add your Gemini API key to the .env file if you haven't already")
        print("2. Run: python main.py")
        print("3. Look for Cherry 🍒 in your system tray!")
        print("\\n📖 For help, check README.md or run with --help")
        
    else:
        print(f"❌ Installation failed at step: {steps[success_count][0]}")
        print("\\n🔧 Troubleshooting:")
        print("- Check your internet connection")
        print("- Ensure you have Python 3.8+")
        print("- Try running with admin/sudo privileges")
        print("- Check the error messages above")

if __name__ == "__main__":
    main()
'''

# Create start.bat for Windows users
start_bat = '''@echo off
echo 🍒 Starting Cherry AI Desktop Assistant...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found! Please install Python 3.8+ first.
    echo Visit: https://python.org/downloads/
    pause
    exit /b 1
)

REM Check if .env exists
if not exist .env (
    echo ⚠️ Warning: .env file not found!
    echo Please run install.py first or create .env from .env.example
    pause
)

REM Start Cherry
echo ✅ Starting Cherry...
python main.py

if errorlevel 1 (
    echo.
    echo ❌ Cherry encountered an error!
    echo Check the logs in data/logs/cherry.log
    pause
)
'''

# Create start.sh for Linux/macOS users
start_sh = '''#!/bin/bash
echo "🍒 Starting Cherry AI Desktop Assistant..."
echo

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found! Please install Python 3.8+ first."
    exit 1
fi

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️ Warning: .env file not found!"
    echo "Please run install.py first or create .env from .env.example"
fi

# Start Cherry
echo "✅ Starting Cherry..."
python3 main.py

if [ $? -ne 0 ]; then
    echo
    echo "❌ Cherry encountered an error!"
    echo "Check the logs in data/logs/cherry.log"
    read -p "Press any key to continue..."
fi
'''

# Create quick setup guide
setup_guide = '''# 🚀 Quick Setup Guide - Cherry AI Desktop Assistant

## Option 1: Automated Installation (Recommended)

1. **Run the installer**:
   ```bash
   python install.py
   ```

2. **Follow the prompts** to:
   - Install dependencies
   - Configure API key
   - Set up directories

3. **Start Cherry**:
   - Windows: Double-click `start.bat`
   - Linux/macOS: `./start.sh` or `python3 main.py`

## Option 2: Manual Installation

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Setup environment**:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and add your Gemini API key

3. **Create directories**:
   ```bash
   mkdir -p data/{memory,cache,logs,assets}
   mkdir -p {config,core,interface,utils}
   ```

4. **Run Cherry**:
   ```bash
   python main.py
   ```

## Getting Your Gemini API Key

1. Visit [Google AI Studio](https://aistudio.google.com)
2. Sign in with your Google account
3. Click "Get API Key"
4. Create a new API key
5. Copy the key to your `.env` file

## First Run

1. Cherry will start in your system tray
2. Look for the 🍒 icon 
3. Right-click for options
4. Say "Cherry" to test voice activation
5. Use `Ctrl+Alt+C` to show the GUI

## Troubleshooting

**"Cherry doesn't start"**
- Check Python version: `python --version` (need 3.8+)
- Check API key in `.env` file
- Look at logs in `data/logs/cherry.log`

**"Voice doesn't work"**
- Check microphone permissions
- Install audio dependencies:
  - Windows: Usually included
  - Linux: `sudo apt-get install espeak espeak-data`
  - macOS: Should work out of the box

**"Screen capture fails"**
- Grant accessibility permissions (macOS)
- Run as administrator (Windows)
- Install X11 development packages (Linux)

## Need Help?

- Check `README.md` for detailed documentation
- Look at example commands in the GUI
- Check the logs for error messages
- Make sure your API key is valid

**Happy Cherry-ing! 🍒**
'''

# Save all setup files
with open('install.py', 'w') as f:
    f.write(install_script)

with open('start.bat', 'w') as f:
    f.write(start_bat)

with open('start.sh', 'w') as f:
    f.write(start_sh)

with open('SETUP.md', 'w') as f:
    f.write(setup_guide)

# Make start.sh executable (on Unix systems)
try:
    import stat
    os.chmod('start.sh', stat.S_IRWXU | stat.S_IRGRP | stat.S_IROTH)
except:
    pass  # Ignore on Windows

print("Created installation and setup files:")
print("✓ install.py - Automated installation script")
print("✓ start.bat - Windows startup script") 
print("✓ start.sh - Linux/macOS startup script")
print("✓ SETUP.md - Quick setup guide")

print("\n" + "="*60)
print("🍒 CHERRY AI DESKTOP ASSISTANT - COMPLETE FRAMEWORK 🍒")
print("="*60)

print("\n📁 Project Structure Created:")
project_files = [
    "main.py - Application entry point",
    "requirements.txt - Dependencies",
    ".env.example - Configuration template",
    "install.py - Automated installer",
    "start.bat / start.sh - Startup scripts",
    "README.md - Full documentation",
    "SETUP.md - Quick setup guide",
    "",
    "Core Modules:",
    "├── cherry_brain.py - AI processing engine", 
    "├── memory_manager.py - RAG and context management",
    "├── voice_processor.py - Speech recognition & TTS",
    "├── vision_system.py - Screen capture & computer vision",
    "└── desktop_controller.py - Mouse & keyboard automation",
    "",
    "Interface Modules:",
    "├── gui_manager.py - Tkinter popup interface",
    "├── system_tray.py - Background service",
    "└── hotkey_manager.py - Global hotkey detection",
    "",
    "Utility Modules:",
    "├── logger.py - Logging configuration", 
    "├── file_handler.py - File operations",
    "├── web_scraper.py - Web information retrieval",
    "└── config_settings.py - Configuration management"
]

for file_info in project_files:
    if file_info:
        if file_info.endswith(":"):
            print(f"\n{file_info}")
        else:
            print(f"  {file_info}")

print("\n🚀 READY TO USE!")
print("1. Get your free Gemini API key at https://aistudio.google.com")
print("2. Run: python install.py") 
print("3. Run: python main.py")
print("4. Look for Cherry 🍒 in your system tray!")

print("\n✨ Features Ready:")
print("• Voice activation with 'Cherry' wake word")
print("• Desktop automation (mouse, keyboard, screenshots)")
print("• Computer vision and screen analysis") 
print("• Memory and context management with RAG")
print("• Web search and information retrieval")
print("• File operations and document creation")
print("• System tray integration and GUI interface") 
print("• Global hotkeys and voice commands")
print("• Free Gemini API integration")
print("• Cross-platform compatibility")

print("\n🍒 Cherry AI Assistant is ready to be your intelligent desktop companion! 🍒")