#!/usr/bin/env python3
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
    api_key = input("\n🔑 Enter your Gemini API Key (or press Enter to skip): ").strip()

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
        print(f"\n{'='*50}")
        print(f"Step: {step_name}")
        print('='*50)

        if step_function():
            success_count += 1
        else:
            print(f"❌ Failed: {step_name}")
            break

    # Installation summary
    print(f"\n{'='*50}")
    print("INSTALLATION SUMMARY")
    print('='*50)

    if success_count == len(steps):
        print("🎉 Installation completed successfully!")
        print("\n🚀 Next steps:")
        print("1. Add your Gemini API key to the .env file if you haven't already")
        print("2. Run: python main.py")
        print("3. Look for Cherry 🍒 in your system tray!")
        print("\n📖 For help, check README.md or run with --help")

    else:
        print(f"❌ Installation failed at step: {steps[success_count][0]}")
        print("\n🔧 Troubleshooting:")
        print("- Check your internet connection")
        print("- Ensure you have Python 3.8+")
        print("- Try running with admin/sudo privileges")
        print("- Check the error messages above")

if __name__ == "__main__":
    main()
