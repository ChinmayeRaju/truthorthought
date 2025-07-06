"""
Main orchestrator for the fact vs opinion analysis system
"""

import json
import time
from datetime import datetime
from scraper import NewsScraper
from gemini_agents import GeminiAgentOrchestrator
from config import OUTPUT_FILE
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('fact_opinion_analysis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class FactOpinionAnalyzer:
    def __init__(self):
        self.scraper = NewsScraper()
        self.orchestrator = GeminiAgentOrchestrator()
    
    def run_analysis(self):
        """
        Main method to run the complete fact vs opinion analysis
        """
        logger.info("Starting fact vs opinion analysis...")
        
        # Step 1: Scrape articles
        logger.info("Step 1: Scraping articles from news sources...")
        articles = self.scraper.scrape_all_sources()
        
        if not articles:
            logger.error("No articles were scraped. Exiting.")
            return
        
        # Step 2: Analyze each article with the agent system
        logger.info("Step 2: Analyzing articles with agent system...")
        analyzed_articles = []
        
        for i, article in enumerate(articles):
            logger.info(f"Analyzing article {i+1}/{len(articles)} from {article['source']}")
            
            try:
                analysis = self.orchestrator.analyze_content(article['content'])
                
                analyzed_article = {
                    'article_info': {
                        'source': article['source'],
                        'url': article['url'],
                        'timestamp': article['timestamp'],
                        'content_preview': analysis['content_preview']
                    },
                    'analysis': {
                        'sentence_analyses': analysis['sentence_analyses'],
                        'overall_consensus': analysis['overall_consensus']
                    },
                    'analysis_timestamp': time.time()
                }
                
                analyzed_articles.append(analyzed_article)
                
            except Exception as e:
                logger.error(f"Error analyzing article from {article['source']}: {e}")
                continue
        
        # Step 3: Generate summary report
        logger.info("Step 3: Generating summary report...")
        summary = self.generate_summary(analyzed_articles)
        
        # Step 4: Save results
        logger.info("Step 4: Saving results...")
        results = {
            'analysis_metadata': {
                'timestamp': datetime.now().isoformat(),
                'total_articles_scraped': len(articles),
                'total_articles_analyzed': len(analyzed_articles),
                'agent_roles': ['Journalist', 'Media Professor', 'Linguist', 'Social Media Veteran']
            },
            'summary': summary,
            'detailed_analyses': analyzed_articles
        }
        
        self.save_results(results)
        self.print_summary(summary)
        
        logger.info("Analysis complete!")
    
    def generate_summary(self, analyzed_articles):
        """
        Generate a summary of all analyses
        """
        if not analyzed_articles:
            return {}
        
        # Count overall classifications
        classification_counts = {
            'mostly_factual': 0,
            'mostly_opinion': 0,
            'mixed_content': 0
        }
        
        source_breakdown = {}
        total_confidence = 0
        
        for article in analyzed_articles:
            classification = article['analysis']['overall_consensus']['classification']
            classification_counts[classification] += 1
            
            confidence = article['analysis']['overall_consensus']['confidence']
            total_confidence += confidence
            
            source = article['article_info']['source']
            if source not in source_breakdown:
                source_breakdown[source] = {
                    'mostly_factual': 0,
                    'mostly_opinion': 0,
                    'mixed_content': 0,
                    'total': 0
                }
            source_breakdown[source][classification] += 1
            source_breakdown[source]['total'] += 1
        
        avg_confidence = total_confidence / len(analyzed_articles)
        
        # Find most factual and most opinion-based sources
        source_scores = {}
        for source, breakdown in source_breakdown.items():
            if breakdown['total'] > 0:
                fact_ratio = breakdown['mostly_factual'] / breakdown['total']
                opinion_ratio = breakdown['mostly_opinion'] / breakdown['total']
                source_scores[source] = {
                    'fact_ratio': fact_ratio,
                    'opinion_ratio': opinion_ratio,
                    'mixed_ratio': breakdown['mixed_content'] / breakdown['total']
                }
        
        return {
            'overall_statistics': {
                'total_articles': len(analyzed_articles),
                'average_confidence': round(avg_confidence, 3),
                'classification_distribution': classification_counts
            },
            'source_breakdown': source_breakdown,
            'source_analysis': source_scores,
            'key_insights': self.generate_insights(classification_counts, source_scores, avg_confidence)
        }
    
    def generate_insights(self, classification_counts, source_scores, avg_confidence):
        """
        Generate key insights from the analysis
        """
        insights = []
        
        total_articles = sum(classification_counts.values())
        
        if total_articles == 0:
            return ["No articles were successfully analyzed."]
        
        # Overall content type insight
        fact_percentage = classification_counts['mostly_factual'] / total_articles * 100
        opinion_percentage = classification_counts['mostly_opinion'] / total_articles * 100
        
        if fact_percentage > 60:
            insights.append(f"Content is predominantly factual ({fact_percentage:.1f}% of articles)")
        elif opinion_percentage > 60:
            insights.append(f"Content is predominantly opinion-based ({opinion_percentage:.1f}% of articles)")
        else:
            insights.append(f"Content is mixed: {fact_percentage:.1f}% factual, {opinion_percentage:.1f}% opinion-based")
        
        # Confidence insight
        if avg_confidence > 0.7:
            insights.append(f"High confidence in classifications (average: {avg_confidence:.2f})")
        elif avg_confidence < 0.5:
            insights.append(f"Low confidence in classifications (average: {avg_confidence:.2f}) - content may be ambiguous")
        
        # Source insights
        if source_scores:
            most_factual = max(source_scores.items(), key=lambda x: x[1]['fact_ratio'])
            most_opinion = max(source_scores.items(), key=lambda x: x[1]['opinion_ratio'])
            
            insights.append(f"Most factual source: {most_factual[0]} ({most_factual[1]['fact_ratio']:.1%} factual content)")
            insights.append(f"Most opinion-based source: {most_opinion[0]} ({most_opinion[1]['opinion_ratio']:.1%} opinion content)")
        
        return insights
    
    def save_results(self, results):
        """
        Save results to JSON file
        """
        try:
            with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            logger.info(f"Results saved to {OUTPUT_FILE}")
        except Exception as e:
            logger.error(f"Error saving results: {e}")
    
    def print_summary(self, summary):
        """
        Print a formatted summary to console
        """
        print("\n" + "="*60)
        print("FACT VS OPINION ANALYSIS SUMMARY")
        print("="*60)
        
        if 'overall_statistics' in summary:
            stats = summary['overall_statistics']
            print(f"\nTotal Articles Analyzed: {stats['total_articles']}")
            print(f"Average Confidence: {stats['average_confidence']:.3f}")
            
            print(f"\nClassification Distribution:")
            for classification, count in stats['classification_distribution'].items():
                percentage = (count / stats['total_articles']) * 100 if stats['total_articles'] > 0 else 0
                print(f"  {classification.replace('_', ' ').title()}: {count} ({percentage:.1f}%)")
        
        if 'key_insights' in summary:
            print(f"\nKey Insights:")
            for i, insight in enumerate(summary['key_insights'], 1):
                print(f"  {i}. {insight}")
        
        if 'source_breakdown' in summary:
            print(f"\nSource Breakdown:")
            for source, breakdown in summary['source_breakdown'].items():
                print(f"  {source.upper()}:")
                print(f"    Total articles: {breakdown['total']}")
                if breakdown['total'] > 0:
                    for classification, count in breakdown.items():
                        if classification != 'total':
                            percentage = (count / breakdown['total']) * 100
                            print(f"    {classification.replace('_', ' ').title()}: {count} ({percentage:.1f}%)")
        
        print("\n" + "="*60)

def main():
    """
    Entry point for the application
    """
    try:
        analyzer = FactOpinionAnalyzer()
        analyzer.run_analysis()
    except KeyboardInterrupt:
        logger.info("Analysis interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise

if __name__ == "__main__":
    main()