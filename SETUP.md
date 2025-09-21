# 🚀 Quick Setup Guide - Cherry AI Desktop Assistant

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
