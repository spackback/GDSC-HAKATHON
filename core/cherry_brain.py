"""
Enhanced Cherry AI Brain with MCP Integration and Extended Action Time
Handles natural language understanding, task planning, and execution with MCP support
"""

import asyncio
import logging
import json
from typing import Callable, Dict, List, Optional, Any
import time
import os
try:
    import google.generativeai as genai
except ImportError:
    print("Google Generative AI not installed. Install with: pip install google-generativeai")
    import sys
    sys.exit(1)

from core.memory_manager import MemoryManager
from core.voice_processor import VoiceProcessor
from core.vision_system import VisionSystem
from core.desktop_controller import DesktopController
from core.mcp_client import MCPClient
from utils.file_handler import FileHandler
from utils.web_scraper import WebScraper


class CherryBrain:
    """Enhanced AI brain for Cherry Assistant with MCP integration and extended action time."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.gui_callback: Optional[Callable[[str, str], None]] = None

        # Initialize Gemini
        try:
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "config/swift-seeker-296907-0704a84f33f1.json"
            genai.configure(api_key=config.get('GEMINI_API_KEY', ''))
            self.model = genai.GenerativeModel(model_name=config.get('GEMINI_MODEL', 'gemini-1.5-flash'))
        except Exception as e:
            self.logger.error(f"Failed to initialize Gemini: {e}")
            self.model = None

        # Initialize components with error handling
        try:
            self.memory_manager = MemoryManager(config)
            self.voice_processor = VoiceProcessor(config)
            self.vision_system = VisionSystem(config)
            self.desktop_controller = DesktopController(config)
            self.file_handler = FileHandler(config)
            self.web_scraper = WebScraper(config)

            # Initialize MCP client
            self.mcp_client = MCPClient(config)

        except Exception as e:
            self.logger.error(f"Failed to initialize components: {e}")

        self.is_listening = False
        self.conversation_history = []

        # Enhanced loop prevention with extended timing
        self.last_spoken_text = None
        self.thinking_shown = False
        self.repeated_actions = {}
        self.consecutive_speak_count = 0
        self.last_screen_context = None
        self.context_unchanged_count = 0

        # Extended action timing configuration
        self.action_timeout = config.get('ACTION_TIMEOUT', 60)  # Extended to 60 seconds per action
        self.max_execution_time = config.get('MAX_EXECUTION_TIME', 900)  # 15 minutes total
        self.action_delay = config.get('ACTION_DELAY', 0.5)  # Increased delay between actions
        self.screen_analysis_delay = config.get('SCREEN_ANALYSIS_DELAY', 1.0)  # Time for screen updates

    def set_gui_callback(self, callback: Callable[[str, str], None]):
        self.gui_callback = callback

    async def initialize(self):
        """Initialize all components including MCP with proper error handling."""
        self.logger.info("Initializing Enhanced Cherry Brain with MCP...")

        try:
            if hasattr(self.memory_manager, 'initialize'):
                await self.memory_manager.initialize()
        except Exception as e:
            self.logger.error(f"Failed to initialize memory manager: {e}")

        try:
            if hasattr(self.voice_processor, 'initialize'):
                await self.voice_processor.initialize()
        except Exception as e:
            self.logger.error(f"Failed to initialize voice processor: {e}")

        try:
            # Initialize MCP client
            if self.config.get('ENABLE_MCP', True):
                await self.mcp_client.initialize()
                if self.mcp_client.is_connected:
                    self.logger.info(f"MCP initialized with tools: {self.mcp_client.get_available_tools()}")
                else:
                    self.logger.warning("MCP initialization failed, continuing without MCP support")
        except Exception as e:
            self.logger.error(f"Failed to initialize MCP client: {e}")

        self.logger.info("Enhanced Cherry Brain initialized successfully!")

    def _build_enhanced_decision_prompt(self, goal: str, history: List[str], screen_context: str) -> str:
        """Build enhanced decision prompt with MCP tools and extended timing awareness."""
        recent_history = history[-8:] if len(history) > 8 else history  # More history for better context

        # Get available MCP tools
        mcp_tools = []
        if hasattr(self.mcp_client, 'is_connected') and self.mcp_client.is_connected:
            mcp_tools = self.mcp_client.get_available_tools()

        mcp_tools_text = ""
        if mcp_tools:
            mcp_tools_text = f'''

MCP Tools Available:
{chr(10).join(f"- {tool}: Use mcp_execute with tool='{tool}'" for tool in mcp_tools[:10])}
'''

        return f'''You are an intelligent AI assistant with extended execution time and advanced tool access.

EXECUTION GUIDELINES:
1. You have up to {self.action_timeout} seconds per action and {self.max_execution_time} seconds total
2. Take time to analyze the screen carefully after each action ({self.screen_analysis_delay}s delay)
3. Break complex tasks into smaller, manageable steps
4. Use MCP tools when available for enhanced capabilities
5. If unclear about the user's goal, ask for clarification ONCE only
6. Use 'finish' when the task is complete or if you encounter persistent errors

Standard Functions:
- open_application(app_name: str) - Opens an application
- open_website(url: str) - Opens a website
- search_web(query: str) - Searches the web
- type_text(text: str) - Types text
- press_key(key: str, modifier: Optional[str] = None) - Presses keys
- click_mouse(x: int, y: int) - Clicks at coordinates
- scroll(x: int, y: int, direction: str, clicks: int) - Scrolls at position
- drag_mouse(start_x: int, start_y: int, end_x: int, end_y: int) - Drags between points
- take_screenshot() - Takes a screenshot for analysis
- speak(text: str) - Speaks to user (use sparingly)
- wait(seconds: float) - Waits for specified time
- finish(summary: str) - Completes the task

MCP Functions:
- mcp_execute(tool: str, arguments: dict) - Execute MCP tool{mcp_tools_text}

User's Goal: "{goal}"

Recent Action History:
{chr(10).join(f"- {action}" for action in recent_history)}

Current Screen Analysis: {screen_context[:1000]}...

IMPORTANT: Take your time, analyze the screen thoroughly, and ensure each action moves toward the goal. 
Respond with clean JSON only: {{"function": "function_name", "parameters": {{"key": "value"}}}} '''

    async def _decide_next_action(self, goal: str, history: List[str]) -> Optional[Dict[str, Any]]:
        """Enhanced decision making with extended timing and MCP awareness."""
        self.logger.info("Analyzing situation and deciding next action...")

        # Check if we're stuck in a loop (more lenient with extended timing)
        if len(history) >= 5:
            recent_actions = [h.split("Action: ")[1].split(",")[0] if "Action: " in h else h for h in history[-5:]]
            unique_actions = len(set(recent_actions))
            if unique_actions <= 2 and len(recent_actions) >= 5:
                self.logger.warning("Detected potential loop, will try different approach")
                return {"function": "speak", "parameters": {"text": "I notice I'm repeating actions. Let me try a different approach or ask for clarification."}}

        # Get enhanced screen context with more time
        try:
            await asyncio.sleep(self.screen_analysis_delay)  # Wait for screen to update
            screen_context = await self.vision_system.get_screen_context()
            if not screen_context:
                screen_context = "Unable to analyze screen - taking screenshot for analysis"
                # Try to take a screenshot
                try:
                    screenshot_data = await self.vision_system.take_screenshot()
                    if screenshot_data and screenshot_data.get('path'):
                        screen_context += f" - Screenshot saved to {screenshot_data['path']}"
                except:
                    pass

            # Enhanced context change detection with more patience
            if screen_context == self.last_screen_context:
                self.context_unchanged_count += 1
                # More patience with extended timing
                if self.context_unchanged_count >= 6:  # Increased from 3
                    return {"function": "finish", "parameters": {"summary": "Screen hasn't changed after multiple attempts with extended wait times. Task may be complete or needs different approach."}}
            else:
                self.context_unchanged_count = 0

            self.last_screen_context = screen_context

        except Exception as e:
            self.logger.error(f"Error getting screen context: {e}")
            screen_context = "Error analyzing screen - will attempt action based on goal"

        if not self.model:
            return {"function": "speak", "parameters": {"text": "AI model not available"}}

        prompt = self._build_enhanced_decision_prompt(goal, history, screen_context)

        try:
            # Use higher temperature for more creative problem-solving
            response = await self.model.generate_content_async(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.8,
                    top_k=40,
                    top_p=0.9,
                    max_output_tokens=2048,
                )
            )
            action_text = response.text.strip()
            self.logger.info(f"AI decision raw: {action_text}")

            # Extract JSON more robustly
            json_start = action_text.find('{')
            json_end = action_text.rfind('}')

            if json_start != -1 and json_end != -1:
                json_str = action_text[json_start:json_end+1]
                action = json.loads(json_str)

                # Validate action structure
                if 'function' not in action:
                    raise ValueError("No function specified in action")

                return action
            else:
                self.logger.error(f"No valid JSON found in AI response: {action_text}")
                return {"function": "finish", "parameters": {"summary": "I had trouble understanding the AI response format."}}

        except Exception as e:
            self.logger.error(f"Failed to decide next action: {e}")
            return {"function": "finish", "parameters": {"summary": f"I encountered an error in decision making: {str(e)}"}}

    async def process_input(self, user_input: str, context: Optional[Dict] = None):
        """Process user input with extended timing and MCP support."""
        start_time = time.time()
        self.logger.info(f"Starting enhanced task execution for: {user_input}")

        # Reset state for new task
        self.last_spoken_text = None
        self.thinking_shown = False
        self.repeated_actions = {}
        self.consecutive_speak_count = 0
        self.context_unchanged_count = 0
        self.last_screen_context = None

        if self.gui_callback:
            self.gui_callback("user", user_input)
            await self.speak("I'll work on that for you.", thinking=True)

        action_history = ["Task started with extended execution time"]
        max_steps = 25  # Increased from 10 for extended execution
        step_timeout = self.action_timeout

        for step in range(max_steps):
            current_time = time.time()
            elapsed_time = current_time - start_time

            # Check total execution time
            if elapsed_time > self.max_execution_time:
                self.logger.warning(f"Maximum execution time ({self.max_execution_time}s) reached")
                await self.speak(f"I've reached the maximum execution time of {self.max_execution_time//60} minutes. Let me summarize what I accomplished.")
                break

            self.logger.info(f"Step {step + 1}/{max_steps} - Elapsed time: {elapsed_time:.1f}s")

            # Get next action with timeout
            try:
                action = await asyncio.wait_for(
                    self._decide_next_action(user_input, action_history),
                    timeout=step_timeout
                )
            except asyncio.TimeoutError:
                self.logger.error(f"Action decision timed out after {step_timeout}s")
                await self.speak("I'm taking longer than expected to decide. Let me continue with the current approach.")
                continue

            if not action or 'function' not in action:
                self.logger.error("AI failed to provide a valid action.")
                await self.speak("I'm having trouble deciding what to do next.")
                break

            function_name = action['function']
            parameters = action.get('parameters', {})

            # Handle finish action
            if function_name == 'finish':
                summary = parameters.get('summary', "Task completed.")
                total_time = time.time() - start_time
                self.logger.info(f"Task finished in {total_time:.1f}s: {summary}")
                await self.speak(f"{summary} Task completed in {total_time:.1f} seconds.")
                break

            # Enhanced repeated action tracking with more patience
            action_key = f"{function_name}:{str(parameters)}"
            self.repeated_actions[action_key] = self.repeated_actions.get(action_key, 0) + 1

            if self.repeated_actions[action_key] > 4:  # Increased from 2
                self.logger.warning(f"Action repeated too many times: {action_key}")
                await self.speak("I'm repeating the same action. Let me try a different approach or take a screenshot to better understand the situation.")
                # Try to take a screenshot for better understanding
                try:
                    await self._execute_single_action("take_screenshot", {})
                    await asyncio.sleep(2.0)  # Give time to analyze
                except:
                    pass
                continue

            # Enhanced consecutive speak prevention
            if function_name == 'speak':
                self.consecutive_speak_count += 1
                if self.consecutive_speak_count > 3:  # Increased from 2
                    self.logger.warning("Too many consecutive speak actions")
                    await self.speak("I'll proceed with actions instead of asking more questions.")
                    continue
            else:
                self.consecutive_speak_count = 0

            # Execute action with extended timeout
            try:
                action_start_time = time.time()
                result = await asyncio.wait_for(
                    self._execute_single_action(function_name, parameters),
                    timeout=self.action_timeout
                )
                action_duration = time.time() - action_start_time

                result_str = str(result) if result is not None else "Completed"
                log_entry = f"Step {step + 1}: {function_name}({parameters}) -> {result_str[:100]} (took {action_duration:.1f}s)"
                action_history.append(log_entry)
                self.logger.info(log_entry)

                # Extended delay between actions for screen updates
                await asyncio.sleep(self.action_delay)

            except asyncio.TimeoutError:
                self.logger.error(f"Action {function_name} timed out after {self.action_timeout}s")
                await self.speak(f"The action {function_name} is taking longer than expected. I'll try a different approach.")
                error_entry = f"Step {step + 1}: {function_name} -> TIMEOUT after {self.action_timeout}s"
                action_history.append(error_entry)
                continue

            except Exception as e:
                self.logger.error(f"Error executing {function_name}: {e}")
                await self.speak(f"I encountered an error with {function_name}: {str(e)[:100]}. I'll try something else.")
                error_entry = f"Step {step + 1}: {function_name} -> ERROR: {str(e)[:100]}"
                action_history.append(error_entry)

        else:
            # Max steps reached
            total_time = time.time() - start_time
            self.logger.warning(f"Task reached maximum steps ({max_steps}) after {total_time:.1f}s")
            await self.speak(f"I've completed {max_steps} steps in {total_time:.1f} seconds. The task may need to be broken down further or require manual intervention.")

    async def _execute_single_action(self, function_name: str, parameters: Dict) -> Any:
        """Execute a single action with MCP support and enhanced error handling."""
        action_map = {
            'open_application': self._safe_open_application,
            'open_website': self._safe_open_website,
            'search_web': self._safe_search_web,
            'type_text': self._safe_type_text,
            'press_key': self._safe_press_key,
            'click_mouse': self._safe_click_mouse,
            'scroll': self._safe_scroll,
            'drag_mouse': self._safe_drag_mouse,
            'take_screenshot': self._safe_take_screenshot,
            'wait': self._safe_wait,
            'speak': self.speak,
            'mcp_execute': self._safe_mcp_execute,
        }

        if function_name in action_map:
            if function_name != 'speak':
                await self.speak(f"Executing {function_name.replace('_', ' ')}")
            return await action_map[function_name](**parameters)
        else:
            raise ValueError(f"Unknown function: {function_name}")

    # Enhanced safe wrapper methods
    async def _safe_open_application(self, app_name: str) -> str:
        try:
            result = await self.desktop_controller.open_application(app_name)
            await asyncio.sleep(3.0)  # Extended wait for app to load
            return f"Opened {app_name}"
        except Exception as e:
            raise Exception(f"Failed to open {app_name}: {e}")

    async def _safe_open_website(self, url: str) -> str:
        try:
            result = await self.desktop_controller.open_website(url)
            await asyncio.sleep(4.0)  # Extended wait for page to load
            return f"Opened website {url}"
        except Exception as e:
            raise Exception(f"Failed to open {url}: {e}")

    async def _safe_search_web(self, query: str) -> str:
        try:
            results = await self.web_scraper.search(query)
            return f"Searched for: {query}"
        except Exception as e:
            raise Exception(f"Failed to search for {query}: {e}")

    async def _safe_type_text(self, text: str) -> str:
        try:
            await self.desktop_controller.type_text(text)
            await asyncio.sleep(0.5)  # Wait for typing to complete
            return f"Typed: {text[:50]}..."
        except Exception as e:
            raise Exception(f"Failed to type text: {e}")

    async def _safe_press_key(self, key: str, modifier: Optional[str] = None) -> str:
        try:
            await self.desktop_controller.press_key(key, modifier)
            await asyncio.sleep(0.5)  # Wait for key press to register
            return f"Pressed {modifier}+{key}" if modifier else f"Pressed {key}"
        except Exception as e:
            raise Exception(f"Failed to press key: {e}")

    async def _safe_click_mouse(self, x: int, y: int) -> str:
        try:
            await self.desktop_controller.click_mouse(x, y)
            await asyncio.sleep(1.0)  # Extended wait for click to register and screen to update
            return f"Clicked at ({x}, {y})"
        except Exception as e:
            raise Exception(f"Failed to click mouse: {e}")

    async def _safe_scroll(self, x: int, y: int, direction: str = 'up', clicks: int = 3) -> str:
        try:
            await self.desktop_controller.scroll(x, y, direction, clicks)
            await asyncio.sleep(1.0)  # Wait for scroll to complete
            return f"Scrolled {direction} {clicks} clicks at ({x}, {y})"
        except Exception as e:
            raise Exception(f"Failed to scroll: {e}")

    async def _safe_drag_mouse(self, start_x: int, start_y: int, end_x: int, end_y: int) -> str:
        try:
            await self.desktop_controller.drag_mouse(start_x, start_y, end_x, end_y)
            await asyncio.sleep(1.5)  # Extended wait for drag operation
            return f"Dragged from ({start_x}, {start_y}) to ({end_x}, {end_y})"
        except Exception as e:
            raise Exception(f"Failed to drag mouse: {e}")

    async def _safe_take_screenshot(self) -> str:
        try:
            screenshot_data = await self.vision_system.take_screenshot()
            if screenshot_data and screenshot_data.get('path'):
                return f"Screenshot saved to {screenshot_data['path']}"
            else:
                return "Screenshot taken but path not available"
        except Exception as e:
            raise Exception(f"Failed to take screenshot: {e}")

    async def _safe_wait(self, seconds: float) -> str:
        try:
            await asyncio.sleep(max(0.1, min(30.0, seconds)))  # Clamp between 0.1 and 30 seconds
            return f"Waited {seconds} seconds"
        except Exception as e:
            raise Exception(f"Failed to wait: {e}")

    async def _safe_mcp_execute(self, tool: str, arguments: Dict[str, Any]) -> str:
        """Execute MCP tool safely"""
        try:
            if not hasattr(self.mcp_client, 'is_connected') or not self.mcp_client.is_connected:
                raise Exception("MCP client not connected")

            result = await self.mcp_client.execute_tool(tool, arguments)
            return f"MCP tool '{tool}' executed successfully: {str(result)[:200]}"
        except Exception as e:
            raise Exception(f"Failed to execute MCP tool '{tool}': {e}")

    async def start_listening(self):
        """Start voice listening."""
        try:
            self.is_listening = True
            await self.voice_processor.start_listening(self._handle_voice_input)
        except Exception as e:
            self.logger.error(f"Failed to start listening: {e}")

    async def stop_listening(self):
        """Stop voice listening."""
        try:
            self.is_listening = False
            await self.voice_processor.stop_listening()
        except Exception as e:
            self.logger.error(f"Failed to stop listening: {e}")

    async def _handle_voice_input(self, voice_text: str):
        """Handle voice input."""
        if voice_text and self.is_listening:
            await self.process_input(voice_text, {'input_type': 'voice'})

    async def speak(self, text: str, thinking=False):
        """Speak with improved duplicate prevention."""
        # Suppress repeated thinking messages
        if thinking and self.thinking_shown:
            return
        if thinking:
            self.thinking_shown = True

        # Suppress exact duplicate messages
        if text == self.last_spoken_text:
            return

        self.last_spoken_text = text

        try:
            if self.gui_callback:
                self.gui_callback("cherry", text)

            if hasattr(self.voice_processor, 'speak'):
                await self.voice_processor.speak(text)
            else:
                await asyncio.sleep(0.1)  # Small delay if no voice processor

        except Exception as e:
            self.logger.error(f"Failed to speak: {e}")

    async def cleanup(self):
        """Clean up resources including MCP."""
        self.logger.info("Cleaning up Enhanced Cherry Brain...")
        try:
            await self.stop_listening()
            if hasattr(self.memory_manager, 'cleanup'):
                await self.memory_manager.cleanup()
            if hasattr(self.voice_processor, 'cleanup'):
                await self.voice_processor.cleanup()
            if hasattr(self.mcp_client, 'cleanup'):
                await self.mcp_client.cleanup()
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
