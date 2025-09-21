"""
System Tray Manager for Cherry AI Assistant
Handles background operation and system tray integration
"""

import logging
import threading
from typing import Callable, Dict, Any
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

    def __init__(self, show_callback: Callable, quit_callback: Callable, config: Dict[str, Any], event_loop):
        self.show_callback = show_callback
        self.quit_callback = quit_callback
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.event_loop = event_loop  # Explicitly passed from the main thread

        self.icon = None
        self.tray_thread = None
        self.is_running = False

        self.tray_image = self._create_icon_image()

    def _create_icon_image(self) -> Image.Image:
        """Create the system tray icon image"""
        try:
            icon_path = self.config['ASSETS_DIR'] / 'cherry_icon.png'
            if icon_path.exists():
                return Image.open(icon_path)
            else:
                return self._create_simple_cherry_icon()
        except Exception as e:
            self.logger.warning(f"Error loading icon, creating simple icon: {e}")
            return self._create_simple_cherry_icon()

    def _create_simple_cherry_icon(self) -> Image.Image:
        """Create a simple cherry icon for the tray."""
        image = Image.new('RGB', (64, 64), color='white')
        draw = ImageDraw.Draw(image)
        draw.ellipse([20, 25, 44, 49], fill='#DC143C', outline='#8B0000', width=2)
        draw.line([32, 25, 32, 15], fill='#228B22', width=3)
        draw.line([32, 15, 35, 10], fill='#228B22', width=2)
        draw.ellipse([35, 12, 42, 18], fill='#32CD32', outline='#228B22')
        return image

    def _create_menu(self) -> pystray.Menu:
        """Create the system tray context menu."""
        return pystray.Menu(
            pystray.MenuItem("🍒 Show Cherry", self._on_show_click, default=True),
            pystray.MenuItem("Status: Running", None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quit Cherry", self._on_quit_click)
        )

    def start(self):
        """Start the system tray icon in a separate thread."""
        if self.is_running:
            return
        try:
            self.is_running = True
            self.icon = pystray.Icon(
                "cherry",
                self.tray_image,
                "Cherry AI Assistant",
                self._create_menu()
            )

            self.tray_thread = threading.Thread(target=self.icon.run, daemon=True)
            self.tray_thread.start()
            self.logger.info("System tray started")

        except Exception as e:
            self.logger.error(f"Error starting system tray: {e}", exc_info=True)

    def stop(self):
        """Stop the system tray icon."""
        if self.icon:
            self.icon.stop()
        self.is_running = False
        self.logger.info("System tray stopped")

    def _on_show_click(self, icon, item):
        """Handle show menu item click in a thread-safe way."""
        if self.show_callback and self.event_loop.is_running():
            # Use root.after to delegate to the main GUI thread
            self.show_callback()

    def _on_quit_click(self, icon, item):
        """Handle quit menu item click in a thread-safe way."""
        self.logger.info("Quit requested from system tray.")
        if self.quit_callback and self.event_loop.is_running():
            # Schedule the quit callback on the main GUI/app thread
            self.quit_callback()
