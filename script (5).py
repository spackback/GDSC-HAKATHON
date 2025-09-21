# Create GUI manager and system tray interface modules

# gui_manager.py - Tkinter popup interface
gui_manager_content = '''"""
GUI Manager for Cherry AI Assistant
Handles the popup interface using Tkinter
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import logging
import threading
import asyncio
from typing import Dict, Any, Optional, Callable

class GUIManager:
    """Manages the Cherry AI Assistant GUI interface"""
    
    def __init__(self, cherry_brain, config: Dict[str, Any]):
        self.cherry_brain = cherry_brain
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # GUI state
        self.root = None
        self.is_visible = False
        self.gui_thread = None
        
        # UI components
        self.chat_display = None
        self.input_entry = None
        self.send_button = None
        self.status_label = None
        self.voice_button = None
        
        # Chat history for display
        self.chat_history = []
        
    def initialize(self):
        """Initialize the GUI in a separate thread"""
        try:
            self.gui_thread = threading.Thread(target=self._create_gui, daemon=True)
            self.gui_thread.start()
            self.logger.info("GUI manager initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize GUI: {e}")
    
    def _create_gui(self):
        """Create the main GUI window"""
        try:
            self.root = tk.Tk()
            self.root.title("🍒 Cherry AI Assistant")
            self.root.geometry("500x600")
            self.root.withdraw()  # Start hidden
            
            # Set window icon (if available)
            try:
                icon_path = self.config['ASSETS_DIR'] / 'cherry_icon.ico'
                if icon_path.exists():
                    self.root.iconbitmap(str(icon_path))
            except:
                pass  # Ignore icon errors
            
            # Configure style
            style = ttk.Style()
            style.theme_use('clam')
            
            # Configure colors
            self.root.configure(bg='#f0f0f0')
            
            self._create_widgets()
            self._setup_layout()
            self._bind_events()
            
            # Center window
            self._center_window()
            
            # Start the GUI main loop
            self.root.mainloop()
            
        except Exception as e:
            self.logger.error(f"Error creating GUI: {e}")
    
    def _create_widgets(self):
        """Create GUI widgets"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title label
        title_label = ttk.Label(main_frame, text="🍒 Cherry AI Assistant", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Ready", foreground="green")
        self.status_label.grid(row=1, column=0, columnspan=2, pady=(0, 10))
        
        # Chat display
        chat_frame = ttk.LabelFrame(main_frame, text="Conversation", padding="5")
        chat_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame, 
            wrap=tk.WORD, 
            width=50, 
            height=20,
            font=('Arial', 10),
            state=tk.DISABLED
        )
        self.chat_display.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Input frame
        input_frame = ttk.Frame(main_frame)
        input_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Text input
        self.input_entry = ttk.Entry(input_frame, font=('Arial', 10))
        self.input_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        # Send button
        self.send_button = ttk.Button(input_frame, text="Send", command=self._on_send_click)
        self.send_button.grid(row=0, column=1)
        
        # Voice button
        self.voice_button = ttk.Button(input_frame, text="🎤 Voice", command=self._on_voice_click)
        self.voice_button.grid(row=0, column=2, padx=(5, 0))
        
        # Control buttons frame
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=4, column=0, columnspan=2, pady=(0, 10))
        
        # Screenshot button
        screenshot_btn = ttk.Button(control_frame, text="📷 Screenshot", 
                                   command=self._on_screenshot_click)
        screenshot_btn.grid(row=0, column=0, padx=(0, 5))
        
        # Clear button
        clear_btn = ttk.Button(control_frame, text="🗑️ Clear", command=self._on_clear_click)
        clear_btn.grid(row=0, column=1, padx=(0, 5))
        
        # Settings button
        settings_btn = ttk.Button(control_frame, text="⚙️ Settings", command=self._on_settings_click)
        settings_btn.grid(row=0, column=2)
        
        # Configure grid weights
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        input_frame.columnconfigure(0, weight=1)
        chat_frame.columnconfigure(0, weight=1)
        chat_frame.rowconfigure(0, weight=1)
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
    
    def _setup_layout(self):
        """Setup the layout and styling"""
        # Configure text tags for chat display
        self.chat_display.configure(state=tk.NORMAL)
        
        # User message style
        self.chat_display.tag_configure("user", foreground="#0066cc", font=('Arial', 10, 'bold'))
        
        # Cherry response style  
        self.chat_display.tag_configure("cherry", foreground="#cc6600", font=('Arial', 10))
        
        # System message style
        self.chat_display.tag_configure("system", foreground="#666666", font=('Arial', 9, 'italic'))
        
        # Timestamp style
        self.chat_display.tag_configure("timestamp", foreground="#888888", font=('Arial', 8))
        
        self.chat_display.configure(state=tk.DISABLED)
    
    def _bind_events(self):
        """Bind keyboard and window events"""
        # Enter key sends message
        self.input_entry.bind('<Return>', lambda e: self._on_send_click())
        
        # Window close event
        self.root.protocol("WM_DELETE_WINDOW", self._on_window_close)
        
        # Escape key hides window
        self.root.bind('<Escape>', lambda e: self.hide())
    
    def _center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def _on_send_click(self):
        """Handle send button click"""
        try:
            message = self.input_entry.get().strip()
            if message:
                self.input_entry.delete(0, tk.END)
                self._process_user_input(message)
        except Exception as e:
            self.logger.error(f"Error handling send click: {e}")
    
    def _on_voice_click(self):
        """Handle voice button click"""
        try:
            if hasattr(self.cherry_brain, 'is_listening') and self.cherry_brain.is_listening:
                # Stop listening
                asyncio.run_coroutine_threadsafe(
                    self.cherry_brain.stop_listening(), 
                    asyncio.get_event_loop()
                )
                self.voice_button.configure(text="🎤 Voice")
                self._add_system_message("Voice listening stopped")
            else:
                # Start listening
                asyncio.run_coroutine_threadsafe(
                    self.cherry_brain.start_listening(),
                    asyncio.get_event_loop()
                )
                self.voice_button.configure(text="🔴 Stop")
                self._add_system_message("Voice listening started...")
                
        except Exception as e:
            self.logger.error(f"Error handling voice click: {e}")
            self._add_system_message(f"Voice error: {str(e)}")
    
    def _on_screenshot_click(self):
        """Handle screenshot button click"""
        try:
            self._add_system_message("Taking screenshot...")
            self._process_user_input("take a screenshot")
        except Exception as e:
            self.logger.error(f"Error handling screenshot click: {e}")
    
    def _on_clear_click(self):
        """Handle clear button click"""
        try:
            self.chat_display.configure(state=tk.NORMAL)
            self.chat_display.delete(1.0, tk.END)
            self.chat_display.configure(state=tk.DISABLED)
            self.chat_history.clear()
            self._add_system_message("Chat cleared")
        except Exception as e:
            self.logger.error(f"Error clearing chat: {e}")
    
    def _on_settings_click(self):
        """Handle settings button click"""
        try:
            self._show_settings_dialog()
        except Exception as e:
            self.logger.error(f"Error opening settings: {e}")
    
    def _show_settings_dialog(self):
        """Show settings dialog"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Cherry Settings")
        settings_window.geometry("400x300")
        settings_window.transient(self.root)
        
        # Settings content
        ttk.Label(settings_window, text="Settings", font=('Arial', 14, 'bold')).pack(pady=10)
        
        # Voice settings
        voice_frame = ttk.LabelFrame(settings_window, text="Voice Settings", padding="10")
        voice_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(voice_frame, text="Wake Word:").grid(row=0, column=0, sticky=tk.W)
        wake_word_var = tk.StringVar(value=self.config['WAKE_WORD'])
        ttk.Entry(voice_frame, textvariable=wake_word_var).grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        # Close button
        ttk.Button(settings_window, text="Close", 
                  command=settings_window.destroy).pack(pady=10)
        
        voice_frame.columnconfigure(1, weight=1)
    
    def _process_user_input(self, message: str):
        """Process user input message"""
        try:
            # Add user message to chat
            self._add_user_message(message)
            
            # Update status
            self._update_status("Processing...", "orange")
            
            # Process with Cherry brain in separate thread
            def process_async():
                try:
                    # Get or create event loop
                    try:
                        loop = asyncio.get_event_loop()
                    except RuntimeError:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                    
                    # Process input
                    response = loop.run_until_complete(
                        self.cherry_brain.process_input(message, {'input_type': 'text'})
                    )
                    
                    # Add response to chat on main thread
                    self.root.after(0, lambda: self._add_cherry_message(response))
                    self.root.after(0, lambda: self._update_status("Ready", "green"))
                    
                except Exception as e:
                    self.logger.error(f"Error processing input: {e}")
                    self.root.after(0, lambda: self._add_system_message(f"Error: {str(e)}"))
                    self.root.after(0, lambda: self._update_status("Error", "red"))
            
            # Start processing in background thread
            threading.Thread(target=process_async, daemon=True).start()
            
        except Exception as e:
            self.logger.error(f"Error processing user input: {e}")
            self._add_system_message(f"Error: {str(e)}")
    
    def _add_user_message(self, message: str):
        """Add user message to chat display"""
        self._add_chat_message(f"You: {message}", "user")
    
    def _add_cherry_message(self, message: str):
        """Add Cherry response to chat display"""
        self._add_chat_message(f"Cherry: {message}", "cherry")
    
    def _add_system_message(self, message: str):
        """Add system message to chat display"""
        self._add_chat_message(f"System: {message}", "system")
    
    def _add_chat_message(self, message: str, tag: str):
        """Add a message to the chat display"""
        try:
            self.chat_display.configure(state=tk.NORMAL)
            
            # Add timestamp
            import datetime
            timestamp = datetime.datetime.now().strftime("%H:%M")
            self.chat_display.insert(tk.END, f"[{timestamp}] ", "timestamp")
            
            # Add message
            self.chat_display.insert(tk.END, f"{message}\\n", tag)
            
            # Scroll to bottom
            self.chat_display.see(tk.END)
            
            self.chat_display.configure(state=tk.DISABLED)
            
            # Store in history
            self.chat_history.append({
                'timestamp': timestamp,
                'message': message,
                'tag': tag
            })
            
        except Exception as e:
            self.logger.error(f"Error adding chat message: {e}")
    
    def _update_status(self, status: str, color: str = "black"):
        """Update status label"""
        try:
            if self.status_label:
                self.status_label.configure(text=status, foreground=color)
        except Exception as e:
            self.logger.error(f"Error updating status: {e}")
    
    def _on_window_close(self):
        """Handle window close event"""
        self.hide()  # Hide instead of destroying
    
    def show(self):
        """Show the GUI window"""
        try:
            if self.root:
                self.root.deiconify()
                self.root.lift()
                self.root.attributes('-topmost', True)
                self.root.after(100, lambda: self.root.attributes('-topmost', False))
                self.is_visible = True
                self.input_entry.focus_set()
                self.logger.info("GUI window shown")
        except Exception as e:
            self.logger.error(f"Error showing GUI: {e}")
    
    def hide(self):
        """Hide the GUI window"""
        try:
            if self.root:
                self.root.withdraw()
                self.is_visible = False
                self.logger.info("GUI window hidden")
        except Exception as e:
            self.logger.error(f"Error hiding GUI: {e}")
    
    def destroy(self):
        """Destroy the GUI window"""
        try:
            if self.root:
                self.root.quit()
                self.root.destroy()
                self.logger.info("GUI destroyed")
        except Exception as e:
            self.logger.error(f"Error destroying GUI: {e}")
    
    def is_gui_visible(self) -> bool:
        """Check if GUI is currently visible"""
        return self.is_visible
'''

print("Created gui_manager.py - Tkinter popup interface")

# system_tray.py - System tray management
system_tray_content = '''"""
System Tray Manager for Cherry AI Assistant
Handles background operation and system tray integration
"""

import logging
import threading
import os
from typing import Callable, Dict, Any, Optional
from pathlib import Path

try:
    import pystray
    from PIL import Image, ImageDraw
except ImportError:
    print("System tray dependencies not installed. Install with:")
    print("pip install pystray pillow")
    import sys
    sys.exit(1)

class SystemTrayManager:
    """Manages system tray integration for Cherry"""
    
    def __init__(self, show_callback: Callable, quit_callback: Callable, config: Dict[str, Any]):
        self.show_callback = show_callback
        self.quit_callback = quit_callback
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Tray components
        self.icon = None
        self.tray_thread = None
        self.is_running = False
        
        # Create tray icon
        self.tray_image = self._create_icon_image()
        
    def _create_icon_image(self) -> Image.Image:
        """Create the system tray icon image"""
        try:
            # Try to load custom icon first
            icon_path = self.config['ASSETS_DIR'] / 'cherry_icon.png'
            
            if icon_path.exists():
                return Image.open(icon_path)
            else:
                # Create a simple cherry icon
                return self._create_simple_cherry_icon()
                
        except Exception as e:
            self.logger.warning(f"Error loading icon, creating simple icon: {e}")
            return self._create_simple_cherry_icon()
    
    def _create_simple_cherry_icon(self) -> Image.Image:
        """Create a simple cherry icon"""
        # Create a 64x64 image with cherry color
        image = Image.new('RGB', (64, 64), color='white')
        draw = ImageDraw.Draw(image)
        
        # Draw a simple cherry shape
        # Cherry body (circle)
        draw.ellipse([20, 25, 44, 49], fill='#DC143C', outline='#8B0000', width=2)
        
        # Cherry stem
        draw.line([32, 25, 32, 15], fill='#228B22', width=3)
        draw.line([32, 15, 35, 10], fill='#228B22', width=2)
        
        # Add a small leaf
        draw.ellipse([35, 12, 42, 18], fill='#32CD32', outline='#228B22')
        
        return image
    
    def _create_menu(self) -> pystray.Menu:
        """Create the system tray context menu"""
        return pystray.Menu(
            pystray.MenuItem("🍒 Show Cherry", self._on_show_click, default=True),
            pystray.MenuItem("Status", self._on_status_click),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Settings", self._on_settings_click),
            pystray.MenuItem("Help", self._on_help_click),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quit Cherry", self._on_quit_click)
        )
    
    def start(self):
        """Start the system tray"""
        try:
            if self.is_running:
                return
            
            self.is_running = True
            
            # Create the system tray icon
            self.icon = pystray.Icon(
                "cherry",
                self.tray_image,
                "Cherry AI Assistant",
                self._create_menu()
            )
            
            # Start the tray in a separate thread
            self.tray_thread = threading.Thread(
                target=self._run_tray,
                daemon=True
            )
            self.tray_thread.start()
            
            self.logger.info("System tray started")
            
        except Exception as e:
            self.logger.error(f"Error starting system tray: {e}")
    
    def _run_tray(self):
        """Run the system tray (blocking)"""
        try:
            self.icon.run()
        except Exception as e:
            self.logger.error(f"Error running system tray: {e}")
    
    def stop(self):
        """Stop the system tray"""
        try:
            self.is_running = False
            
            if self.icon:
                self.icon.stop()
            
            if self.tray_thread and self.tray_thread.is_alive():
                self.tray_thread.join(timeout=2)
            
            self.logger.info("System tray stopped")
            
        except Exception as e:
            self.logger.error(f"Error stopping system tray: {e}")
    
    def _on_show_click(self, icon, item):
        """Handle show menu item click"""
        try:
            if self.show_callback:
                self.show_callback()
        except Exception as e:
            self.logger.error(f"Error handling show click: {e}")
    
    def _on_status_click(self, icon, item):
        """Handle status menu item click"""
        try:
            # Show status notification
            self.show_notification(
                "Cherry Status",
                "Cherry AI Assistant is running in the background"
            )
        except Exception as e:
            self.logger.error(f"Error handling status click: {e}")
    
    def _on_settings_click(self, icon, item):
        """Handle settings menu item click"""
        try:
            # Show Cherry interface for settings
            if self.show_callback:
                self.show_callback()
        except Exception as e:
            self.logger.error(f"Error handling settings click: {e}")
    
    def _on_help_click(self, icon, item):
        """Handle help menu item click"""
        try:
            help_text = """Cherry AI Assistant Help:
            
🍒 Voice Commands: Say "Cherry" to activate voice mode
⌨️ Hotkeys: Ctrl+Alt+C to show interface
🖱️ Desktop Control: Cherry can control your mouse and keyboard
📷 Screenshots: Cherry can take and analyze screenshots
🔍 Web Search: Ask Cherry to search for information
📁 File Operations: Cherry can create and manage files

For more help, say "Cherry, what can you do?" or type it in the interface."""
            
            self.show_notification("Cherry Help", help_text)
            
        except Exception as e:
            self.logger.error(f"Error handling help click: {e}")
    
    def _on_quit_click(self, icon, item):
        """Handle quit menu item click"""
        try:
            if self.quit_callback:
                self.quit_callback()
        except Exception as e:
            self.logger.error(f"Error handling quit click: {e}")
    
    def show_notification(self, title: str, message: str, timeout: int = 5):
        """Show a system notification"""
        try:
            if self.icon:
                self.icon.notify(message, title)
                self.logger.info(f"Notification shown: {title}")
        except Exception as e:
            self.logger.error(f"Error showing notification: {e}")
    
    def update_icon(self, status: str = "normal"):
        """Update the tray icon based on status"""
        try:
            if status == "listening":
                # Create listening icon (red dot)
                icon_image = self.tray_image.copy()
                draw = ImageDraw.Draw(icon_image)
                draw.ellipse([45, 5, 55, 15], fill='red')
                
            elif status == "processing":
                # Create processing icon (orange dot)
                icon_image = self.tray_image.copy()
                draw = ImageDraw.Draw(icon_image)
                draw.ellipse([45, 5, 55, 15], fill='orange')
                
            else:
                # Normal icon
                icon_image = self.tray_image
            
            if self.icon:
                self.icon.icon = icon_image
                
        except Exception as e:
            self.logger.error(f"Error updating icon: {e}")
    
    def update_tooltip(self, tooltip: str):
        """Update the tray icon tooltip"""
        try:
            if self.icon:
                self.icon.title = tooltip
        except Exception as e:
            self.logger.error(f"Error updating tooltip: {e}")
    
    def is_tray_running(self) -> bool:
        """Check if system tray is running"""
        return self.is_running and self.icon is not None
'''

print("Created system_tray.py - System tray management")

# hotkey_manager.py - Global hotkey detection
hotkey_manager_content = '''"""
Hotkey Manager for Cherry AI Assistant
Handles global hotkey detection and registration
"""

import logging
import threading
from typing import Dict, Callable, Any

try:
    from pynput import keyboard
except ImportError:
    print("Hotkey dependencies not installed. Install with:")
    print("pip install pynput")
    import sys
    sys.exit(1)

class HotkeyManager:
    """Manages global hotkeys for Cherry"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Hotkey listener
        self.listener = None
        self.hotkeys = {}
        self.is_listening = False
        
        # Hotkey state tracking
        self.pressed_keys = set()
        
    def register_hotkeys(self, hotkey_map: Dict[str, Callable]):
        """Register global hotkeys"""
        try:
            self.hotkeys = {}
            
            for hotkey_str, callback in hotkey_map.items():
                try:
                    # Parse hotkey string
                    hotkey = keyboard.HotKey.parse(hotkey_str)
                    self.hotkeys[frozenset(hotkey)] = {
                        'callback': callback,
                        'hotkey_str': hotkey_str
                    }
                    
                    self.logger.info(f"Registered hotkey: {hotkey_str}")
                    
                except Exception as e:
                    self.logger.error(f"Error parsing hotkey '{hotkey_str}': {e}")
            
            # Start listening if not already
            if not self.is_listening:
                self.start_listening()
                
        except Exception as e:
            self.logger.error(f"Error registering hotkeys: {e}")
    
    def start_listening(self):
        """Start listening for global hotkeys"""
        try:
            if self.is_listening:
                return
            
            self.is_listening = True
            
            # Create keyboard listener
            self.listener = keyboard.Listener(
                on_press=self._on_key_press,
                on_release=self._on_key_release,
                suppress=False  # Don't suppress keys
            )
            
            # Start listener in daemon thread
            self.listener.start()
            
            self.logger.info("Hotkey listener started")
            
        except Exception as e:
            self.logger.error(f"Error starting hotkey listener: {e}")
    
    def stop_listening(self):
        """Stop listening for hotkeys"""
        try:
            if not self.is_listening:
                return
            
            self.is_listening = False
            
            if self.listener:
                self.listener.stop()
                self.listener = None
            
            self.pressed_keys.clear()
            
            self.logger.info("Hotkey listener stopped")
            
        except Exception as e:
            self.logger.error(f"Error stopping hotkey listener: {e}")
    
    def _on_key_press(self, key):
        """Handle key press event"""
        try:
            # Normalize the key
            normalized_key = self._normalize_key(key)
            self.pressed_keys.add(normalized_key)
            
            # Check for hotkey matches
            self._check_hotkey_match()
            
        except Exception as e:
            self.logger.error(f"Error handling key press: {e}")
    
    def _on_key_release(self, key):
        """Handle key release event"""
        try:
            # Normalize the key
            normalized_key = self._normalize_key(key)
            self.pressed_keys.discard(normalized_key)
            
        except Exception as e:
            self.logger.error(f"Error handling key release: {e}")
    
    def _normalize_key(self, key):
        """Normalize key for comparison"""
        try:
            if hasattr(key, 'char') and key.char is not None:
                return keyboard.KeyCode.from_char(key.char.lower())
            else:
                return key
        except Exception:
            return key
    
    def _check_hotkey_match(self):
        """Check if current pressed keys match any registered hotkey"""
        try:
            current_keys = frozenset(self.pressed_keys)
            
            for hotkey_keys, hotkey_info in self.hotkeys.items():
                if current_keys == hotkey_keys:
                    self.logger.info(f"Hotkey triggered: {hotkey_info['hotkey_str']}")
                    
                    # Execute callback in separate thread to avoid blocking
                    callback_thread = threading.Thread(
                        target=hotkey_info['callback'],
                        daemon=True
                    )
                    callback_thread.start()
                    break
                    
        except Exception as e:
            self.logger.error(f"Error checking hotkey match: {e}")
    
    def add_hotkey(self, hotkey_str: str, callback: Callable):
        """Add a single hotkey"""
        try:
            hotkey_map = {hotkey_str: callback}
            self.register_hotkeys({**self.hotkeys_as_dict(), **hotkey_map})
            
        except Exception as e:
            self.logger.error(f"Error adding hotkey: {e}")
    
    def remove_hotkey(self, hotkey_str: str):
        """Remove a hotkey"""
        try:
            hotkey = keyboard.HotKey.parse(hotkey_str)
            hotkey_key = frozenset(hotkey)
            
            if hotkey_key in self.hotkeys:
                del self.hotkeys[hotkey_key]
                self.logger.info(f"Removed hotkey: {hotkey_str}")
            else:
                self.logger.warning(f"Hotkey not found: {hotkey_str}")
                
        except Exception as e:
            self.logger.error(f"Error removing hotkey: {e}")
    
    def hotkeys_as_dict(self) -> Dict[str, Callable]:
        """Convert internal hotkey storage to simple dict"""
        result = {}
        for hotkey_keys, hotkey_info in self.hotkeys.items():
            result[hotkey_info['hotkey_str']] = hotkey_info['callback']
        return result
    
    def list_registered_hotkeys(self) -> list:
        """Get list of registered hotkey strings"""
        return [info['hotkey_str'] for info in self.hotkeys.values()]
    
    def is_hotkey_registered(self, hotkey_str: str) -> bool:
        """Check if a hotkey is registered"""
        try:
            hotkey = keyboard.HotKey.parse(hotkey_str)
            hotkey_key = frozenset(hotkey)
            return hotkey_key in self.hotkeys
        except:
            return False
    
    def stop(self):
        """Stop the hotkey manager"""
        self.stop_listening()
        self.logger.info("Hotkey manager stopped")
    
    def get_status(self) -> Dict[str, Any]:
        """Get hotkey manager status"""
        return {
            'is_listening': self.is_listening,
            'registered_hotkeys': self.list_registered_hotkeys(),
            'currently_pressed_keys': len(self.pressed_keys),
        }
'''

print("Created hotkey_manager.py - Global hotkey detection")

# Save all interface modules
with open('gui_manager.py', 'w') as f:
    f.write(gui_manager_content)

with open('system_tray.py', 'w') as f:
    f.write(system_tray_content)

with open('hotkey_manager.py', 'w') as f:
    f.write(hotkey_manager_content)

print("\nCompleted interface modules:")
print("✓ gui_manager.py - Tkinter popup interface")
print("✓ system_tray.py - System tray management")
print("✓ hotkey_manager.py - Global hotkey detection")