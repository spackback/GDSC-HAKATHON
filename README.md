# 🍒 Cherry AI Desktop Assistant

Cherry is an intelligent AI-powered desktop assistant that lives in your system tray and can control your computer, understand what's on your screen, and help with various tasks using voice or text commands.

## ✨ Features

### 🧠 AI Intelligence
- **Powered by Google Gemini API** (free tier compatible)
- **Contextual Memory**: Remembers conversations and learns your preferences
- **Multi-modal Understanding**: Processes text, voice, and visual input
- **RAG Integration**: Long-term memory with vector embeddings

### 🎤 Voice Capabilities
- **Wake Word Detection**: Say "Cherry" to activate
- **Speech Recognition**: Multiple engines (Whisper, Vosk, Google)
- **Text-to-Speech**: Natural voice responses with multiple voice options
- **Continuous Listening**: Background voice activation

### 👀 Computer Vision
- **Screen Analysis**: Understands what's currently on your screen
- **Screenshot Capture**: Take and analyze screenshots
- **OCR**: Extract text from images and screen content
- **Window Detection**: Identify and interact with applications

### ⌨️ Desktop Control
- **Mouse Control**: Click, drag, scroll at precise coordinates
- **Keyboard Automation**: Type text, press key combinations
- **Application Control**: Open, close, minimize, maximize windows
- **System Integration**: Native Windows, macOS, and Linux support

### 🖥️ Interface Options
- **System Tray**: Runs quietly in background
- **Popup GUI**: Modern Tkinter interface when needed
- **Global Hotkeys**: Customizable keyboard shortcuts
- **Voice Commands**: Hands-free operation

### 📁 File Operations
- **Document Creation**: Create Word docs, text files, code files
- **File Management**: Read, write, copy, move, delete files
- **Multi-format Support**: PDF, DOCX, TXT, MD, and more

### 🌐 Web Integration  
- **Web Search**: Search for information online
- **Content Extraction**: Read and summarize web pages
- **Privacy-Focused**: Uses DuckDuckGo for searches

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Windows 10/11, macOS 10.14+, or Linux
- Google Gemini API key (free at [aistudio.google.com](https://aistudio.google.com))

### Installation

1. **Clone or Download** the Cherry AI Assistant files
2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Get Gemini API Key**:
   - Visit [Google AI Studio](https://aistudio.google.com)
   - Create a free account
   - Generate an API key

4. **Configure Cherry**:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and add your API key:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```

5. **Run Cherry**:
   ```bash
   python main.py
   ```

Cherry will start in your system tray! 🍒

## 🎮 How to Use

### Voice Commands
1. Say **"Cherry"** to wake her up
2. Give your command: "Cherry, take a screenshot"
3. Cherry will respond and perform the action

### Keyboard Shortcuts
- `Ctrl+Alt+C`: Show Cherry interface
- `Ctrl+Alt+Q`: Quit Cherry
- `Escape`: Hide interface

### Text Interface
- Click the Cherry icon in system tray
- Select "Show Cherry" to open the GUI
- Type commands or chat naturally

## 🗣️ Example Commands

### Desktop Control
- "Cherry, take a screenshot"
- "Cherry, open calculator"
- "Cherry, type 'Hello World'"
- "Cherry, click at coordinates 100, 200"

### File Operations  
- "Cherry, create a document called 'meeting notes'"
- "Cherry, read the contents of readme.txt"
- "Cherry, list all Python files in this folder"

### Web & Research
- "Cherry, search for Python tutorials"
- "Cherry, what's the weather like today?"
- "Cherry, summarize this webpage"

### System Tasks
- "Cherry, what's running on my screen?"
- "Cherry, minimize all windows"
- "Cherry, show me system information"

## ⚙️ Configuration

### Environment Variables (.env)
```bash
# Required
GEMINI_API_KEY=your_api_key_here

# Optional Customization
WAKE_WORD=cherry
TTS_RATE=200
GUI_THEME=modern
LOG_LEVEL=INFO
```

### Voice Settings
- Change wake word in settings
- Adjust speech rate and volume
- Select different voice engines

### Memory Settings
- Control context window size
- Set memory retention period
- Configure RAG parameters

## 🏗️ Architecture

```
Cherry AI Assistant
├── Core Engine (cherry_brain.py)
│   ├── Gemini API Integration
│   ├── Task Planning & Execution
│   └── Context Management
├── Memory System (memory_manager.py)
│   ├── Vector Database (ChromaDB)
│   ├── Conversation History
│   └── RAG Implementation
├── Voice Processing (voice_processor.py)
│   ├── Wake Word Detection
│   ├── Speech Recognition
│   └── Text-to-Speech
├── Vision System (vision_system.py)
│   ├── Screen Capture
│   ├── OCR & Analysis
│   └── Window Detection
├── Desktop Control (desktop_controller.py)
│   ├── Mouse & Keyboard
│   ├── Application Control
│   └── System Integration
└── Interface Layer
    ├── System Tray (system_tray.py)
    ├── GUI Manager (gui_manager.py)
    └── Hotkey Manager (hotkey_manager.py)
```

## 🔧 Advanced Usage

### Custom Functions
Add your own capabilities by extending the Cherry brain:

```python
async def custom_function(self, params):
    # Your custom logic here
    return "Task completed!"
```

### Plugin System
Cherry's modular design makes it easy to add new features:
- Drop new modules in the `core/` directory
- Implement the standard async interface
- Register with the main brain

### API Integration
Connect Cherry to other services:
- Email (Gmail, Outlook)
- Calendar (Google Calendar)
- Cloud storage (Dropbox, Google Drive)
- Smart home devices

## 🛡️ Privacy & Security

- **Local Processing**: Most operations run locally
- **Encrypted Storage**: Sensitive data is encrypted
- **Privacy Mode**: Option to disable cloud features
- **Data Control**: Full control over stored information
- **No Tracking**: Cherry doesn't track or sell your data

## 📊 Free Tier Limits

Cherry is designed to work within Google Gemini's free tier:
- **15 requests per minute**
- **1,500 requests per day** 
- **1 million tokens per month**

Cherry optimizes usage by:
- Caching frequent responses
- Compressing context intelligently
- Using local processing when possible

## 🐛 Troubleshooting

### Common Issues

**"Cherry doesn't respond to wake word"**
- Check microphone permissions
- Adjust wake word sensitivity in settings
- Verify audio input device

**"GUI doesn't show"**
- Try `Ctrl+Alt+C` hotkey
- Check system tray for Cherry icon
- Restart Cherry if needed

**"API key errors"**
- Verify API key in `.env` file
- Check Gemini API quota
- Ensure API key has proper permissions

### Logs
Check `data/logs/cherry.log` for detailed error information.

## 🤝 Contributing

Cherry is open source! Contributions welcome:

1. Fork the repository
2. Create a feature branch
3. Add your improvements
4. Submit a pull request

### Development Setup
```bash
git clone <repository>
cd cherry-ai-assistant
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies
python -m pytest tests/  # Run tests
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Google Gemini for AI capabilities
- OpenAI for Whisper speech recognition
- The Python community for amazing libraries
- Contributors and testers

## 🔮 Roadmap

### Upcoming Features
- [ ] Multi-language support
- [ ] Calendar integration
- [ ] Email management
- [ ] Smart home control
- [ ] Custom voice training
- [ ] Mobile companion app
- [ ] Plugin marketplace
- [ ] Team collaboration features

### Performance Improvements
- [ ] Faster startup time
- [ ] Reduced memory usage
- [ ] Better caching strategies
- [ ] Offline mode enhancements

---

## 📞 Support

Need help? Here are your options:

1. **Documentation**: Check this README and code comments
2. **Issues**: Report bugs and request features on GitHub
3. **Discussions**: Join community discussions
4. **Wiki**: Detailed guides and tutorials

---

**Made with 🍒 and ❤️ for the AI community**

*Cherry AI Assistant - Your intelligent desktop companion*
