import requests
import time
import re
from typing import List, Dict, Optional, Tuple
from urllib.parse import urlparse, urljoin
from dataclasses import dataclass
import json

@dataclass
class VerifiedURL:
    original_url: str
    working_url: str
    status_code: int
    is_accessible: bool
    redirect_chain: List[str]
    final_title: str
    verification_timestamp: str
    fallback_urls: List[str]

class URLVerificationSystem:
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        self.verified_base_urls = {
            'bbc.co.uk': 'https://www.bbc.co.uk/news',
            'bbc.com': 'https://www.bbc.com/news',
            'cnn.com': 'https://edition.cnn.com',
            'reuters.com': 'https://www.reuters.com',
            'guardian.com': 'https://www.theguardian.com',
            'theguardian.com': 'https://www.theguardian.com',
            'nytimes.com': 'https://www.nytimes.com',
            'washingtonpost.com': 'https://www.washingtonpost.com',
            'npr.org': 'https://www.npr.org',
            'skynews.com': 'https://news.sky.com',
            'ap.org': 'https://apnews.com',
            'apnews.com': 'https://apnews.com',
            'aljazeera.com': 'https://www.aljazeera.com',
            'bloomberg.com': 'https://www.bloomberg.com',
            'wsj.com': 'https://www.wsj.com',
            'economist.com': 'https://www.economist.com',
            'ipcc.ch': 'https://www.ipcc.ch',
            'nasa.gov': 'https://www.nasa.gov',
            'climate.nasa.gov': 'https://climate.nasa.gov',
            'noaa.gov': 'https://www.noaa.gov',
            'who.int': 'https://www.who.int',
            'un.org': 'https://www.un.org',
            'investopedia.com': 'https://www.investopedia.com',
            'coindesk.com': 'https://www.coindesk.com',
            'coinmetrics.io': 'https://coinmetrics.io',
            'bankrate.com': 'https://www.bankrate.com',
            'metoffice.gov.uk': 'https://www.metoffice.gov.uk'
        }
        
        self.search_patterns = {
            'climate_change': [
                'https://climate.nasa.gov/evidence/',
                'https://www.ipcc.ch/reports/',
                'https://www.noaa.gov/climate',
                'https://www.metoffice.gov.uk/weather/climate-change'
            ],
            'bitcoin_price': [
                'https://www.coindesk.com/price/bitcoin/',
                'https://www.investopedia.com/terms/b/bitcoin.asp',
                'https://www.bankrate.com/investing/bitcoin-price-history/',
                'https://coinmetrics.io/charts/#assets=btc'
            ],
            'global_warming': [
                'https://climate.nasa.gov/vital-signs/global-warming/',
                'https://www.noaa.gov/climate/global-warming',
                'https://www.ipcc.ch/sr15/',
                'https://www.metoffice.gov.uk/weather/climate-change/climate-change-explained'
            ]
        }
    
    def verify_url(self, url: str, timeout: int = 10) -> VerifiedURL:
        print(f"🔍 Verifying URL: {url}")
        
        redirect_chain = []
        original_url = url
        
        try:
            response = self.session.head(url, timeout=timeout, allow_redirects=True)
            
            if response.history:
                redirect_chain = [resp.url for resp in response.history]
                redirect_chain.append(response.url)
            
            if response.status_code == 200:
                try:
                    get_response = self.session.get(url, timeout=timeout)
                    title = self._extract_title(get_response.text)
                except:
                    title = "Page accessible"
                
                print(f"✅ URL accessible: {response.status_code}")
                return VerifiedURL(
                    original_url=original_url,
                    working_url=response.url,
                    status_code=response.status_code,
                    is_accessible=True,
                    redirect_chain=redirect_chain,
                    final_title=title,
                    verification_timestamp=time.strftime('%Y-%m-%d %H:%M:%S'),
                    fallback_urls=[]
                )
            
            elif response.status_code in [301, 302, 303, 307, 308]:
                final_url = response.url
                print(f"🔄 URL redirected to: {final_url}")
                return self.verify_url(final_url, timeout)
            
            else:
                print(f"❌ URL not accessible: {response.status_code}")
                fallback_urls = self._find_fallback_urls(url)
                
                return VerifiedURL(
                    original_url=original_url,
                    working_url="",
                    status_code=response.status_code,
                    is_accessible=False,
                    redirect_chain=redirect_chain,
                    final_title="",
                    verification_timestamp=time.strftime('%Y-%m-%d %H:%M:%S'),
                    fallback_urls=fallback_urls
                )
        
        except requests.exceptions.RequestException as e:
            print(f"❌ URL verification failed: {e}")
            fallback_urls = self._find_fallback_urls(url)
            
            return VerifiedURL(
                original_url=original_url,
                working_url="",
                status_code=0,
                is_accessible=False,
                redirect_chain=[],
                final_title="",
                verification_timestamp=time.strftime('%Y-%m-%d %H:%M:%S'),
                fallback_urls=fallback_urls
            )
    
    def _extract_title(self, html_content: str) -> str:
        try:
            title_match = re.search(r'<title[^>]*>(.*?)</title>', html_content, re.IGNORECASE | re.DOTALL)
            if title_match:
                title = title_match.group(1).strip()
                title = re.sub(r'\s+', ' ', title)
                return title[:200]  
            return "No title found"
        except:
            return "Title extraction failed"
    
    def _find_fallback_urls(self, broken_url: str) -> List[str]:
        fallback_urls = []
        
        try:
            parsed_url = urlparse(broken_url)
            domain = parsed_url.netloc.lower()
            
            clean_domain = domain.replace('www.', '')
            
            if clean_domain in self.verified_base_urls:
                base_url = self.verified_base_urls[clean_domain]
                verified_base = self.verify_url(base_url, timeout=5)
                if verified_base.is_accessible:
                    fallback_urls.append(base_url)
            
            url_lower = broken_url.lower()
            if any(term in url_lower for term in ['climate', 'temperature', 'warming', 'ipcc']):
                for pattern_url in self.search_patterns['climate_change']:
                    verified = self.verify_url(pattern_url, timeout=5)
                    if verified.is_accessible:
                        fallback_urls.append(pattern_url)
                        break
            
            elif any(term in url_lower for term in ['bitcoin', 'btc', 'crypto', 'price']):
                for pattern_url in self.search_patterns['bitcoin_price']:
                    verified = self.verify_url(pattern_url, timeout=5)
                    if verified.is_accessible:
                        fallback_urls.append(pattern_url)
                        break
            
            if not fallback_urls:
                homepage = f"https://{domain}"
                verified_homepage = self.verify_url(homepage, timeout=5)
                if verified_homepage.is_accessible:
                    fallback_urls.append(homepage)
        
        except Exception as e:
            print(f"Error finding fallback URLs: {e}")
        
        return fallback_urls[:3]  
    
    def verify_citation_urls(self, citations: List[Dict]) -> List[Dict]:
        print(f"🔍 Verifying {len(citations)} citation URLs...")
        
        verified_citations = []
        
        for i, citation in enumerate(citations, 1):
            print(f"   Verifying citation {i}/{len(citations)}...")
            
            url = citation.get('url', '')
            if not url:
                print(f"   ⚠️  Citation {i} has no URL")
                verified_citations.append(citation)
                continue
            
            verification = self.verify_url(url)
            
            updated_citation = citation.copy()
            updated_citation['url_verification'] = {
                'is_accessible': verification.is_accessible,
                'status_code': verification.status_code,
                'verification_timestamp': verification.verification_timestamp,
                'redirect_chain': verification.redirect_chain
            }
            
            if verification.is_accessible:
                updated_citation['url'] = verification.working_url
                updated_citation['verified_title'] = verification.final_title
                print(f"   ✅ Citation {i} URL is accessible")
            else:
                print(f"   ❌ Citation {i} URL is broken (status: {verification.status_code})")
                
                if verification.fallback_urls:
                    updated_citation['url'] = verification.fallback_urls[0]
                    updated_citation['original_broken_url'] = verification.original_url
                    updated_citation['fallback_urls'] = verification.fallback_urls
                    updated_citation['url_status'] = 'fixed_with_fallback'
                    print(f"   🔧 Citation {i} fixed with fallback URL: {verification.fallback_urls[0]}")
                else:
                    updated_citation['url_status'] = 'broken_no_fallback'
                    updated_citation['broken_url'] = verification.original_url
                    print(f"   ⚠️  Citation {i} could not be fixed - no working fallback found")
            
            verified_citations.append(updated_citation)
            
            time.sleep(1)
        
        working_count = len([c for c in verified_citations if c.get('url_verification', {}).get('is_accessible', False)])
        print(f"✅ URL verification complete: {working_count}/{len(citations)} URLs are accessible")
        
        return verified_citations
    
    def generate_verified_sources_report(self, verified_citations: List[Dict]) -> str:
        
        working_citations = [c for c in verified_citations if c.get('url_verification', {}).get('is_accessible', False)]
        broken_citations = [c for c in verified_citations if not c.get('url_verification', {}).get('is_accessible', False)]
        fixed_citations = [c for c in verified_citations if c.get('url_status') == 'fixed_with_fallback']
        
        report = f"""# Verified Sources Report with Working URLs

*Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}*

- **Total Citations Checked:** {len(verified_citations)}
- **Working URLs:** {len(working_citations)}
- **Fixed with Fallbacks:** {len(fixed_citations)}
- **Broken URLs:** {len(broken_citations)}
- **Success Rate:** {(len(working_citations) / len(verified_citations) * 100):.1f}%


"""
        
        for i, citation in enumerate(working_citations, 1):
            title = citation.get('title', 'Unknown Title')
            url = citation.get('url', '')
            domain = citation.get('domain', '')
            verification = citation.get('url_verification', {})
            
            report += f"**{i}.** {title}\n\n"
            report += f"   - **URL:** [{url}]({url})\n"
            report += f"   - **Domain:** {domain}\n"
            report += f"   - **Status:** ✅ Accessible (HTTP {verification.get('status_code', 'Unknown')})\n"
            report += f"   - **Verified:** {verification.get('verification_timestamp', 'Unknown')}\n"
            
            if citation.get('snippet'):
                report += f"   - **Excerpt:** \"{citation['snippet'][:150]}...\"\n"
            
            if citation.get('url_status') == 'fixed_with_fallback':
                report += f"   - **Note:** ⚠️ Original URL was broken, using verified fallback\n"
                report += f"   - **Original URL:** {citation.get('original_broken_url', 'Unknown')}\n"
            
            report += "\n"
        
        if broken_citations:
            report += "## ❌ Broken URLs (Could Not Be Fixed)\n\n"
            
            for i, citation in enumerate(broken_citations, 1):
                if citation.get('url_status') != 'fixed_with_fallback':
                    title = citation.get('title', 'Unknown Title')
                    broken_url = citation.get('broken_url', citation.get('url', ''))
                    verification = citation.get('url_verification', {})
                    
                    report += f"**{i}.** {title}\n"
                    report += f"   - **Broken URL:** {broken_url}\n"
                    report += f"   - **Status:** ❌ HTTP {verification.get('status_code', 'Unknown')}\n"
                    report += f"   - **Checked:** {verification.get('verification_timestamp', 'Unknown')}\n"
                    
                    if citation.get('fallback_urls'):
                        report += f"   - **Suggested Alternatives:** {', '.join(citation['fallback_urls'])}\n"
                    
                    report += "\n"
        
        report += """
## Verification Process
1. Each URL was tested with HTTP HEAD/GET requests
2. Redirect chains were followed automatically
3. Broken URLs were replaced with verified alternatives when possible
4. All working URLs were confirmed accessible at generation time

---
*All URLs in the "Verified Working Sources" section have been confirmed accessible and should work when clicked.*
"""
        
        return report

if __name__ == "__main__":
    print("🔍 Testing URL Verification and Correction System")
    print("=" * 60)
    
    verification_system = URLVerificationSystem()
    
    test_citations = [
        {
            'title': 'Climate Change 2021: The Physical Science Basis',
            'url': 'https://www.ipcc.ch/report/ar6/wg1/',
            'domain': 'ipcc.ch',
            'snippet': 'Global surface temperature has increased...'
        },
        {
            'title': 'Bitcoin Price History',
            'url': 'https://www.coindesk.com/price/bitcoin/',
            'domain': 'coindesk.com',
            'snippet': 'Bitcoin price reached new highs...'
        },
        {
            'title': 'NASA Climate Evidence',
            'url': 'https://climate.nasa.gov/evidence/',
            'domain': 'climate.nasa.gov',
            'snippet': 'Evidence for climate change...'
        },
        {
            'title': 'Broken BBC Link Example',
            'url': 'https://www.bbc.co.uk/news/world-middle-east-68934567',  # Likely broken
            'domain': 'bbc.co.uk',
            'snippet': 'This is an example of a potentially broken link...'
        }
    ]
    
    verified_citations = verification_system.verify_citation_urls(test_citations)
    
    report = verification_system.generate_verified_sources_report(verified_citations)
    
    report_filename = f"verified_sources_report_{time.strftime('%Y%m%d_%H%M%S')}.md"
    with open(report_filename, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n✅ URL verification test complete!")
    print(f"📄 Report saved to: {report_filename}")