"""
Configuration file for the fact vs opinion scraper
"""

# News sources to scrape
NEWS_SOURCES = {
    'bbc': {
        'url': 'https://www.bbc.com/news',
        'article_selector': 'h3 a',
        'content_selector': 'div[data-component="text-block"] p'
    },
    'reuters': {
        'url': 'https://www.reuters.com/world/',
        'article_selector': 'a[data-testid="Heading"]',
        'content_selector': 'div[data-testid="paragraph"] p'
    },
    'cnn': {
        'url': 'https://edition.cnn.com/',
        'article_selector': 'h3 a',
        'content_selector': 'div.zn-body__paragraph p'
    }
}

# Keywords that often indicate opinions
OPINION_KEYWORDS = [
    'believe', 'think', 'feel', 'opinion', 'should', 'must', 'ought',
    'probably', 'likely', 'seems', 'appears', 'suggest', 'recommend',
    'prefer', 'better', 'worse', 'best', 'worst', 'amazing', 'terrible',
    'wonderful', 'awful', 'beautiful', 'ugly', 'love', 'hate'
]

# Keywords that often indicate facts
FACT_KEYWORDS = [
    'according to', 'data shows', 'research indicates', 'study found',
    'statistics show', 'reported', 'confirmed', 'announced', 'stated',
    'published', 'documented', 'recorded', 'measured', 'observed'
]

# Headers for web requests
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Output settings
OUTPUT_FILE = 'fact_opinion_results.json'
MAX_ARTICLES_PER_SOURCE = 5