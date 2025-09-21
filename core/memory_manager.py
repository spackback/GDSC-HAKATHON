"""
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
