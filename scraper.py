"""
Web scraper module for collecting articles from news sources
"""

import requests
from bs4 import BeautifulSoup
import time
import logging
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin
from config import NEWS_SOURCES, HEADERS, MAX_ARTICLES_PER_SOURCE

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewsContentScraper:
    """Simple content scraper for individual URLs"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
    
    def scrape_url(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Scrape content from a single URL
        Returns dict with title, content, and metadata
        """
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract title
            title_element = soup.find('title')
            title = title_element.get_text(strip=True) if title_element else "No Title"
            
            # Extract main content - try common selectors
            content_selectors = [
                'article',
                '.article-content',
                '.content',
                '.post-content',
                'main',
                '.story-body',
                'p'
            ]
            
            content_text = ""
            for selector in content_selectors:
                elements = soup.select(selector)
                if elements:
                    content_parts = []
                    for element in elements:
                        text = element.get_text(strip=True)
                        if text and len(text) > 50:
                            content_parts.append(text)
                    
                    if content_parts:
                        content_text = ' '.join(content_parts)
                        break
            
            # Fallback to all paragraph text
            if not content_text:
                paragraphs = soup.find_all('p')
                content_parts = []
                for p in paragraphs:
                    text = p.get_text(strip=True)
                    if text and len(text) > 30:
                        content_parts.append(text)
                content_text = ' '.join(content_parts)
            
            return {
                'title': title,
                'content': content_text,
                'url': url,
                'timestamp': time.time()
            }
            
        except requests.RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error parsing content from {url}: {e}")
            return None

class NewsScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
    
    def get_page_content(self, url: str) -> Optional[str]:
        """
        Fetch the content of a web page
        """
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
            return None
    
    def extract_article_links(self, html_content: str, base_url: str, selector: str) -> List[str]:
        """
        Extract article links from the main page
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        links = []
        
        for element in soup.select(selector):
            href = element.get('href')
            if href and isinstance(href, str):
                full_url = urljoin(base_url, href)
                links.append(full_url)
        
        return links[:MAX_ARTICLES_PER_SOURCE]
    
    def extract_article_content(self, html_content: str, content_selector: str) -> str:
        """
        Extract the main content from an article page
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        content_elements = soup.select(content_selector)
        
        content = []
        for element in content_elements:
            text = element.get_text(strip=True)
            if text and len(text) > 50:  # Filter out very short paragraphs
                content.append(text)
        
        return ' '.join(content)
    
    def scrape_source(self, source_name: str, source_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Scrape articles from a single news source
        """
        logger.info(f"Scraping {source_name}...")
        
        # Get main page content
        main_page_content = self.get_page_content(source_config['url'])
        if not main_page_content:
            return []
        
        # Extract article links
        article_links = self.extract_article_links(
            main_page_content, 
            source_config['url'], 
            source_config['article_selector']
        )
        
        articles = []
        for i, link in enumerate(article_links):
            logger.info(f"Scraping article {i+1}/{len(article_links)} from {source_name}")
            
            # Get article content
            article_content = self.get_page_content(link)
            if article_content:
                content = self.extract_article_content(
                    article_content, 
                    source_config['content_selector']
                )
                
                if content:
                    articles.append({
                        'source': source_name,
                        'url': link,
                        'content': content,
                        'timestamp': time.time()
                    })
            
            # Be respectful to the server
            time.sleep(1)
        
        return articles
    
    def scrape_all_sources(self) -> List[Dict[str, Any]]:
        """
        Scrape articles from all configured news sources
        """
        all_articles = []
        
        for source_name, source_config in NEWS_SOURCES.items():
            try:
                articles = self.scrape_source(source_name, source_config)
                all_articles.extend(articles)
                logger.info(f"Scraped {len(articles)} articles from {source_name}")
            except Exception as e:
                logger.error(f"Error scraping {source_name}: {e}")
        
        logger.info(f"Total articles scraped: {len(all_articles)}")
        return all_articles