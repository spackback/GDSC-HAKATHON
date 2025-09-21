"""
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
