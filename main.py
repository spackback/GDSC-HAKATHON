#!/usr/bin/env python3
"""
Cherry AI Desktop Assistant
Main application entry point - Manages asyncio event loop and GUI
"""

import asyncio
import logging
import sys
import threading
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config.settings import load_config
from core.cherry_brain import CherryBrain
from interface.gui_manager import GUIManager
from interface.hotkey_manager import HotkeyManager
from interface.system_tray import SystemTrayManager
from utils.logger import setup_logging

class CherryAssistant:
    """Main application class orchestrating all components."""

    def __init__(self, event_loop):
        self.config = load_config()
        self.logger = setup_logging()
        self.event_loop = event_loop
        
        self.brain = None
        self.gui_manager = None
        self.tray_manager = None
        self.hotkey_manager = None

    def initialize(self):
        """Initializes all components. Called from the main thread."""
        self.logger.info("Initializing Cherry AI Assistant...")

        self.brain = CherryBrain(self.config)
        self.gui_manager = GUIManager(self.brain, self.config, self.event_loop)
        self.brain.set_gui_callback(self.gui_manager.add_conversation_message)

        future = asyncio.run_coroutine_threadsafe(self.brain.initialize(), self.event_loop)
        future.result()  # Wait for async initialization to complete

        self.gui_manager.initialize()

        # Pass the event loop to the SystemTrayManager
        self.tray_manager = SystemTrayManager(self.show_gui, self.quit_application, self.config, self.event_loop)
        self.hotkey_manager = HotkeyManager(self.config)
        self.hotkey_manager.register_hotkeys({
            '<ctrl>+<alt>+c': self.show_gui,
            '<ctrl>+<alt>+q': self.quit_application
        })

        self.logger.info("Cherry AI Assistant initialized successfully!")

    def run(self):
        """Starts the application, hotkeys, and the main GUI loop."""
        self.tray_manager.start()
        self.logger.info("Cherry AI Assistant is now running...")
        if self.gui_manager and self.gui_manager.root:
            self.gui_manager.root.mainloop()

    def show_gui(self):
        """Thread-safe method to show the GUI."""
        if self.gui_manager and self.gui_manager.root:
            self.gui_manager.root.after(0, self.gui_manager.show)

    def quit_application(self):
        """Gracefully shuts down the entire application."""
        self.logger.info("Shutting down Cherry AI Assistant...")

        if self.hotkey_manager:
            self.hotkey_manager.stop()
        if self.tray_manager:
            self.tray_manager.stop()

        if self.brain:
            asyncio.run_coroutine_threadsafe(self.brain.cleanup(), self.event_loop).result()

        self.event_loop.call_soon_threadsafe(self.event_loop.stop)
        
        if self.gui_manager and self.gui_manager.root:
            self.gui_manager.root.after(0, self.gui_manager.destroy)

def main():
    """Application entry point."""
    print("🍒 Starting Cherry AI Desktop Assistant...")

    loop = asyncio.get_event_loop()
    assistant = CherryAssistant(event_loop=loop)

    def run_asyncio_loop(loop):
        asyncio.set_event_loop(loop)
        loop.run_forever()

    asyncio_thread = threading.Thread(target=run_asyncio_loop, args=(loop,), daemon=True)
    asyncio_thread.start()

    try:
        assistant.initialize()
        assistant.run()
    except (KeyboardInterrupt, SystemExit):
        pass
    except Exception as e:
        logging.getLogger().critical(f"Fatal error in main thread: {e}", exc_info=True)
    finally:
        print("\n🍒 Shutting down...")
        if assistant.gui_manager and assistant.gui_manager.root.winfo_exists():
             assistant.quit_application()
        asyncio_thread.join(timeout=5)
        print("\n🍒 Cherry AI Assistant shut down gracefully.")

if __name__ == "__main__":
    main()
