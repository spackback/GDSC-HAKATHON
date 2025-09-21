"""
Task Planner for Cherry AI Assistant
Breaks down complex user commands into a sequence of executable steps.
"""

import json
import logging
from typing import Dict, List, Any, Optional

import google.generativeai as genai

class TaskPlanner:
    """Deconstructs user requests into actionable plans using the Gemini API."""

    def __init__(self, config: Dict[str, Any], model: genai.GenerativeModel):
        self.config = config
        self.model = model
        self.logger = logging.getLogger(__name__)

    def _build_planning_prompt(self, user_input: str, context: Optional[Dict]) -> str:
        """Builds a detailed prompt to guide the AI in creating a step-by-step plan."""
        return f"""You are a task planner for an AI assistant. Your job is to take a user's request and break it down into a clear, step-by-step plan in JSON format. The assistant will then execute this plan.

Here are the functions the assistant can perform:

- `open_application(app_name: str)`: Opens a local application (e.g., 'notepad', 'discord').
- `open_website(url: str)`: Opens a specified URL in the browser.
- `search_web(query: str)`: Searches the web for a given query.
- `type_text(text: str, interval: float = 0.05)`: Types the given text.
- `press_key(key: str, modifier: Optional[str] = None)`: Presses a single key (e.g., 'enter', 'f5') or a combination (e.g., key='c', modifier='ctrl').
- `click_mouse(x: int, y: int, button: str = 'left')`: Clicks the mouse at a specific coordinate. (Note: Use this sparingly, as finding coordinates is hard. Prefer keyboard navigation.)
- `analyze_screen()`: Captures the screen and returns a description of the visible elements. This is useful for finding where to click or what to do next.
- `wait(seconds: int)`: Pauses for a specified number of seconds.

User Request: "{user_input}"

Context: {json.dumps(context)}

Based on the user's request and the available functions, create a JSON array of steps to accomplish the goal. Each step should be an object with `"function"` and `"parameters"`.

Example Plan for: "Open notepad and type hello world."
[
  {{
    "function": "open_application",
    "parameters": {{"app_name": "notepad"}}
  }},
  {{
    "function": "wait",
    "parameters": {{"seconds": 2}}
  }},
  {{
    "function": "type_text",
    "parameters": {{"text": "hello world"}}
  }}
]

Now, generate the plan for the user's request.
"""

    async def create_plan(self, user_input: str, context: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """Creates a structured plan from the user's input."""
        self.logger.info(f"Creating a plan for input: '{user_input}'")
        prompt = self._build_planning_prompt(user_input, context)

        try:
            response = await self.model.generate_content_async(prompt)
            
            plan_text = response.text.strip()
            # More robust JSON extraction
            json_start = plan_text.find('[')
            json_end = plan_text.rfind(']')
            if json_start != -1 and json_end != -1:
                plan_text = plan_text[json_start:json_end+1]
            
            plan = json.loads(plan_text)
            self.logger.info(f"Generated plan: {plan}")
            return plan
        except (json.JSONDecodeError, Exception) as e:
            self.logger.error(f"Failed to create or parse plan: {e}")
            return [
                {{
                    "function": "speak",
                    "parameters": {{"text": "I had trouble creating a plan for that. Please try rephrasing your request."}}
                }}
            ]
