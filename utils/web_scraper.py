"""
Web Scraper for Cherry AI Assistant
Handles web searches and information retrieval
"""

import asyncio
import logging
import aiohttp
from typing import Dict, Any, List, Optional
from urllib.parse import quote_plus
import json

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("Web scraping dependencies not installed. Install with:")
    print("pip install beautifulsoup4 aiohttp")

class WebScraper:
    """Handles web searches and content extraction for Cherry"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Session for HTTP requests
        self.session = None

        # Search engines
        self.search_engines = {
            'duckduckgo': 'https://duckduckgo.com/html/?q={}',
            'bing': 'https://www.bing.com/search?q={}',
        }

        # Request headers
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }

    async def initialize(self):
        """Initialize the web scraper"""
        try:
            self.session = aiohttp.ClientSession(
                headers=self.headers,
                timeout=aiohttp.ClientTimeout(total=30)
            )
            self.logger.info("Web scraper initialized")
        except Exception as e:
            self.logger.error(f"Error initializing web scraper: {e}")

    async def search(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        """Search for information on the web"""
        try:
            if not self.session:
                await self.initialize()

            self.logger.info(f"Searching web for: {query}")

            # Use DuckDuckGo for privacy-friendly search
            search_url = self.search_engines['duckduckgo'].format(quote_plus(query))

            async with self.session.get(search_url) as response:
                if response.status == 200:
                    html = await response.text()
                    results = await self._parse_duckduckgo_results(html, max_results)

                    return {
                        'query': query,
                        'results': results,
                        'total_results': len(results)
                    }
                else:
                    self.logger.error(f"Search request failed: {response.status}")
                    return {'query': query, 'results': [], 'error': f'HTTP {response.status}'}

        except Exception as e:
            self.logger.error(f"Error searching web: {e}")
            return {'query': query, 'results': [], 'error': str(e)}

    async def _parse_duckduckgo_results(self, html: str, max_results: int) -> List[Dict[str, str]]:
        """Parse DuckDuckGo search results"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            results = []

            # Find result containers
            result_containers = soup.find_all('div', class_='result')

            for container in result_containers[:max_results]:
                try:
                    # Extract title
                    title_elem = container.find('a', class_='result__a')
                    title = title_elem.get_text().strip() if title_elem else "No title"

                    # Extract URL
                    url = title_elem.get('href') if title_elem else ""

                    # Extract snippet
                    snippet_elem = container.find('a', class_='result__snippet')
                    snippet = snippet_elem.get_text().strip() if snippet_elem else ""

                    if title and url:
                        results.append({
                            'title': title,
                            'url': url,
                            'snippet': snippet
                        })

                except Exception as e:
                    self.logger.warning(f"Error parsing result container: {e}")
                    continue

            return results

        except Exception as e:
            self.logger.error(f"Error parsing search results: {e}")
            return []

    async def get_page_content(self, url: str) -> Dict[str, Any]:
        """Get content from a web page"""
        try:
            if not self.session:
                await self.initialize()

            async with self.session.get(url) as response:
                if response.status == 200:
                    html = await response.text()
                    content = await self._extract_page_content(html)

                    return {
                        'url': url,
                        'title': content.get('title', ''),
                        'text': content.get('text', ''),
                        'success': True
                    }
                else:
                    return {
                        'url': url,
                        'success': False,
                        'error': f'HTTP {response.status}'
                    }

        except Exception as e:
            self.logger.error(f"Error getting page content: {e}")
            return {
                'url': url,
                'success': False,
                'error': str(e)
            }

    async def _extract_page_content(self, html: str) -> Dict[str, str]:
        """Extract text content from HTML"""
        try:
            soup = BeautifulSoup(html, 'html.parser')

            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()

            # Extract title
            title = ""
            title_tag = soup.find('title')
            if title_tag:
                title = title_tag.get_text().strip()

            # Extract main content
            # Try to find main content areas first
            main_content = soup.find('main') or soup.find('article') or soup.find('div', class_='content')

            if main_content:
                text = main_content.get_text()
            else:
                text = soup.get_text()

            # Clean up text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)

            # Limit text length
            if len(text) > 5000:
                text = text[:5000] + "..."

            return {
                'title': title,
                'text': text
            }

        except Exception as e:
            self.logger.error(f"Error extracting page content: {e}")
            return {'title': '', 'text': ''}

    async def quick_search_summary(self, query: str) -> str:
        """Get a quick summary from web search"""
        try:
            search_results = await self.search(query, max_results=3)

            if search_results['results']:
                summary_parts = [f"Search results for '{query}':"]

                for i, result in enumerate(search_results['results'], 1):
                    summary_parts.append(f"{i}. {result['title']}")
                    if result['snippet']:
                        summary_parts.append(f"   {result['snippet']}")

                return '\n'.join(summary_parts)
            else:
                return f"No search results found for '{query}'"

        except Exception as e:
            self.logger.error(f"Error getting search summary: {e}")
            return f"Error searching for '{query}': {str(e)}"

    async def cleanup(self):
        """Cleanup web scraper resources"""
        try:
            if self.session:
                await self.session.close()
            self.logger.info("Web scraper cleanup completed")
        except Exception as e:
            self.logger.error(f"Error during web scraper cleanup: {e}")
