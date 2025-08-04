# Fact vs Opinion Analysis System

An agentic approach to differentiate facts from opinions by scraping content from multiple news sources and analyzing it through the perspectives of four different expert roles powered by **Gemini AI**.

## Overview

This project implements a multi-agent system that analyzes scraped news content to classify statements as facts or opinions. The system uses four distinct **Gemini AI-powered agents**, each with specialized expertise:

1. **Journalist Agent** - Focuses on source attribution, quotes, and journalistic standards
2. **Media Professor Agent** - Applies media literacy principles and academic rigor
3. **Linguist Agent** - Analyzes language patterns, modal verbs, and linguistic markers
4. **Social Media Veteran Agent** - Identifies viral patterns, emotional language, and social media indicators

## Key Features

- **Multi-source web scraping** using Beautiful Soup
- **Gemini AI-powered agentic analysis** with four specialized perspectives
- **Consensus-based classification** combining all agent opinions
- **Detailed reporting** with confidence scores and reasoning
- **Configurable news sources** and analysis parameters
- **Comprehensive logging** and error handling
- **Real AI analysis** using Google's Gemini 2.5 Flash model

## Project Structure

```
├── main.py              # Main orchestrator and entry point
├── scraper.py           # Web scraping functionality
├── gemini_agents.py     # Gemini AI-powered four-agent analysis system
├── agents.py            # Original rule-based agents (legacy)
├── config.py            # Configuration settings
├── gemini_demo.py       # Demo script for Gemini agents
├── demo.py              # Demo script for rule-based agents
├── .env.example         # Environment variables template
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Installation

1. Clone or download the project files
2. Install required dependencies:
```bash
pip install -r requirements.txt
```
3. Set up your Gemini API key:
   - Copy `.env.example` to `.env`
   - Add your Gemini API key: `GEMINI_API_KEY=your_api_key_here`
   - Get your API key from: https://makersuite.google.com/app/apikey

## Usage

### Gemini AI-Powered Analysis (Recommended)

Test with sample content (working demo):
```bash
python simple_demo.py
```

Run the complete analysis pipeline:
```bash
python main.py
```

Advanced demo (may hit token limits):
```bash
python gemini_demo.py
```

This will:
1. Scrape articles from configured news sources
2. Analyze each article using all four Gemini AI agents
3. Generate consensus classifications with detailed AI reasoning
4. Save detailed results to `fact_opinion_results.json`
5. Display a summary report

### Legacy Rule-Based Analysis

For comparison, you can also run the original rule-based system:
```bash
python demo.py  # Test with samples
```

### Configuration

Edit [`config.py`](config.py) to customize:

- **News sources**: Add/modify URLs and CSS selectors
- **Analysis parameters**: Adjust keyword lists and scoring weights
- **Output settings**: Change file names and limits

Example configuration:
```python
NEWS_SOURCES = {
    'bbc': {
        'url': 'https://www.bbc.com/news',
        'article_selector': 'h3 a',
        'content_selector': 'div[data-component="text-block"] p'
    }
}
```

## Gemini AI Agent System Details

Each agent uses sophisticated AI prompting to analyze content from their specialized perspective:

### 1. Gemini Journalist Agent
- **Expertise**: 20+ years investigative journalism experience
- **Focus**: Source verification, fact-checking, journalistic standards
- **Analysis**:
  - Verifies source attribution and credibility
  - Identifies proper journalistic language vs editorial content
  - Recognizes official statements and documented evidence
- **Prompting**: Uses journalistic ethics and verification standards

### 2. Gemini Media Professor Agent
- **Expertise**: Distinguished Media Studies professor with academic research focus
- **Focus**: Media literacy, critical analysis, academic rigor
- **Analysis**:
  - Applies academic research standards and peer review criteria
  - Detects bias and evaluates methodological soundness
  - Distinguishes scholarly vs non-academic sources
- **Prompting**: Uses academic critical thinking and research methodology

### 3. Gemini Linguist Agent
- **Expertise**: Computational linguist specializing in discourse analysis
- **Focus**: Language structure, modal verbs, semantic analysis
- **Analysis**:
  - Examines modal verbs and epistemic modality
  - Identifies evidential markers and subjective language structures
  - Analyzes pragmatic implications of statements
- **Prompting**: Uses linguistic theory and semantic analysis frameworks

### 4. Gemini Social Media Veteran Agent
- **Expertise**: 15+ years analyzing digital communication and viral content
- **Focus**: Online discourse patterns, viral content, digital fact-checking
- **Analysis**:
  - Recognizes viral opinion language vs factual reporting
  - Identifies emotional engagement tactics and social proof
  - Detects verification markers in digital contexts
- **Prompting**: Uses digital communication expertise and online verification methods
## API Integration

The system uses Google's Gemini 2.0 Flash model via REST API calls:

```bash
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent" \
  -H 'Content-Type: application/json' \
  -H 'X-goog-api-key: YOUR_API_KEY' \
  -X POST \
  -d '{
    "contents": [
      {
        "parts": [
          {
            "text": "Your analysis prompt here"
          }
        ]
      }
    ]
  }'
```

Each agent sends specialized prompts to Gemini AI and parses structured JSON responses for consistent analysis.


## Output Format

The system generates detailed JSON output with:

```json
{
  "analysis_metadata": {
    "timestamp": "2025-01-06T18:35:00",
    "total_articles_analyzed": 15,
    "agent_roles": ["Journalist", "Media Professor", "Linguist", "Social Media Veteran"]
  },
  "summary": {
    "overall_statistics": {
      "classification_distribution": {
        "mostly_factual": 8,
        "mostly_opinion": 4,
        "mixed_content": 3
      }
    },
    "key_insights": [
      "Content is predominantly factual (53.3% of articles)",
      "High confidence in classifications (average: 0.72)"
    ]
  },
  "detailed_analyses": [...]
}
```

## Classification Logic

### Individual Agent Analysis
Each agent analyzes content using:
- **Pattern matching** for role-specific indicators
- **Confidence scoring** based on evidence strength
- **Detailed reasoning** explaining the classification

### Consensus Building
- **Majority voting** among the four agents
- **Confidence averaging** across all agents
- **Evidence aggregation** from all perspectives

### Final Classification
- **mostly_factual**: >60% of sentences classified as facts
- **mostly_opinion**: >60% of sentences classified as opinions  
- **mixed_content**: Balanced mix of facts and opinions

## Example Analysis

For the statement: *"According to the latest research, climate change will probably affect global temperatures."*

- **Journalist**: FACT (0.8) - "according to" indicates source attribution
- **Media Professor**: FACT (0.7) - "research" suggests academic backing
- **Linguist**: MIXED (0.6) - "probably" indicates epistemic uncertainty
- **Social Media Veteran**: FACT (0.6) - Formal language structure

**Consensus**: FACT with 75% confidence

## Limitations

- **Web scraping dependencies**: Site structure changes may break scrapers
- **Language-specific**: Currently optimized for English content
- **Pattern-based analysis**: May miss nuanced contextual meanings
- **Source limitations**: Analysis quality depends on scraped content quality

## Future Enhancements

- **Machine learning integration** for improved pattern recognition
- **Multi-language support** for international sources
- **Real-time analysis** with streaming data
- **Interactive web interface** for manual review
- **Custom agent training** for domain-specific analysis

## Dependencies

- [`beautifulsoup4`](https://pypi.org/project/beautifulsoup4/) - Web scraping
- [`requests`](https://pypi.org/project/requests/) - HTTP requests
- [`lxml`](https://pypi.org/project/lxml/) - XML/HTML parsing
- [`nltk`](https://pypi.org/project/nltk/) - Natural language processing
- [`textblob`](https://pypi.org/project/textblob/) - Text analysis
- [`pandas`](https://pypi.org/project/pandas/) - Data manipulation
- [`numpy`](https://pypi.org/project/numpy/) - Numerical computing
- [`scikit-learn`](https://pypi.org/project/scikit-learn/) - Machine learning utilities

## License

This project is provided as-is for educational and research purposes.

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve the system.