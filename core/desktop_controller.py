"""
Desktop Controller for Cherry AI Assistant  
Handles mouse, keyboard control and desktop automation
"""

import asyncio
import logging
import time
import webbrowser
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

    async def open_website(self, url: str) -> bool:
        """Open a website in the default web browser."""
        try:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            webbrowser.open(url, new=2)
            self.logger.info(f"Opened website: {url}")
            await asyncio.sleep(2)
            return True
        except Exception as e:
            self.logger.error(f"Error opening website {url}: {e}")
            return False

    async def open_application(self, app_name: str) -> bool:
        """Opens an application by searching in the Start Menu."""
        try:
            await self.press_key('win')
            await asyncio.sleep(0.7)

            await self.type_text(app_name)
            await asyncio.sleep(0.7)

            await self.press_key('enter')

            self.logger.info(f"Attempted to open application via Start Menu search: {app_name}")
            return True
        except Exception as e:
            self.logger.error(f"Error opening application {app_name}: {e}")
            return False

    async def move_mouse(self, x: int, y: int, smooth: bool = True) -> bool:
        """Move mouse to specified coordinates"""
        try:
            current_x, current_y = pyautogui.position()

            if smooth and self.movement_speed < 1.0:
                steps = 10
                for step in range(steps):
                    intermediate_x = current_x + (x - current_x) * (step + 1) / steps
                    intermediate_y = current_y + (y - current_y) * (step + 1) / steps
                    pyautogui.moveTo(intermediate_x, intermediate_y)
                    await asyncio.sleep(0.01 / self.movement_speed)
            else:
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
            if not self._check_click_safety():
                self.logger.warning("Click rate limit exceeded")
                return False

            if x is not None and y is not None:
                await self.move_mouse(x, y)

            pyautogui.click(clicks=clicks, interval=interval, button=button)

            self.click_count += clicks
            self.logger.info(f"Clicked {button} button {clicks} times at current position")
            return True

        except Exception as e:
            self.logger.error(f"Error clicking mouse: {e}")
            return False

    async def type_text(self, text: str, interval: float = 0.05) -> bool:
        """Type text with specified interval between characters"""
        try:
            clean_text = text.replace('\n', '\n').replace('\t', '\t')
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
                key_combination = [modifier, key]
                pyautogui.hotkey(*key_combination)
                self.logger.info(f"Pressed key combination: {modifier}+{key}")
            else:
                pyautogui.press(key)
                self.logger.info(f"Pressed key: {key}")

            return True

        except Exception as e:
            self.logger.error(f"Error pressing key: {e}")
            return False

    # ... (rest of the file remains the same) ...
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

    def _check_click_safety(self) -> bool:
        """Check if click rate is within safe limits"""
        current_time = time.time()
        if current_time - self.last_reset_time > 60:
            self.click_count = 0
            self.last_reset_time = current_time
        return self.click_count < self.max_clicks_per_minute

    async def cleanup(self):
        """Cleanup desktop controller resources"""
        self.logger.info("Desktop controller cleanup completed")
