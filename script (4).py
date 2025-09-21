# Create voice_processor.py
voice_processor_content = '''"""
Voice Processor for Cherry AI Assistant
Handles speech recognition, text-to-speech, and wake word detection
"""

import asyncio
import logging
import threading
import queue
from typing import Callable, Optional, Any, Dict

try:
    import speech_recognition as sr
    import pyttsx3
    import pyaudio
    import sounddevice as sd
    import numpy as np
except ImportError:
    print("Voice processing dependencies not installed. Install with:")
    print("pip install SpeechRecognition pyttsx3 pyaudio sounddevice numpy")
    import sys
    sys.exit(1)

class VoiceProcessor:
    """Handles all voice-related functionality for Cherry"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Speech recognition
        self.recognizer = sr.Recognizer()
        self.microphone = None
        
        # Text-to-speech engine
        self.tts_engine = None
        
        # Voice processing state
        self.is_listening = False
        self.listening_thread = None
        self.voice_callback = None
        
        # Wake word detection
        self.wake_word = config['WAKE_WORD'].lower()
        self.wake_word_active = False
        
        # Audio settings
        self.sample_rate = 16000
        self.chunk_size = 1024
        
    async def initialize(self):
        """Initialize voice processing components"""
        try:
            self.logger.info("Initializing voice processor...")
            
            # Initialize microphone
            self.microphone = sr.Microphone()
            
            # Calibrate for ambient noise
            self.logger.info("Calibrating microphone for ambient noise...")
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=2)
            
            # Initialize TTS engine
            self.tts_engine = pyttsx3.init()
            
            # Configure TTS settings
            self._configure_tts()
            
            # Test TTS
            await self.speak("Cherry voice system initialized", wait=True)
            
            self.logger.info("Voice processor initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize voice processor: {e}")
            raise
    
    def _configure_tts(self):
        """Configure text-to-speech settings"""
        try:
            # Set speech rate
            rate = self.tts_engine.getProperty('rate')
            self.tts_engine.setProperty('rate', self.config['TTS_RATE'])
            
            # Set volume
            volume = self.tts_engine.getProperty('volume')
            self.tts_engine.setProperty('volume', self.config['TTS_VOLUME'])
            
            # Set voice (try to use female voice if available)
            voices = self.tts_engine.getProperty('voices')
            if voices:
                # Prefer female voice for Cherry
                female_voice = None
                for voice in voices:
                    if 'female' in voice.name.lower() or 'woman' in voice.name.lower():
                        female_voice = voice
                        break
                
                if female_voice:
                    self.tts_engine.setProperty('voice', female_voice.id)
                    self.logger.info(f"Using voice: {female_voice.name}")
                else:
                    # Use first available voice
                    self.tts_engine.setProperty('voice', voices[0].id)
                    self.logger.info(f"Using voice: {voices[0].name}")
            
        except Exception as e:
            self.logger.warning(f"Error configuring TTS: {e}")
    
    async def start_listening(self, voice_callback: Callable[[str], None]):
        """Start continuous voice listening"""
        if self.is_listening:
            return
        
        self.voice_callback = voice_callback
        self.is_listening = True
        
        # Start listening in a separate thread
        self.listening_thread = threading.Thread(
            target=self._continuous_listening_loop,
            daemon=True
        )
        self.listening_thread.start()
        
        self.logger.info("Started continuous voice listening")
    
    async def stop_listening(self):
        """Stop voice listening"""
        self.is_listening = False
        self.voice_callback = None
        
        if self.listening_thread and self.listening_thread.is_alive():
            self.listening_thread.join(timeout=2)
        
        self.logger.info("Stopped voice listening")
    
    def _continuous_listening_loop(self):
        """Main listening loop running in separate thread"""
        self.logger.info("Voice listening loop started")
        
        while self.is_listening:
            try:
                # Listen for audio
                with self.microphone as source:
                    # Listen with timeout
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=5)
                
                # Recognize speech
                try:
                    # Use Google Speech Recognition (free tier)
                    text = self.recognizer.recognize_google(audio).lower()
                    
                    if text:
                        self.logger.info(f"Heard: {text}")
                        
                        # Check for wake word or process command
                        if self._check_wake_word(text):
                            self.wake_word_active = True
                            self.logger.info("Wake word detected!")
                            if self.voice_callback:
                                asyncio.create_task(self.speak("Yes?"))
                        elif self.wake_word_active:
                            # Process command after wake word
                            self.wake_word_active = False
                            if self.voice_callback:
                                asyncio.run_coroutine_threadsafe(
                                    self.voice_callback(text),
                                    asyncio.get_event_loop()
                                )
                
                except sr.UnknownValueError:
                    # Speech not recognized, continue listening
                    pass
                except sr.RequestError as e:
                    self.logger.error(f"Speech recognition error: {e}")
                    
            except sr.WaitTimeoutError:
                # No speech detected, continue
                pass
            except Exception as e:
                self.logger.error(f"Error in listening loop: {e}")
                break
        
        self.logger.info("Voice listening loop ended")
    
    def _check_wake_word(self, text: str) -> bool:
        """Check if wake word is present in text"""
        words = text.split()
        
        # Check for exact wake word
        if self.wake_word in words:
            return True
        
        # Check for wake word as part of phrase
        if self.wake_word in text:
            return True
        
        # Check for variations (hey cherry, hi cherry, etc.)
        wake_variations = [
            f"hey {self.wake_word}",
            f"hi {self.wake_word}",
            f"hello {self.wake_word}",
            f"ok {self.wake_word}",
        ]
        
        for variation in wake_variations:
            if variation in text:
                return True
        
        return False
    
    async def speak(self, text: str, wait: bool = False):
        """Convert text to speech"""
        try:
            if not text or not self.tts_engine:
                return
            
            self.logger.info(f"Speaking: {text[:100]}...")
            
            if wait:
                # Synchronous speech (wait for completion)
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            else:
                # Asynchronous speech
                def speak_async():
                    self.tts_engine.say(text)
                    self.tts_engine.runAndWait()
                
                thread = threading.Thread(target=speak_async, daemon=True)
                thread.start()
                
        except Exception as e:
            self.logger.error(f"Error in text-to-speech: {e}")
    
    async def recognize_speech_from_audio(self, audio_data) -> Optional[str]:
        """Recognize speech from audio data"""
        try:
            # Convert audio data to speech recognition format
            text = self.recognizer.recognize_google(audio_data)
            return text
        except sr.UnknownValueError:
            return None
        except sr.RequestError as e:
            self.logger.error(f"Speech recognition error: {e}")
            return None
    
    def get_available_voices(self) -> list:
        """Get list of available TTS voices"""
        try:
            if self.tts_engine:
                voices = self.tts_engine.getProperty('voices')
                return [{'id': v.id, 'name': v.name} for v in voices] if voices else []
            return []
        except Exception as e:
            self.logger.error(f"Error getting voices: {e}")
            return []
    
    def set_voice(self, voice_id: str):
        """Set TTS voice by ID"""
        try:
            if self.tts_engine:
                self.tts_engine.setProperty('voice', voice_id)
                self.logger.info(f"Voice changed to: {voice_id}")
        except Exception as e:
            self.logger.error(f"Error setting voice: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get voice processor status"""
        return {
            'is_listening': self.is_listening,
            'wake_word_active': self.wake_word_active,
            'wake_word': self.wake_word,
            'tts_engine_available': self.tts_engine is not None,
            'microphone_available': self.microphone is not None,
            'available_voices': len(self.get_available_voices()),
        }
    
    async def cleanup(self):
        """Cleanup voice processor resources"""
        try:
            await self.stop_listening()
            
            if self.tts_engine:
                self.tts_engine.stop()
            
            self.logger.info("Voice processor cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during voice processor cleanup: {e}")
'''

print("Created voice_processor.py - Speech recognition and TTS")

# Create vision_system.py
vision_system_content = '''"""
Vision System for Cherry AI Assistant
Handles screen capture, computer vision, and visual analysis
"""

import asyncio
import logging
import cv2
import numpy as np
from typing import Dict, List, Tuple, Any, Optional
from pathlib import Path
from datetime import datetime

try:
    import pyautogui
    from PIL import Image, ImageGrab
    import pytesseract  # For OCR
except ImportError:
    print("Vision dependencies not installed. Install with:")
    print("pip install pyautogui pillow opencv-python pytesseract")
    import sys
    sys.exit(1)

class VisionSystem:
    """Handles screen capture and visual analysis for Cherry"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Screen capture settings
        self.screen_width, self.screen_height = pyautogui.size()
        self.capture_interval = config['SCREEN_CAPTURE_INTERVAL']
        
        # Visual analysis state
        self.last_screenshot = None
        self.last_screen_text = None
        self.screen_change_threshold = 0.1
        
        # Cache for performance
        self.screenshot_cache = {}
        self.analysis_cache = {}
        
    async def take_screenshot(self, region: Optional[Tuple[int, int, int, int]] = None) -> Dict[str, Any]:
        """Take a screenshot and return image info"""
        try:
            timestamp = datetime.now().isoformat()
            
            # Take screenshot
            if region:
                screenshot = pyautogui.screenshot(region=region)
            else:
                screenshot = pyautogui.screenshot()
            
            # Save screenshot
            screenshot_dir = self.config['CACHE_DIR'] / 'screenshots'
            screenshot_dir.mkdir(exist_ok=True)
            
            filename = f"screenshot_{timestamp.replace(':', '_')}.png"
            filepath = screenshot_dir / filename
            screenshot.save(filepath)
            
            # Convert to OpenCV format for analysis
            cv_image = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            
            # Store for comparison
            self.last_screenshot = cv_image
            
            # Basic image analysis
            analysis = await self._analyze_screenshot(cv_image)
            
            return {
                'timestamp': timestamp,
                'filepath': str(filepath),
                'dimensions': screenshot.size,
                'analysis': analysis,
                'region': region
            }
            
        except Exception as e:
            self.logger.error(f"Error taking screenshot: {e}")
            return {'error': str(e)}
    
    async def _analyze_screenshot(self, cv_image: np.ndarray) -> Dict[str, Any]:
        """Analyze screenshot content"""
        analysis = {}
        
        try:
            # Convert back to PIL for OCR
            pil_image = Image.fromarray(cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB))
            
            # Extract text using OCR
            try:
                extracted_text = pytesseract.image_to_string(pil_image)
                analysis['text_content'] = extracted_text.strip()
                analysis['has_text'] = bool(extracted_text.strip())
            except Exception as e:
                analysis['text_content'] = ""
                analysis['has_text'] = False
                self.logger.warning(f"OCR failed: {e}")
            
            # Color analysis
            mean_color = cv_image.mean(axis=(0, 1))
            analysis['dominant_colors'] = {
                'blue': int(mean_color[0]),
                'green': int(mean_color[1]), 
                'red': int(mean_color[2])
            }
            
            # Brightness analysis
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            analysis['brightness'] = float(gray.mean())
            analysis['is_dark'] = analysis['brightness'] < 100
            
            # Edge detection for activity
            edges = cv2.Canny(gray, 50, 150)
            analysis['edge_density'] = float(edges.mean())
            analysis['has_activity'] = analysis['edge_density'] > 10
            
            # Window detection (basic)
            analysis['potential_windows'] = await self._detect_windows(cv_image)
            
        except Exception as e:
            self.logger.error(f"Error in screenshot analysis: {e}")
            analysis['error'] = str(e)
        
        return analysis
    
    async def _detect_windows(self, cv_image: np.ndarray) -> List[Dict]:
        """Detect potential window areas"""
        try:
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            # Find contours that might be windows
            contours, _ = cv2.findContours(gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            windows = []
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 10000:  # Filter small areas
                    x, y, w, h = cv2.boundingRect(contour)
                    windows.append({
                        'x': int(x),
                        'y': int(y), 
                        'width': int(w),
                        'height': int(h),
                        'area': int(area)
                    })
            
            return windows[:10]  # Limit to 10 largest windows
            
        except Exception as e:
            self.logger.error(f"Error detecting windows: {e}")
            return []
    
    async def get_screen_context(self) -> Optional[str]:
        """Get textual description of current screen content"""
        try:
            screenshot_info = await self.take_screenshot()
            
            if 'analysis' in screenshot_info:
                analysis = screenshot_info['analysis']
                
                context_parts = []
                
                # Screen content description
                if analysis.get('has_text'):
                    text_content = analysis['text_content'][:500]  # Limit text length
                    context_parts.append(f"Screen contains text: {text_content}")
                
                # Visual characteristics
                if analysis.get('is_dark'):
                    context_parts.append("Screen appears dark")
                else:
                    context_parts.append("Screen appears bright")
                
                if analysis.get('has_activity'):
                    context_parts.append("Screen shows visual activity")
                
                # Window information
                windows = analysis.get('potential_windows', [])
                if windows:
                    context_parts.append(f"Detected {len(windows)} potential windows/areas")
                
                return ". ".join(context_parts) if context_parts else "Screen analysis available"
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting screen context: {e}")
            return None
    
    async def find_image_on_screen(self, template_path: str, confidence: float = 0.8) -> Optional[Dict]:
        """Find an image template on the current screen"""
        try:
            # Take current screenshot
            screenshot = pyautogui.screenshot()
            screen_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            
            # Load template image
            template = cv2.imread(template_path)
            if template is None:
                self.logger.error(f"Template image not found: {template_path}")
                return None
            
            # Template matching
            result = cv2.matchTemplate(screen_cv, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)
            
            if max_val >= confidence:
                # Found match
                h, w = template.shape[:2]
                center_x = max_loc[0] + w // 2
                center_y = max_loc[1] + h // 2
                
                return {
                    'found': True,
                    'confidence': float(max_val),
                    'location': {
                        'x': center_x,
                        'y': center_y,
                        'top_left': max_loc,
                        'bottom_right': (max_loc[0] + w, max_loc[1] + h)
                    }
                }
            else:
                return {'found': False, 'confidence': float(max_val)}
                
        except Exception as e:
            self.logger.error(f"Error finding image on screen: {e}")
            return None
    
    async def detect_screen_changes(self) -> bool:
        """Detect if screen has changed significantly"""
        try:
            current_screenshot = pyautogui.screenshot()
            current_cv = cv2.cvtColor(np.array(current_screenshot), cv2.COLOR_RGB2BGR)
            
            if self.last_screenshot is not None:
                # Calculate difference
                diff = cv2.absdiff(self.last_screenshot, current_cv)
                diff_percentage = diff.mean() / 255.0
                
                has_changed = diff_percentage > self.screen_change_threshold
                
                if has_changed:
                    self.logger.info(f"Screen change detected: {diff_percentage:.3f}")
                
                # Update last screenshot
                self.last_screenshot = current_cv
                
                return has_changed
            else:
                # First screenshot
                self.last_screenshot = current_cv
                return True
                
        except Exception as e:
            self.logger.error(f"Error detecting screen changes: {e}")
            return False
    
    async def get_window_info(self) -> List[Dict]:
        """Get information about currently open windows"""
        try:
            import psutil
            
            windows = []
            
            # Get running processes with windows (simplified)
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    proc_info = proc.as_dict(attrs=['pid', 'name'])
                    
                    # Filter common GUI applications
                    gui_apps = ['chrome', 'firefox', 'notepad', 'code', 'explorer', 
                               'word', 'excel', 'powerpoint', 'calculator']
                    
                    if any(app in proc_info['name'].lower() for app in gui_apps):
                        windows.append({
                            'name': proc_info['name'],
                            'pid': proc_info['pid']
                        })
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return windows[:20]  # Limit results
            
        except Exception as e:
            self.logger.error(f"Error getting window info: {e}")
            return []
    
    async def capture_specific_area(self, x: int, y: int, width: int, height: int) -> Dict[str, Any]:
        """Capture a specific area of the screen"""
        try:
            region = (x, y, width, height)
            return await self.take_screenshot(region=region)
        except Exception as e:
            self.logger.error(f"Error capturing specific area: {e}")
            return {'error': str(e)}
    
    def get_screen_resolution(self) -> Tuple[int, int]:
        """Get current screen resolution"""
        return (self.screen_width, self.screen_height)
    
    async def cleanup(self):
        """Cleanup vision system resources"""
        try:
            # Clear caches
            self.screenshot_cache.clear()
            self.analysis_cache.clear()
            
            self.logger.info("Vision system cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during vision system cleanup: {e}")
'''

print("Created vision_system.py - Screen capture and computer vision")

# Create desktop_controller.py 
desktop_controller_content = '''"""
Desktop Controller for Cherry AI Assistant  
Handles mouse, keyboard control and desktop automation
"""

import asyncio
import logging
import time
from typing import Dict, List, Tuple, Any, Optional

try:
    import pyautogui
    import pynput
    from pynput import mouse, keyboard
    import psutil
except ImportError:
    print("Desktop control dependencies not installed. Install with:")
    print("pip install pyautogui pynput psutil")
    import sys
    sys.exit(1)

class DesktopController:
    """Handles desktop automation and control for Cherry"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # PyAutoGUI settings
        pyautogui.FAILSAFE = config['PYAUTOGUI_FAILSAFE']
        pyautogui.PAUSE = 0.1  # Small pause between actions
        
        # Mouse and keyboard controllers
        self.mouse_controller = mouse.Controller()
        self.keyboard_controller = keyboard.Controller()
        
        # Movement settings
        self.movement_speed = config['MOUSE_MOVEMENT_SPEED']
        
        # Safety limits
        self.max_clicks_per_minute = 60
        self.click_count = 0
        self.last_reset_time = time.time()
        
    async def move_mouse(self, x: int, y: int, smooth: bool = True) -> bool:
        """Move mouse to specified coordinates"""
        try:
            current_x, current_y = pyautogui.position()
            
            if smooth and self.movement_speed < 1.0:
                # Smooth movement
                steps = 10
                for step in range(steps):
                    intermediate_x = current_x + (x - current_x) * (step + 1) / steps
                    intermediate_y = current_y + (y - current_y) * (step + 1) / steps
                    pyautogui.moveTo(intermediate_x, intermediate_y)
                    await asyncio.sleep(0.01 / self.movement_speed)
            else:
                # Direct movement
                pyautogui.moveTo(x, y)
            
            self.logger.info(f"Moved mouse to ({x}, {y})")
            return True
            
        except Exception as e:
            self.logger.error(f"Error moving mouse: {e}")
            return False
    
    async def click_mouse(self, x: Optional[int] = None, y: Optional[int] = None, 
                         button: str = 'left', clicks: int = 1, interval: float = 0.1) -> bool:
        """Click mouse at specified location"""
        try:
            # Safety check
            if not self._check_click_safety():
                self.logger.warning("Click rate limit exceeded")
                return False
            
            # Move to position if specified
            if x is not None and y is not None:
                await self.move_mouse(x, y)
            
            # Perform click
            pyautogui.click(clicks=clicks, interval=interval, button=button)
            
            self.click_count += clicks
            self.logger.info(f"Clicked {button} button {clicks} times at current position")
            return True
            
        except Exception as e:
            self.logger.error(f"Error clicking mouse: {e}")
            return False
    
    async def drag_mouse(self, start_x: int, start_y: int, end_x: int, end_y: int, 
                        duration: float = 1.0) -> bool:
        """Drag mouse from start to end position"""
        try:
            # Move to start position
            await self.move_mouse(start_x, start_y)
            await asyncio.sleep(0.1)
            
            # Perform drag
            pyautogui.drag(end_x - start_x, end_y - start_y, duration=duration)
            
            self.logger.info(f"Dragged from ({start_x}, {start_y}) to ({end_x}, {end_y})")
            return True
            
        except Exception as e:
            self.logger.error(f"Error dragging mouse: {e}")
            return False
    
    async def scroll(self, clicks: int, x: Optional[int] = None, y: Optional[int] = None) -> bool:
        """Scroll at specified location"""
        try:
            if x is not None and y is not None:
                await self.move_mouse(x, y)
                await asyncio.sleep(0.1)
            
            pyautogui.scroll(clicks)
            
            self.logger.info(f"Scrolled {clicks} clicks")
            return True
            
        except Exception as e:
            self.logger.error(f"Error scrolling: {e}")
            return False
    
    async def type_text(self, text: str, interval: float = 0.05) -> bool:
        """Type text with specified interval between characters"""
        try:
            # Clean text (remove problematic characters)
            clean_text = text.replace('\\n', '\\n').replace('\\t', '\\t')
            
            pyautogui.typewrite(clean_text, interval=interval)
            
            self.logger.info(f"Typed text: {text[:50]}...")
            return True
            
        except Exception as e:
            self.logger.error(f"Error typing text: {e}")
            return False
    
    async def press_key(self, key: str, modifier: Optional[str] = None) -> bool:
        """Press a key or key combination"""
        try:
            if modifier:
                # Key combination (e.g., ctrl+c)
                key_combination = [modifier, key]
                pyautogui.hotkey(*key_combination)
                self.logger.info(f"Pressed key combination: {modifier}+{key}")
            else:
                # Single key
                pyautogui.press(key)
                self.logger.info(f"Pressed key: {key}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error pressing key: {e}")
            return False
    
    async def press_multiple_keys(self, keys: List[str]) -> bool:
        """Press multiple keys in sequence"""
        try:
            for key in keys:
                pyautogui.press(key)
                await asyncio.sleep(0.1)
            
            self.logger.info(f"Pressed keys: {', '.join(keys)}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error pressing multiple keys: {e}")
            return False
    
    async def open_application(self, app_name: str) -> bool:
        """Open an application using Windows Run dialog or system commands"""
        try:
            # Use Windows Run dialog (Win + R)
            await self.press_key('r', 'win')
            await asyncio.sleep(0.5)
            
            # Type application name
            await self.type_text(app_name)
            await asyncio.sleep(0.5)
            
            # Press Enter
            await self.press_key('enter')
            
            self.logger.info(f"Attempted to open application: {app_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error opening application: {e}")
            return False
    
    async def minimize_window(self) -> bool:
        """Minimize current active window"""
        try:
            await self.press_key('down', 'win')
            self.logger.info("Minimized current window")
            return True
        except Exception as e:
            self.logger.error(f"Error minimizing window: {e}")
            return False
    
    async def maximize_window(self) -> bool:
        """Maximize current active window"""
        try:
            await self.press_key('up', 'win')
            self.logger.info("Maximized current window")
            return True
        except Exception as e:
            self.logger.error(f"Error maximizing window: {e}")
            return False
    
    async def close_window(self) -> bool:
        """Close current active window"""
        try:
            await self.press_key('f4', 'alt')
            self.logger.info("Closed current window")
            return True
        except Exception as e:
            self.logger.error(f"Error closing window: {e}")
            return False
    
    async def switch_application(self, direction: str = 'forward') -> bool:
        """Switch between applications using Alt+Tab"""
        try:
            if direction == 'forward':
                await self.press_key('tab', 'alt')
            else:
                # Alt+Shift+Tab for backward
                pyautogui.hotkey('alt', 'shift', 'tab')
            
            self.logger.info(f"Switched application ({direction})")
            return True
            
        except Exception as e:
            self.logger.error(f"Error switching application: {e}")
            return False
    
    def get_mouse_position(self) -> Tuple[int, int]:
        """Get current mouse position"""
        return pyautogui.position()
    
    def get_screen_size(self) -> Tuple[int, int]:
        """Get screen dimensions"""
        return pyautogui.size()
    
    async def take_screenshot_action(self) -> str:
        """Take a screenshot using system hotkeys"""
        try:
            # Use Windows screenshot shortcut
            await self.press_key('prtsc', 'win')
            await asyncio.sleep(1)
            
            self.logger.info("Screenshot taken using system shortcut")
            return "Screenshot captured to clipboard"
            
        except Exception as e:
            self.logger.error(f"Error taking screenshot: {e}")
            return f"Error: {str(e)}"
    
    def _check_click_safety(self) -> bool:
        """Check if click rate is within safe limits"""
        current_time = time.time()
        
        # Reset counter every minute
        if current_time - self.last_reset_time > 60:
            self.click_count = 0
            self.last_reset_time = current_time
        
        return self.click_count < self.max_clicks_per_minute
    
    async def copy_text(self) -> bool:
        """Copy selected text to clipboard"""
        try:
            await self.press_key('c', 'ctrl')
            self.logger.info("Copied text to clipboard")
            return True
        except Exception as e:
            self.logger.error(f"Error copying text: {e}")
            return False
    
    async def paste_text(self) -> bool:
        """Paste text from clipboard"""
        try:
            await self.press_key('v', 'ctrl')
            self.logger.info("Pasted text from clipboard")
            return True
        except Exception as e:
            self.logger.error(f"Error pasting text: {e}")
            return False
    
    async def select_all(self) -> bool:
        """Select all content"""
        try:
            await self.press_key('a', 'ctrl')
            self.logger.info("Selected all content")
            return True
        except Exception as e:
            self.logger.error(f"Error selecting all: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get desktop controller status"""
        return {
            'mouse_position': self.get_mouse_position(),
            'screen_size': self.get_screen_size(),
            'click_count_current_minute': self.click_count,
            'movement_speed': self.movement_speed,
            'failsafe_enabled': pyautogui.FAILSAFE,
        }
    
    async def cleanup(self):
        """Cleanup desktop controller resources"""
        try:
            # Reset any held keys/buttons
            self.logger.info("Desktop controller cleanup completed")
        except Exception as e:
            self.logger.error(f"Error during desktop controller cleanup: {e}")
'''

print("Created desktop_controller.py - Mouse and keyboard automation")

# Save all the files
with open('voice_processor.py', 'w') as f:
    f.write(voice_processor_content)

with open('vision_system.py', 'w') as f:
    f.write(vision_system_content)

with open('desktop_controller.py', 'w') as f:
    f.write(desktop_controller_content)

print("\nCompleted additional core modules:")
print("✓ voice_processor.py - Speech recognition and text-to-speech")
print("✓ vision_system.py - Screen capture and computer vision") 
print("✓ desktop_controller.py - Mouse and keyboard automation")