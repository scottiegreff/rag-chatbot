import requests
import json
import re
from typing import List, Dict, Optional
from urllib.parse import quote_plus
import time
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

class SearchService:
    """
    Service for performing internet searches and retrieving web content.
    Supports multiple search engines and content extraction.
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.search_engines = {
            'duckduckgo': self._search_duckduckgo,
            'google': self._search_google,
            'bing': self._search_bing
        }
    
    def search(self, query: str, num_results: int = 5, engine: str = 'duckduckgo') -> List[Dict]:
        """
        Perform an internet search and return results.
        
        Args:
            query: Search query string
            num_results: Number of results to return
            engine: Search engine to use ('duckduckgo', 'google', 'bing')
            
        Returns:
            List of search results with title, url, and snippet
        """
        try:
            if engine not in self.search_engines:
                logger.warning(f"Unknown search engine: {engine}, using duckduckgo")
                engine = 'duckduckgo'
            
            logger.info(f"Searching for: {query} using {engine}")
            results = self.search_engines[engine](query, num_results)
            
            # Add content extraction for top results
            for result in results[:3]:  # Extract content for top 3 results
                try:
                    content = self._extract_content(result['url'])
                    if content:
                        result['content'] = content[:1000]  # Limit content length
                except Exception as e:
                    logger.warning(f"Failed to extract content from {result['url']}: {e}")
                    result['content'] = ""
            
            return results
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    def _search_duckduckgo(self, query: str, num_results: int) -> List[Dict]:
        """Search using DuckDuckGo Instant Answer API."""
        try:
            # DuckDuckGo Instant Answer API
            url = "https://api.duckduckgo.com/"
            params = {
                'q': query,
                'format': 'json',
                'no_html': '1',
                'skip_disambig': '1'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            results = []
            
            # Add instant answer if available
            if data.get('Abstract'):
                results.append({
                    'title': data.get('Heading', 'Instant Answer'),
                    'url': data.get('AbstractURL', ''),
                    'snippet': data.get('Abstract', ''),
                    'source': 'duckduckgo_instant'
                })
            
            # Add related topics
            for topic in data.get('RelatedTopics', [])[:num_results-1]:
                if isinstance(topic, dict) and topic.get('Text'):
                    results.append({
                        'title': topic.get('FirstURL', '').split('/')[-1].replace('_', ' '),
                        'url': topic.get('FirstURL', ''),
                        'snippet': topic.get('Text', ''),
                        'source': 'duckduckgo_related'
                    })
            
            # If no results from DuckDuckGo, try fallback to Google
            if not results:
                logger.info(f"No DuckDuckGo results for '{query}', trying Google fallback...")
                return self._search_google(query, num_results)
            
            return results[:num_results]
            
        except Exception as e:
            logger.error(f"DuckDuckGo search failed: {e}")
            # Try Google as fallback
            logger.info(f"Trying Google fallback for query: {query}")
            return self._search_google(query, num_results)
    
    def _search_google(self, query: str, num_results: int) -> List[Dict]:
        """Search using Google (simplified approach)."""
        try:
            # Note: This is a simplified approach. For production, consider using official APIs
            search_url = f"https://www.google.com/search?q={quote_plus(query)}&num={num_results}"
            
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            results = []
            
            # Try multiple selectors for Google search results
            selectors = [
                'div.g',  # Standard Google results
                'div[data-hveid]',  # Alternative selector
                'div.rc',  # Another common selector
                'div.yuRUbf'  # Yet another selector
            ]
            
            for selector in selectors:
                result_elements = soup.select(selector)
                if result_elements:
                    logger.info(f"Found {len(result_elements)} results using selector: {selector}")
                    break
            
            if not result_elements:
                # Fallback: look for any div with links
                result_elements = soup.find_all('div')
                logger.info(f"Using fallback selector, found {len(result_elements)} divs")
            
            for result in result_elements[:num_results]:
                # Try to find title and link
                title_elem = result.find('h3') or result.find('h2') or result.find('h1')
                link_elem = result.find('a')
                snippet_elem = result.find('span', class_='st') or result.find('div', class_='s') or result.find('p')
                
                if title_elem and link_elem:
                    url = link_elem.get('href', '')
                    # Filter out non-search result URLs
                    if url.startswith('/url?') or url.startswith('http'):
                        # Clean up Google redirect URLs
                        if url.startswith('/url?'):
                            from urllib.parse import parse_qs, urlparse
                            parsed = urlparse(url)
                            params = parse_qs(parsed.query)
                            url = params.get('q', [url])[0]
                        
                        results.append({
                            'title': title_elem.get_text().strip(),
                            'url': url,
                            'snippet': snippet_elem.get_text().strip() if snippet_elem else '',
                            'source': 'google'
                        })
            
            # If still no results, try a different approach
            if not results:
                logger.info("No results found with standard selectors, trying alternative approach...")
                # Look for any links that might be search results
                links = soup.find_all('a', href=True)
                for link in links[:num_results]:
                    url = link.get('href', '')
                    if url.startswith('http') and 'google.com' not in url:
                        title = link.get_text().strip()
                        if title and len(title) > 10:  # Filter out short/navigation links
                            results.append({
                                'title': title,
                                'url': url,
                                'snippet': f"Found via Google search for: {query}",
                                'source': 'google_fallback'
                            })
            
            return results
            
        except Exception as e:
            logger.error(f"Google search failed: {e}")
            return []
    
    def _search_bing(self, query: str, num_results: int) -> List[Dict]:
        """Search using Bing (simplified approach)."""
        try:
            search_url = f"https://www.bing.com/search?q={quote_plus(query)}&count={num_results}"
            
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            results = []
            
            # Extract search results
            for result in soup.find_all('li', class_='b_algo')[:num_results]:
                title_elem = result.find('h2')
                link_elem = result.find('a')
                snippet_elem = result.find('p')
                
                if title_elem and link_elem:
                    results.append({
                        'title': title_elem.get_text(),
                        'url': link_elem.get('href', ''),
                        'snippet': snippet_elem.get_text() if snippet_elem else '',
                        'source': 'bing'
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"Bing search failed: {e}")
            return []
    
    def _extract_content(self, url: str) -> Optional[str]:
        """Extract main content from a webpage."""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Try to find main content areas
            content_selectors = [
                'main',
                'article',
                '.content',
                '.post-content',
                '.entry-content',
                '#content',
                '.main-content'
            ]
            
            content = None
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    content = content_elem.get_text()
                    break
            
            # Fallback to body text
            if not content:
                content = soup.get_text()
            
            # Clean up the text
            if content:
                # Remove extra whitespace
                content = re.sub(r'\s+', ' ', content)
                # Remove special characters
                content = re.sub(r'[^\w\s\.\,\!\?\:\;\-\(\)]', '', content)
                return content.strip()
            
            return None
            
        except Exception as e:
            logger.warning(f"Content extraction failed for {url}: {e}")
            return None
    
    def get_search_summary(self, query: str, results: List[Dict]) -> str:
        """
        Create a summary of search results for the chatbot.
        
        Args:
            query: Original search query
            results: List of search results
            
        Returns:
            Formatted summary string
        """
        if not results:
            return f"I couldn't find any recent information about '{query}'."
        
        summary = f"Here's what I found about '{query}':\n\n"
        
        for i, result in enumerate(results[:3], 1):
            summary += f"{i}. **{result['title']}**\n"
            summary += f"   {result['snippet'][:200]}...\n"
            if result.get('content'):
                summary += f"   *Additional content: {result['content'][:150]}...*\n"
            summary += f"   Source: {result['url']}\n\n"
        
        summary += f"*Search performed using {results[0].get('source', 'web search')}*"
        
        return summary 