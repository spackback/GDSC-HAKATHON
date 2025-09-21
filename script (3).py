# Create the core AI brain module - cherry_brain.py
cherry_brain_content = '''"""
Cherry AI Brain - Core AI processing with Gemini integration
Handles natural language understanding, task planning, and execution
"""

import asyncio
import logging
import json
from typing import Dict, List, Optional, Any
from datetime import datetime

try:
    import google.genai as genai
except ImportError:
    print("google-genai not installed. Install with: pip install google-genai")
    import sys
    sys.exit(1)

from core.memory_manager import MemoryManager
from core.voice_processor import VoiceProcessor
from core.vision_system import VisionSystem
from core.desktop_controller import DesktopController
from utils.file_handler import FileHandler
from utils.web_scraper import WebScraper

class CherryBrain:
    """Main AI brain for Cherry Assistant"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize Gemini client
        genai.configure(api_key=config['GEMINI_API_KEY'])
        self.model = genai.GenerativeModel(config['GEMINI_MODEL'])
        
        # Core components
        self.memory_manager = None
        self.voice_processor = None
        self.vision_system = None
        self.desktop_controller = None
        self.file_handler = None
        self.web_scraper = None
        
        # State management
        self.conversation_history = []
        self.current_task = None
        self.is_listening = False
        
        # System prompt for Cherry
        self.system_prompt = self._build_system_prompt()
    
    async def initialize(self):
        """Initialize all brain components"""
        try:
            self.logger.info("Initializing Cherry Brain components...")
            
            # Initialize memory manager
            self.memory_manager = MemoryManager(self.config)
            await self.memory_manager.initialize()
            
            # Initialize voice processor
            self.voice_processor = VoiceProcessor(self.config)
            await self.voice_processor.initialize()
            
            # Initialize vision system
            self.vision_system = VisionSystem(self.config)
            
            # Initialize desktop controller
            self.desktop_controller = DesktopController(self.config)
            
            # Initialize file handler
            self.file_handler = FileHandler(self.config)
            
            # Initialize web scraper
            self.web_scraper = WebScraper(self.config)
            
            self.logger.info("Cherry Brain initialized successfully!")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Cherry Brain: {e}")
            raise
    
    def _build_system_prompt(self) -> str:
        """Build the system prompt for Cherry"""
        return f"""You are Cherry, an intelligent AI desktop assistant with comprehensive capabilities.

PERSONALITY:
- Friendly, helpful, and proactive
- Speak naturally and conversationally
- Be concise but thorough when needed
- Show enthusiasm for helping users
- Remember context from previous conversations

CAPABILITIES:
You can perform these actions:
1. **Desktop Control**: Control mouse, keyboard, take screenshots, analyze screen content
2. **File Operations**: Create, read, edit, and organize files and documents
3. **Web Research**: Search for information, browse websites, extract content
4. **System Management**: Monitor system status, manage applications, automate tasks
5. **Memory**: Remember user preferences, past conversations, and context
6. **Vision**: Analyze screenshots, images, and visual content on screen
7. **Voice**: Listen to voice commands and respond with speech

AVAILABLE FUNCTIONS:
- take_screenshot() - Capture and analyze current screen
- control_mouse(action, x, y) - Move, click, drag mouse
- control_keyboard(action, text) - Type text, press keys, shortcuts
- search_web(query) - Search for information online
- create_file(filename, content, type) - Create documents, code files
- read_file(filename) - Read file contents
- analyze_screen() - Understand what's currently on screen
- remember(key, value) - Store information for later use
- recall(key) - Retrieve stored information
- execute_command(command) - Run system commands safely

RESPONSE FORMAT:
- Always provide a brief acknowledgment
- If you need to perform actions, explain what you're doing
- Provide results or status updates
- Ask clarifying questions if needed

Current date and time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
User's name: {self.config.get('USER_NAME', 'User')}
Wake word: "{self.config['WAKE_WORD']}"

Remember: You are running with free Gemini API, so be efficient with token usage while maintaining helpfulness.
"""

    async def process_input(self, user_input: str, context: Optional[Dict] = None) -> str:
        """Process user input and generate response"""
        try:
            self.logger.info(f"Processing user input: {user_input[:100]}...")
            
            # Add to conversation history
            self.conversation_history.append({
                'timestamp': datetime.now().isoformat(),
                'user': user_input,
                'context': context or {}
            })
            
            # Get relevant memories
            relevant_memories = await self.memory_manager.search_memories(user_input)
            
            # Build enhanced prompt
            enhanced_prompt = await self._build_enhanced_prompt(user_input, context, relevant_memories)
            
            # Generate response using Gemini
            response = await self._generate_response(enhanced_prompt)
            
            # Process any required actions
            action_results = await self._execute_actions(response)
            
            # Update response with action results
            if action_results:
                response = await self._integrate_action_results(response, action_results)
            
            # Store interaction in memory
            await self.memory_manager.store_interaction(user_input, response, context)
            
            # Add to conversation history
            self.conversation_history[-1]['cherry'] = response
            
            self.logger.info("Input processed successfully")
            return response
            
        except Exception as e:
            self.logger.error(f"Error processing input: {e}")
            return f"I encountered an error while processing your request: {str(e)}"
    
    async def _build_enhanced_prompt(self, user_input: str, context: Optional[Dict], relevant_memories: List[str]) -> str:
        """Build enhanced prompt with context and memories"""
        
        prompt_parts = [self.system_prompt]
        
        # Add relevant memories
        if relevant_memories:
            prompt_parts.append("\\nRELEVANT MEMORIES:")
            for memory in relevant_memories[:5]:  # Limit to 5 most relevant
                prompt_parts.append(f"- {memory}")
        
        # Add recent conversation context
        if self.conversation_history:
            prompt_parts.append("\\nRECENT CONVERSATION:")
            for interaction in self.conversation_history[-3:]:  # Last 3 interactions
                if 'user' in interaction:
                    prompt_parts.append(f"User: {interaction['user']}")
                if 'cherry' in interaction:
                    prompt_parts.append(f"Cherry: {interaction['cherry']}")
        
        # Add current context
        if context:
            prompt_parts.append(f"\\nCURRENT CONTEXT: {json.dumps(context, indent=2)}")
        
        # Add current screen context if available
        if self.config['ENABLE_SCREEN_ANALYSIS']:
            try:
                screen_context = await self.vision_system.get_screen_context()
                if screen_context:
                    prompt_parts.append(f"\\nCURRENT SCREEN: {screen_context}")
            except Exception as e:
                self.logger.warning(f"Could not get screen context: {e}")
        
        # Add user input
        prompt_parts.append(f"\\nUSER INPUT: {user_input}")
        prompt_parts.append("\\nCHERRY RESPONSE:")
        
        return "\\n".join(prompt_parts)
    
    async def _generate_response(self, prompt: str) -> str:
        """Generate response using Gemini API"""
        try:
            response = await self.model.generate_content_async(
                prompt,
                generation_config={
                    'temperature': self.config['GEMINI_TEMPERATURE'],
                    'max_output_tokens': self.config['GEMINI_MAX_TOKENS'],
                }
            )
            return response.text
        except Exception as e:
            self.logger.error(f"Error generating response: {e}")
            return "I'm having trouble connecting to my AI brain right now. Please try again."
    
    async def _execute_actions(self, response: str) -> Dict[str, Any]:
        """Execute any actions mentioned in the response"""
        action_results = {}
        
        # Parse response for action patterns
        actions = self._parse_actions_from_response(response)
        
        for action in actions:
            try:
                result = await self._execute_single_action(action)
                action_results[action['type']] = result
            except Exception as e:
                self.logger.error(f"Error executing action {action['type']}: {e}")
                action_results[action['type']] = {'error': str(e)}
        
        return action_results
    
    def _parse_actions_from_response(self, response: str) -> List[Dict]:
        """Parse actions from AI response using pattern matching"""
        actions = []
        
        # Common action patterns
        patterns = {
            'screenshot': ['take screenshot', 'capture screen', 'take a screenshot'],
            'web_search': ['search for', 'look up', 'find information about'],
            'mouse_click': ['click on', 'click at', 'mouse click'],
            'keyboard_type': ['type', 'enter text', 'input'],
            'create_file': ['create file', 'make document', 'save file'],
        }
        
        response_lower = response.lower()
        
        for action_type, keywords in patterns.items():
            for keyword in keywords:
                if keyword in response_lower:
                    # Extract parameters based on action type
                    action = {'type': action_type}
                    
                    if action_type == 'web_search':
                        # Extract search query
                        query_start = response_lower.find(keyword) + len(keyword)
                        query_end = response_lower.find('.', query_start)
                        if query_end == -1:
                            query_end = len(response_lower)
                        action['query'] = response[query_start:query_end].strip()
                    
                    actions.append(action)
                    break
        
        return actions
    
    async def _execute_single_action(self, action: Dict) -> Any:
        """Execute a single action"""
        action_type = action['type']
        
        if action_type == 'screenshot':
            return await self.vision_system.take_screenshot()
        
        elif action_type == 'web_search' and 'query' in action:
            return await self.web_scraper.search(action['query'])
        
        elif action_type == 'mouse_click':
            # For now, just log - would need coordinates
            self.logger.info("Mouse click action requested")
            return {'status': 'acknowledged'}
        
        elif action_type == 'keyboard_type' and 'text' in action:
            return await self.desktop_controller.type_text(action['text'])
        
        elif action_type == 'create_file':
            # Would need filename and content from action
            self.logger.info("File creation action requested")
            return {'status': 'acknowledged'}
        
        else:
            return {'status': 'unknown_action', 'action': action}
    
    async def _integrate_action_results(self, response: str, action_results: Dict) -> str:
        """Integrate action results into the response"""
        
        if not action_results:
            return response
        
        # Add action results to response
        result_parts = [response, "\\nAction Results:"]
        
        for action_type, result in action_results.items():
            if isinstance(result, dict) and 'error' in result:
                result_parts.append(f"- {action_type}: Error - {result['error']}")
            else:
                result_parts.append(f"- {action_type}: Completed successfully")
        
        return "\\n".join(result_parts)
    
    async def start_listening(self):
        """Start continuous voice listening"""
        self.is_listening = True
        if self.voice_processor:
            await self.voice_processor.start_listening(self._handle_voice_input)
    
    async def stop_listening(self):
        """Stop voice listening"""
        self.is_listening = False
        if self.voice_processor:
            await self.voice_processor.stop_listening()
    
    async def _handle_voice_input(self, voice_text: str):
        """Handle voice input from voice processor"""
        if voice_text and self.is_listening:
            response = await self.process_input(voice_text, {'input_type': 'voice'})
            
            # Speak the response
            if self.voice_processor:
                await self.voice_processor.speak(response)
    
    async def speak(self, text: str):
        """Make Cherry speak the given text"""
        if self.voice_processor:
            await self.voice_processor.speak(text)
    
    async def cleanup(self):
        """Cleanup resources"""
        self.logger.info("Cleaning up Cherry Brain...")
        
        await self.stop_listening()
        
        if self.memory_manager:
            await self.memory_manager.cleanup()
        
        if self.voice_processor:
            await self.voice_processor.cleanup()
        
        self.logger.info("Cherry Brain cleanup completed")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status of Cherry Brain"""
        return {
            'is_listening': self.is_listening,
            'conversation_history_length': len(self.conversation_history),
            'current_task': self.current_task,
            'memory_status': self.memory_manager.get_status() if self.memory_manager else {},
            'voice_status': self.voice_processor.get_status() if self.voice_processor else {},
        }
'''

print("Created cherry_brain.py - Core AI brain module")

# Create the memory manager module
memory_manager_content = '''"""
Memory Manager for Cherry AI Assistant
Handles RAG, context management, and conversation memory using vector embeddings
"""

import asyncio
import logging
import json
import pickle
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path

try:
    import chromadb
    from chromadb.config import Settings
    from sentence_transformers import SentenceTransformer
except ImportError:
    print("Memory dependencies not installed. Install with:")
    print("pip install chromadb sentence-transformers")
    import sys
    sys.exit(1)

class MemoryManager:
    """Manages long-term and short-term memory for Cherry"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Memory storage
        self.db_path = config['MEMORY_DIR']
        self.client = None
        self.collection = None
        
        # Embedding model for semantic search
        self.embedding_model = None
        
        # Short-term memory (recent interactions)
        self.short_term_memory = []
        self.max_short_term = config['CONTEXT_WINDOW']
        
        # Long-term memory metadata
        self.memory_stats = {
            'total_interactions': 0,
            'total_memories': 0,
            'last_cleanup': None
        }
    
    async def initialize(self):
        """Initialize the memory system"""
        try:
            self.logger.info("Initializing memory manager...")
            
            # Initialize ChromaDB
            self.client = chromadb.PersistentClient(
                path=str(self.db_path),
                settings=Settings(anonymized_telemetry=False)
            )
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name="cherry_memories",
                metadata={"description": "Cherry AI Assistant memory storage"}
            )
            
            # Initialize embedding model
            self.logger.info("Loading embedding model...")
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Load memory stats
            await self._load_memory_stats()
            
            self.logger.info(f"Memory manager initialized with {self.memory_stats['total_memories']} stored memories")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize memory manager: {e}")
            raise
    
    async def store_interaction(self, user_input: str, cherry_response: str, context: Optional[Dict] = None):
        """Store a user interaction in both short-term and long-term memory"""
        try:
            timestamp = datetime.now().isoformat()
            
            # Create interaction record
            interaction = {
                'timestamp': timestamp,
                'user_input': user_input,
                'cherry_response': cherry_response,
                'context': context or {}
            }
            
            # Add to short-term memory
            self.short_term_memory.append(interaction)
            
            # Maintain short-term memory size
            if len(self.short_term_memory) > self.max_short_term:
                self.short_term_memory.pop(0)
            
            # Store in long-term memory (vector database)
            await self._store_in_long_term_memory(interaction)
            
            # Update stats
            self.memory_stats['total_interactions'] += 1
            
        except Exception as e:
            self.logger.error(f"Error storing interaction: {e}")
    
    async def _store_in_long_term_memory(self, interaction: Dict):
        """Store interaction in vector database for semantic retrieval"""
        try:
            # Combine user input and response for better context
            combined_text = f"User: {interaction['user_input']} Cherry: {interaction['cherry_response']}"
            
            # Generate unique ID
            interaction_id = f"interaction_{self.memory_stats['total_interactions']}"
            
            # Add to ChromaDB collection
            self.collection.add(
                documents=[combined_text],
                metadatas=[{
                    'timestamp': interaction['timestamp'],
                    'user_input': interaction['user_input'],
                    'cherry_response': interaction['cherry_response'],
                    'context': json.dumps(interaction['context'])
                }],
                ids=[interaction_id]
            )
            
            self.memory_stats['total_memories'] += 1
            
        except Exception as e:
            self.logger.error(f"Error storing in long-term memory: {e}")
    
    async def search_memories(self, query: str, limit: int = 5) -> List[str]:
        """Search for relevant memories using semantic similarity"""
        try:
            if not self.collection or self.memory_stats['total_memories'] == 0:
                return []
            
            # Search in vector database
            results = self.collection.query(
                query_texts=[query],
                n_results=min(limit, self.memory_stats['total_memories'])
            )
            
            # Extract relevant memories
            relevant_memories = []
            
            if results['documents'] and results['documents'][0]:
                for doc, metadata in zip(results['documents'][0], results['metadatas'][0]):
                    # Format memory for context
                    memory_text = f"Previous interaction: {metadata['user_input']} -> {metadata['cherry_response']}"
                    relevant_memories.append(memory_text)
            
            return relevant_memories
            
        except Exception as e:
            self.logger.error(f"Error searching memories: {e}")
            return []
    
    def get_short_term_context(self) -> List[Dict]:
        """Get recent conversation context"""
        return self.short_term_memory.copy()
    
    async def store_fact(self, key: str, value: Any, category: str = "general"):
        """Store a specific fact or preference"""
        try:
            fact_text = f"Fact - {key}: {value}"
            fact_id = f"fact_{key}_{datetime.now().timestamp()}"
            
            self.collection.add(
                documents=[fact_text],
                metadatas=[{
                    'type': 'fact',
                    'key': key,
                    'value': str(value),
                    'category': category,
                    'timestamp': datetime.now().isoformat()
                }],
                ids=[fact_id]
            )
            
            self.memory_stats['total_memories'] += 1
            
        except Exception as e:
            self.logger.error(f"Error storing fact: {e}")
    
    async def recall_fact(self, key: str) -> Optional[Any]:
        """Recall a specific fact"""
        try:
            results = self.collection.query(
                query_texts=[f"Fact - {key}"],
                n_results=1,
                where={"type": "fact", "key": key}
            )
            
            if results['metadatas'] and results['metadatas'][0]:
                return results['metadatas'][0][0]['value']
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error recalling fact: {e}")
            return None
    
    async def cleanup_old_memories(self, days_to_keep: int = 30):
        """Clean up old memories to free space"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            cutoff_iso = cutoff_date.isoformat()
            
            # This would require custom implementation with ChromaDB
            # For now, just log the intent
            self.logger.info(f"Memory cleanup requested for memories older than {cutoff_date}")
            
            self.memory_stats['last_cleanup'] = datetime.now().isoformat()
            
        except Exception as e:
            self.logger.error(f"Error during memory cleanup: {e}")
    
    async def _load_memory_stats(self):
        """Load memory statistics"""
        try:
            stats_file = self.config['MEMORY_DIR'] / 'memory_stats.json'
            
            if stats_file.exists():
                with open(stats_file, 'r') as f:
                    self.memory_stats.update(json.load(f))
            else:
                # Initialize with collection count
                if self.collection:
                    count = self.collection.count()
                    self.memory_stats['total_memories'] = count
                    
        except Exception as e:
            self.logger.warning(f"Could not load memory stats: {e}")
    
    async def _save_memory_stats(self):
        """Save memory statistics"""
        try:
            stats_file = self.config['MEMORY_DIR'] / 'memory_stats.json'
            
            with open(stats_file, 'w') as f:
                json.dump(self.memory_stats, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Error saving memory stats: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get memory manager status"""
        return {
            'short_term_memory_count': len(self.short_term_memory),
            'total_memories': self.memory_stats['total_memories'],
            'total_interactions': self.memory_stats['total_interactions'],
            'last_cleanup': self.memory_stats['last_cleanup'],
            'memory_dir': str(self.config['MEMORY_DIR']),
        }
    
    async def cleanup(self):
        """Cleanup memory manager resources"""
        try:
            await self._save_memory_stats()
            
            if self.client:
                # ChromaDB doesn't need explicit cleanup
                pass
                
            self.logger.info("Memory manager cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during memory manager cleanup: {e}")
'''

print("Created memory_manager.py - Memory and context management")

with open('cherry_brain.py', 'w') as f:
    f.write(cherry_brain_content)

with open('memory_manager.py', 'w') as f:
    f.write(memory_manager_content)

print("\nCompleted core modules:")
print("✓ cherry_brain.py - Main AI processing engine")
print("✓ memory_manager.py - RAG and memory management")