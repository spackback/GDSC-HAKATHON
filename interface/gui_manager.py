import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import logging
import threading
import asyncio
from typing import Callable, Dict, Any

class GUIManager:
    """Manages the Cherry AI Assistant GUI interface"""

    def __init__(self, cherry_brain, config: Dict[str, Any], event_loop):
        self.cherry_brain = cherry_brain
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.event_loop = event_loop
        self.root = None
        self.is_visible = False
        self.chat_display = None
        self.input_entry = None
        self.send_button = None
        self.status_label = None
        self.voice_button = None
        self.chat_history = []

    def initialize(self):
        """Initialize the GUI in the main thread"""
        try:
            self._create_gui()
            self.logger.info("GUI manager initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize GUI: {e}")

    def _create_gui(self):
        try:
            self.root = tk.Tk()
            self.root.title("🍒 Cherry AI Assistant")
            self.root.geometry("500x600")
            self.root.withdraw()  # Start hidden

            try:
                icon_path = self.config['ASSETS_DIR'] / 'cherry_icon.ico'
                if icon_path.exists():
                    self.root.iconbitmap(str(icon_path))
            except:
                pass

            style = ttk.Style()
            style.theme_use('clam')
            self.root.configure(bg='#f0f0f0')
            self._create_widgets()
            self._setup_layout()
            self._bind_events()
            self._center_window()

        except Exception as e:
            self.logger.error(f"Error creating GUI: {e}")

    def _create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        title_label = ttk.Label(main_frame, text="🍒 Cherry AI Assistant", font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        self.status_label = ttk.Label(main_frame, text="Ready", foreground="green")
        self.status_label.grid(row=1, column=0, columnspan=2, pady=(0, 10))
        chat_frame = ttk.LabelFrame(main_frame, text="Conversation", padding="5")
        chat_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        self.chat_display = scrolledtext.ScrolledText(chat_frame, wrap=tk.WORD, width=50, height=20,
                                                      font=('Arial', 10), state=tk.DISABLED)
        self.chat_display.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        input_frame = ttk.Frame(main_frame)
        input_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        self.input_entry = ttk.Entry(input_frame, font=('Arial', 10))
        self.input_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        self.send_button = ttk.Button(input_frame, text="Send", command=self._on_send_click)
        self.send_button.grid(row=0, column=1)
        self.voice_button = ttk.Button(input_frame, text="🎤 Voice", command=self._on_voice_click)
        self.voice_button.grid(row=0, column=2, padx=(5, 0))
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=4, column=0, columnspan=2, pady=(0, 10))
        screenshot_btn = ttk.Button(control_frame, text="📷 Screenshot", command=self._on_screenshot_click)
        screenshot_btn.grid(row=0, column=0, padx=(0, 5))
        clear_btn = ttk.Button(control_frame, text="🗑️ Clear", command=self._on_clear_click)
        clear_btn.grid(row=0, column=1, padx=(0, 5))
        settings_btn = ttk.Button(control_frame, text="⚙️ Settings", command=self._on_settings_click)
        settings_btn.grid(row=0, column=2)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        input_frame.columnconfigure(0, weight=1)
        chat_frame.columnconfigure(0, weight=1)
        chat_frame.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

    def _setup_layout(self):
        self.chat_display.configure(state=tk.NORMAL)
        self.chat_display.tag_configure("user", foreground="#0066cc", font=('Arial', 10, 'bold'))
        self.chat_display.tag_configure("cherry", foreground="#cc6600", font=('Arial', 10))
        self.chat_display.tag_configure("system", foreground="#666666", font=('Arial', 9, 'italic'))
        self.chat_display.tag_configure("timestamp", foreground="#888888", font=('Arial', 8))
        self.chat_display.configure(state=tk.DISABLED)

    def _bind_events(self):
        self.input_entry.bind('<Return>', lambda e: self._on_send_click())
        self.root.protocol("WM_DELETE_WINDOW", self._on_window_close)
        self.root.bind('<Escape>', lambda e: self.hide())

    def _center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def _on_send_click(self):
        try:
            message = self.input_entry.get().strip()
            if message:
                self.input_entry.delete(0, tk.END)
                self._process_user_input(message)
        except Exception as e:
            self.logger.error(f"Error handling send click: {e}")

    def _on_voice_click(self):
        try:
            if hasattr(self.cherry_brain, 'is_listening') and self.cherry_brain.is_listening:
                asyncio.run_coroutine_threadsafe(
                    self.cherry_brain.stop_listening(),
                    self.event_loop
                )
                self.voice_button.configure(text="🎤 Voice")
                self._add_system_message("Voice listening stopped")
            else:
                asyncio.run_coroutine_threadsafe(
                    self.cherry_brain.start_listening(),
                    self.event_loop
                )
                self.voice_button.configure(text="🔴 Stop")
                self._add_system_message("Voice listening started...")
        except Exception as e:
            self.logger.error(f"Error handling voice click: {e}")
            self._add_system_message(f"Voice error: {str(e)}")

    def _on_screenshot_click(self):
        try:
            self._add_system_message("Taking screenshot...")
            self._process_user_input("take a screenshot")
        except Exception as e:
            self.logger.error(f"Error handling screenshot click: {e}")

    def _on_clear_click(self):
        try:
            self.chat_display.configure(state=tk.NORMAL)
            self.chat_display.delete(1.0, tk.END)
            self.chat_display.configure(state=tk.DISABLED)
            self.chat_history.clear()
            self._add_system_message("Chat cleared")
        except Exception as e:
            self.logger.error(f"Error clearing chat: {e}")

    def _on_settings_click(self):
        try:
            self._show_settings_dialog()
        except Exception as e:
            self.logger.error(f"Error opening settings: {e}")

    def _show_settings_dialog(self):
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Cherry Settings")
        settings_window.geometry("400x300")
        settings_window.transient(self.root)
        ttk.Label(settings_window, text="Settings", font=('Arial', 14, 'bold')).pack(pady=10)
        voice_frame = ttk.LabelFrame(settings_window, text="Voice Settings", padding="10")
        voice_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(voice_frame, text="Wake Word:").grid(row=0, column=0, sticky=tk.W)
        wake_word_var = tk.StringVar(value=self.config['WAKE_WORD'])
        ttk.Entry(voice_frame, textvariable=wake_word_var).grid(row=0, column=1, sticky=(tk.W, tk.E))
        ttk.Button(settings_window, text="Close", command=settings_window.destroy).pack(pady=10)
        voice_frame.columnconfigure(1, weight=1)

    def _process_user_input(self, message: str):
        try:
            self._update_status("Processing...", "orange")
            def process_async():
                try:
                    future = asyncio.run_coroutine_threadsafe(
                        self.cherry_brain.process_input(message, {'input_type': 'text'}),
                        self.event_loop
                    )
                    future.result(timeout=20)  # Wait for completion
                    self.event_loop.call_soon_threadsafe(self._update_status, "Ready", "green")
                except Exception as e:
                    self.logger.error(f"Error processing input in thread: {e}")
                    self.event_loop.call_soon_threadsafe(self._add_system_message, f"Error: {str(e)}")
                    self.event_loop.call_soon_threadsafe(self._update_status, "Error", "red")

            threading.Thread(target=process_async, daemon=True).start()
        except Exception as e:
            self.logger.error(f"Error processing user input: {e}")
            self._add_system_message(f"Error: {str(e)}")

    def add_conversation_message(self, sender: str, message: str):
        """Public method to add a message to the conversation view, called via callback."""
        if sender == "user":
            self.event_loop.call_soon_threadsafe(self._add_user_message, message)
        elif sender == "cherry":
            self.event_loop.call_soon_threadsafe(self._add_cherry_message, message)
        else:
            self.event_loop.call_soon_threadsafe(self._add_system_message, message)

    def _add_user_message(self, message: str):
        self._add_chat_message(f"You: {message}", "user")

    def _add_cherry_message(self, message: str):
        self._add_chat_message(f"Cherry: {message}", "cherry")

    def _add_system_message(self, message: str):
        self._add_chat_message(f"System: {message}", "system")

    def _add_chat_message(self, message: str, tag: str):
        try:
            if not self.root:
                return
            self.chat_display.configure(state=tk.NORMAL)
            import datetime
            timestamp = datetime.datetime.now().strftime("%H:%M")
            self.chat_display.insert(tk.END, f"[{timestamp}] ", "timestamp")
            self.chat_display.insert(tk.END, f"{message}\n", tag)
            self.chat_display.see(tk.END)
            self.chat_display.configure(state=tk.DISABLED)
            self.chat_history.append({
                'timestamp': timestamp,
                'message': message,
                'tag': tag
            })
        except Exception as e:
            self.logger.error(f"Error adding chat message: {e}")

    def _update_status(self, status: str, color: str = "black"):
        try:
            if self.status_label:
                self.status_label.configure(text=status, foreground=color)
        except Exception as e:
            self.logger.error(f"Error updating status: {e}")

    def _on_window_close(self):
        self.hide()

    def show(self):
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
        try:
            if self.root:
                self.root.withdraw()
                self.is_visible = False
                self.logger.info("GUI window hidden")
        except Exception as e:
            self.logger.error(f"Error hiding GUI: {e}")

    def destroy(self):
        try:
            if self.root:
                self.root.quit()
                self.root.destroy()
                self.root = None # Avoid further updates
                self.logger.info("GUI destroyed")
        except Exception as e:
            self.logger.error(f"Error destroying GUI: {e}")

    def update_gui(self):
        """Update the GUI manually."""
        try:
            if self.root:
                self.root.update_idletasks()
                self.root.update()
        except tk.TclError as e:
            if "application has been destroyed" not in str(e):
                self.logger.error(f"Error updating GUI: {e}")

    def is_gui_visible(self) -> bool:
        return self.is_visible
