"""
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
