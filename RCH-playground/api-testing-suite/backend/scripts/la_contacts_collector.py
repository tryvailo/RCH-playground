#!/usr/bin/env python3
"""
Local Authority Contacts Collector Script
Automated collection of contact information for all 152 UK Local Authorities

Based on implementation_guide_152_la.md methodology
"""

import json
import re
import time
import random
import asyncio
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import httpx
from bs4 import BeautifulSoup
import logging
from urllib.parse import urljoin

# Try to import Firecrawl client
try:
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from api_clients.firecrawl_client import FirecrawlAPIClient
    from config_manager import get_credentials
    FIRECRAWL_AVAILABLE = True
except ImportError as e:
    FIRECRAWL_AVAILABLE = False
    FirecrawlAPIClient = None
    get_credentials = None

# Try to import external sources service
try:
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from services.la_external_sources import LAExternalSources
    EXTERNAL_SOURCES_AVAILABLE = True
except ImportError as e:
    EXTERNAL_SOURCES_AVAILABLE = False
    LAExternalSources = None

# Try to import external sources service
try:
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from services.la_external_sources import LAExternalSources
    EXTERNAL_SOURCES_AVAILABLE = True
except ImportError as e:
    EXTERNAL_SOURCES_AVAILABLE = False
    LAExternalSources = None

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
BASE_DIR = Path(__file__).parent.parent
DATA_FILE = BASE_DIR / "data" / "local_authority_contacts.json"
BACKUP_DIR = BASE_DIR / "data" / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

# Rate limiting
REQUEST_DELAY = (2, 4)  # Random delay between requests (seconds)
MAX_RETRIES = 3

# User agents for scraping
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
]


class LAContactsCollector:
    """Collect Local Authority contact information"""
    
    def __init__(self, use_firecrawl: bool = True):
        self.client = httpx.Client(
            timeout=30.0,
            headers={'User-Agent': random.choice(USER_AGENTS)},
            follow_redirects=True
        )
        self.data: Dict[str, Any] = {}
        self.stats = {
            'total': 0,
            'processed': 0,
            'updated': 0,
            'failed': 0,
            'skipped': 0,
            'firecrawl_used': 0,
            'firecrawl_failed': 0
        }
        
        # Initialize Firecrawl client if available
        self.firecrawl_client = None
        if use_firecrawl and FIRECRAWL_AVAILABLE and get_credentials:
            try:
                creds = get_credentials()
                api_key = None
                
                # Try to get API key from credentials
                if creds and hasattr(creds, 'firecrawl') and creds.firecrawl:
                    api_key = getattr(creds.firecrawl, 'api_key', None) or getattr(creds.firecrawl, 'apiKey', None)
                
                # Fallback: try to read directly from config file
                if not api_key:
                    try:
                        config_file = Path(__file__).parent.parent / "config.json"
                        if config_file.exists():
                            with open(config_file, 'r') as f:
                                config_data = json.load(f)
                                firecrawl_config = config_data.get('firecrawl', {})
                                api_key = firecrawl_config.get('api_key') or firecrawl_config.get('apiKey')
                    except Exception as e:
                        logger.debug(f"Could not read config file: {e}")
                
                if api_key and api_key.strip():
                    self.firecrawl_client = FirecrawlAPIClient(api_key=api_key)
                    logger.info("✅ Firecrawl client initialized")
                else:
                    logger.warning("⚠️ Firecrawl API key not configured (empty or missing)")
            except Exception as e:
                logger.warning(f"⚠️ Failed to initialize Firecrawl: {e}")
        elif use_firecrawl and not FIRECRAWL_AVAILABLE:
            logger.warning("⚠️ Firecrawl not available (import failed)")
        
        # Initialize external sources service
        self.external_sources = None
        if EXTERNAL_SOURCES_AVAILABLE:
            try:
                self.external_sources = LAExternalSources()
                logger.info("✅ External sources service initialized")
            except Exception as e:
                logger.warning(f"⚠️ Failed to initialize external sources: {e}")
    
    def load_data(self) -> Dict[str, Any]:
        """Load existing LA contacts data"""
        if not DATA_FILE.exists():
            logger.error(f"Data file not found: {DATA_FILE}")
            return {}
        
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        logger.info(f"Loaded {len(data.get('councils', []))} councils from database")
        return data
    
    def save_backup(self):
        """Create backup before making changes"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = BACKUP_DIR / f"local_authority_contacts_backup_{timestamp}.json"
        
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Backup created: {backup_file}")
    
    def save_data(self):
        """Save updated data to file"""
        # Update metadata
        if 'metadata' not in self.data:
            self.data['metadata'] = {}
        
        self.data['metadata']['last_updated'] = datetime.now().strftime("%Y-%m-%d")
        self.data['metadata']['last_collection_run'] = datetime.now().isoformat()
        
        # Count verified councils
        verified_count = sum(
            1 for c in self.data.get('councils', [])
            if c.get('asc_phone') or c.get('asc_email')
        )
        self.data['metadata']['councils_with_full_contacts'] = verified_count
        
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Data saved to {DATA_FILE}")
    
    def extract_phone(self, text: str) -> Optional[str]:
        """Extract phone number from text with improved patterns"""
        # UK phone number patterns - more comprehensive
        patterns = [
            # Standard UK formats
            r'0\d{2,4}[\s-]?\d{3,4}[\s-]?\d{3,4}',  # Standard UK format with optional separators
            r'\+44[\s-]?\d{2,4}[\s-]?\d{3,4}[\s-]?\d{3,4}',  # International format
            r'\(0\d{2,4}\)[\s-]?\d{3,4}[\s-]?\d{3,4}',  # With brackets
            r'0\d{2,4}\.\d{3,4}\.\d{3,4}',  # With dots
            # Freephone and special numbers
            r'0(?:300|800|500)[\s-]?\d{3}[\s-]?\d{4}',  # 0300, 0800, 0500 numbers
            r'0(?:300|800|500)\s?\d{6}',  # Without separator
            # Emergency and helpline formats
            r'0\d{3}\s?\d{3}\s?\d{4}',  # 11-digit format
            r'0\d{4}\s?\d{3}\s?\d{3}',  # Alternative 11-digit
        ]
        
        # Also look for phone numbers in tel: links
        tel_pattern = r'tel:[\s+]?([0-9\s\+\-\(\)]+)'
        tel_matches = re.findall(tel_pattern, text, re.I)
        if tel_matches:
            phone = tel_matches[0].strip()
            # Clean up
            phone = re.sub(r'[\s\+\-\(\)]', '', phone)
            if phone.startswith('44'):
                phone = '0' + phone[2:]
            if len(phone) >= 10 and phone.startswith('0'):
                return phone
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            if matches:
                # Clean and return first match
                phone = matches[0].strip()
                # Remove common prefixes
                phone = re.sub(r'^(Tel|Phone|Call|Telephone|T)[:\s]+', '', phone, flags=re.I)
                # Normalize separators
                phone = re.sub(r'[\s\.\-]+', ' ', phone)
                # Remove invalid patterns (too short/long)
                digits_only = re.sub(r'[^\d]', '', phone)
                if 10 <= len(digits_only) <= 13:
                    return phone.strip()
        
        return None
    
    def extract_email(self, text: str) -> Optional[str]:
        """Extract email address from text with improved patterns"""
        # More comprehensive email patterns
        patterns = [
            # Standard email
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            # Email in mailto: links
            r'mailto:[\s+]?([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})',
            # Email with spaces (common in web pages)
            r'([A-Za-z0-9._%+-]+)\s*@\s*([A-Za-z0-9.-]+\.[A-Z|a-z]{2,})',
            # Email in parentheses or brackets
            r'[\(\[{]([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})[\)\]}]',
            # Email with "at" or "dot" (obfuscated)
            r'([A-Za-z0-9._%+-]+)\s*(?:at|@)\s*([A-Za-z0-9.-]+)\s*(?:dot|\.)\s*([A-Z|a-z]{2,})',
        ]
        
        all_emails = []
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.I)
            if matches:
                for match in matches:
                    if isinstance(match, tuple):
                        # Reconstruct email from tuple
                        email = ''.join(match).replace('at', '@').replace('dot', '.')
                    else:
                        email = match
                    
                    # Clean up
                    email = email.strip().lower()
                    email = re.sub(r'\s+', '', email)  # Remove spaces
                    
                    # Validate basic email format
                    if re.match(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$', email):
                        all_emails.append(email)
        
        if all_emails:
            # Filter out common non-contact emails
            exclude_patterns = [
                r'noreply', r'no-reply', r'donotreply', r'example',
                r'test@', r'sample@', r'placeholder@', r'webmaster',
                r'admin@', r'info@.*example', r'contact@.*test'
            ]
            
            # Also exclude generic addresses that are likely not contact emails
            exclude_domains = ['example.com', 'test.com', 'sample.com', 'placeholder.com']
            
            for email in all_emails:
                email_lower = email.lower()
                
                # Check exclude patterns
                if any(re.search(exclude, email_lower) for exclude in exclude_patterns):
                    continue
                
                # Check exclude domains
                if any(domain in email_lower for domain in exclude_domains):
                    continue
                
                # Prefer council-related domains (.gov.uk, .gov, council-related)
                if '.gov.uk' in email_lower or 'council' in email_lower or 'gov' in email_lower:
                    return email
                
                # Return first valid email
                return email
        
        return None
    
    def find_council_website(self, council_name: str) -> Optional[str]:
        """Try to find council website URL and Adult Social Care page"""
        # Common patterns
        name_clean = council_name.lower()
        
        # Handle London Boroughs and Royal Boroughs specially
        is_london_borough = 'london borough of' in name_clean or 'royal borough of' in name_clean
        
        if is_london_borough:
            # Extract borough name
            if 'royal borough of' in name_clean:
                borough_name = name_clean.replace('royal borough of ', '').strip()
            else:
                borough_name = name_clean.replace('london borough of ', '').strip()
            
            # Special cases for London Boroughs
            london_special = {
                'barking and dagenham': ['lbbd.gov.uk'],
                'hammersmith and fulham': ['lbhf.gov.uk', 'hammersmithfulham.gov.uk'],
                'kensington and chelsea': ['rbkc.gov.uk', 'kensingtonchelsea.gov.uk'],
                'kingston upon thames': ['kingston.gov.uk'],
                'richmond upon thames': ['richmond.gov.uk'],
                'westminster': ['westminster.gov.uk'],
                'greenwich': ['royalgreenwich.gov.uk', 'greenwich.gov.uk'],
            }
            
            borough_key = borough_name.lower()
            if borough_key in london_special:
                patterns = [f"https://www.{domain}" if not domain.startswith('http') else domain 
                           for domain in london_special[borough_key]]
                patterns.extend([f"https://{domain}" if not domain.startswith('http') else domain 
                                 for domain in london_special[borough_key]])
            # Handle "and" in names (e.g., "Barking and Dagenham")
            elif ' and ' in borough_name:
                parts = borough_name.split(' and ')
                # Try different combinations
                patterns = [
                    f"https://www.{parts[0]}.gov.uk",  # e.g., barking.gov.uk
                    f"https://{parts[0]}.gov.uk",
                    f"https://www.{parts[0]}{parts[1]}.gov.uk",  # e.g., barkingdagenham.gov.uk
                    f"https://www.{parts[0]}and{parts[1]}.gov.uk",  # e.g., barkinganddagenham.gov.uk
                ]
            else:
                # Single word borough
                patterns = [
                    f"https://www.{borough_name}.gov.uk",
                    f"https://{borough_name}.gov.uk",
                ]
        else:
            # Non-London councils
            name_clean = name_clean.replace(' county council', '').replace(' borough council', '')
            name_clean = name_clean.replace(' city council', '').replace(' council', '')
            name_clean = name_clean.replace(' ', '').replace("'", '')
            
            # Special cases
            special_cases = {
                'hampshire': 'hants',
                'east sussex': 'eastsussex',
                'west sussex': 'westsussex',
                'north yorkshire': 'northyorks',
                'south yorkshire': 'southyorks',
                'luton': 'luton',  # Luton uses different pattern
            }
            
            if name_clean in special_cases:
                name_clean = special_cases[name_clean]
            
            # Try common domain patterns
            patterns = [
                f"https://www.{name_clean}.gov.uk",
                f"https://{name_clean}.gov.uk",
                f"https://www.{name_clean}borough.gov.uk",
                f"https://www.{name_clean}city.gov.uk",
            ]
        
        # Try common domain patterns - first try main site
        base_patterns = patterns
        
        base_url = None
        blocked_urls = []  # Track URLs that return 403 (we can use Firecrawl for these)
        
        for url in base_patterns:
            try:
                # Try HEAD first, but some sites block HEAD requests
                response = self.client.head(url, timeout=5.0, follow_redirects=True)
                if response.status_code == 200:
                    base_url = url
                    break
                # If 403, try GET with different user agent
                elif response.status_code == 403:
                    blocked_urls.append(url)
                    # Try with GET and different headers
                    headers = {'User-Agent': random.choice(USER_AGENTS)}
                    get_response = self.client.get(url, timeout=5.0, follow_redirects=True, headers=headers)
                    if get_response.status_code == 200:
                        base_url = url
                        break
            except httpx.HTTPStatusError as e:
                # If 403, note it for Firecrawl
                if e.response.status_code == 403:
                    blocked_urls.append(url)
                    try:
                        headers = {'User-Agent': random.choice(USER_AGENTS)}
                        get_response = self.client.get(url, timeout=5.0, follow_redirects=True, headers=headers)
                        if get_response.status_code == 200:
                            base_url = url
                            break
                    except:
                        continue
            except Exception as e:
                # Try GET as fallback
                try:
                    headers = {'User-Agent': random.choice(USER_AGENTS)}
                    get_response = self.client.get(url, timeout=5.0, follow_redirects=True, headers=headers)
                    if get_response.status_code == 200:
                        base_url = url
                        break
                    elif get_response.status_code == 403:
                        blocked_urls.append(url)
                except:
                    continue
        
        # If no accessible URL found but we have blocked URLs and Firecrawl, use first blocked URL
        if not base_url and blocked_urls and self.firecrawl_client:
            base_url = blocked_urls[0]
            logger.info(f"  Site blocks access (403) - will use Firecrawl: {base_url}")
        elif not base_url:
            return None
        
        # Try to find Adult Social Care page or Contact page
        # Priority: Contact pages first (more likely to have direct contact info)
        contact_paths = [
            '/contact-us',
            '/contact',
            '/get-in-touch',
            '/contact-adult-social-care',
            '/contact-social-care',
        ]
        
        # Then try Adult Social Care pages
        asc_paths = [
            '/adult-social-care',
            '/social-care-and-health/adult-social-care',
            '/care-and-support/adults',
            '/adults',
            '/social-care',
            '/health-and-social-care/adult-social-care',
            '/adult-social-care/contact',
            '/adult-social-care/contact-us',
        ]
        
        # Try contact pages first
        contact_url = None
        blocked_contact_urls = []
        
        for path in contact_paths:
            try:
                url = base_url.rstrip('/') + path
                response = self.client.head(url, timeout=5.0, follow_redirects=True)
                if response.status_code == 200:
                    contact_url = url
                    logger.info(f"  Found contact page: {contact_url}")
                    break
                elif response.status_code == 403:
                    blocked_contact_urls.append(url)
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 403:
                    blocked_contact_urls.append(url)
            except:
                continue
        
        # If no contact page, try ASC pages
        asc_url = None
        blocked_asc_urls = []
        
        if not contact_url:
            for path in asc_paths:
                try:
                    url = base_url.rstrip('/') + path
                    response = self.client.head(url, timeout=5.0, follow_redirects=True)
                    if response.status_code == 200:
                        asc_url = url
                        logger.info(f"  Found ASC page: {asc_url}")
                        break
                    elif response.status_code == 403:
                        blocked_asc_urls.append(url)
                except httpx.HTTPStatusError as e:
                    if e.response.status_code == 403:
                        blocked_asc_urls.append(url)
                except:
                    continue
        
        # Prioritize contact pages, then ASC pages
        final_url = contact_url or asc_url
        blocked_urls = blocked_contact_urls + blocked_asc_urls
        
        # If no accessible URL but we have blocked URLs and Firecrawl, use first blocked URL
        if not final_url and blocked_urls and self.firecrawl_client:
            final_url = blocked_urls[0]
            logger.info(f"  Contact/ASC page blocks access (403) - will use Firecrawl: {final_url}")
        elif not final_url:
            # Return base URL if no specific page found
            return base_url
        
        return final_url
    
    def search_google(self, query: str) -> List[str]:
        """Search Google for council contact information"""
        # Note: This is a simplified version. For production, use Google Custom Search API
        # or a proper search API service
        try:
            search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            response = self.client.get(search_url, timeout=10.0)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                links = []
                
                # Extract search result links
                for link in soup.find_all('a', href=True):
                    href = link.get('href')
                    if href and ('gov.uk' in href or 'council' in href.lower()):
                        if href.startswith('/url?q='):
                            href = href.split('/url?q=')[1].split('&')[0]
                        links.append(href)
                
                return links[:5]  # Return top 5 results
        except Exception as e:
            logger.warning(f"Google search failed: {e}")
        
        return []
    
    async def scrape_with_firecrawl(self, url: str) -> Optional[Dict[str, Any]]:
        """Scrape council page using Firecrawl (for protected sites)"""
        if not self.firecrawl_client:
            return None
        
        try:
            logger.info(f"  🔥 Using Firecrawl to scrape {url}")
            
            # Use Firecrawl to scrape the page
            result = await self.firecrawl_client.scrape_url(
                url=url,
                formats=[{"type": "markdown"}, {"type": "html"}],
                only_main_content=True
            )
            
            # Debug: log result structure
            logger.debug(f"  Firecrawl result type: {type(result)}, keys: {list(result.keys()) if isinstance(result, dict) else 'N/A'}")
            
            # Firecrawl API v2 may return data in 'data' key
            data = result.get('data') if isinstance(result, dict) and 'data' in result else result
            
            # Extract markdown and HTML
            markdown = None
            html = None
            
            if isinstance(data, dict):
                markdown = data.get('markdown') or data.get('content') or data.get('text')
                html = data.get('html')
            elif isinstance(data, str):
                markdown = data
            
            # Also check top-level result
            if not markdown and isinstance(result, dict):
                markdown = result.get('markdown') or result.get('content') or result.get('text')
            if not html and isinstance(result, dict):
                html = result.get('html')
            
            if markdown or html:
                # Parse HTML if available
                soup = None
                if html:
                    soup = BeautifulSoup(html, 'html.parser')
                    text = soup.get_text()
                elif markdown:
                    text = markdown
                else:
                    text = ''
                
                # Extract contact information
                phone = self.extract_phone(text)
                email = self.extract_email(text)
                
                logger.info(f"  ✓ Firecrawl extracted: phone={bool(phone)}, email={bool(email)}, text_len={len(text)}")
                
                return {
                    'text': text,
                    'html': html or '',
                    'phone': phone,
                    'email': email,
                    'soup': soup
                }
            
            logger.warning(f"  ⚠️ Firecrawl: no markdown/html found. Result keys: {list(result.keys()) if isinstance(result, dict) else 'not a dict'}")
            return None
        except Exception as e:
            logger.warning(f"  ⚠️ Firecrawl scraping failed: {e}")
            return None
    
    async def scrape_council_page(self, url: str) -> Dict[str, Optional[str]]:
        """Scrape contact information from council website"""
        result = {
            'asc_phone': None,
            'asc_email': None,
            'asc_website_url': url,
            'assessment_url': None,
            'office_address': None,
            'opening_hours': None,
        }
        
        # Try regular scraping first
        try:
            response = self.client.get(url, timeout=15.0)
            if response.status_code == 403:
                # Site blocks us - try Firecrawl if available
                if self.firecrawl_client:
                    logger.info(f"  🔥 Site blocked (403), trying Firecrawl...")
                    try:
                        # We're already in async context, just await
                        firecrawl_result = await self.scrape_with_firecrawl(url)
                        if firecrawl_result:
                            self.stats['firecrawl_used'] += 1
                            text = firecrawl_result.get('text', '')
                            soup = firecrawl_result.get('soup')
                            
                            # Use extracted data from Firecrawl
                            if firecrawl_result.get('phone'):
                                result['asc_phone'] = firecrawl_result['phone']
                            if firecrawl_result.get('email'):
                                result['asc_email'] = firecrawl_result['email']
                            # Mark that Firecrawl was used
                            result['firecrawl_used'] = True
                            result['source'] = 'firecrawl'
                            
                            # Continue with address and other fields extraction
                            if soup:
                                # Look for contact forms and extract data from them
                                forms = soup.find_all('form')
                                for form in forms:
                                    form_text = form.get_text().lower()
                                    # Look for email inputs
                                    email_inputs = form.find_all(['input', 'textarea'], {'type': 'email', 'name': re.compile(r'email|contact', re.I)})
                                    for inp in email_inputs:
                                        value = inp.get('value') or inp.get('placeholder', '')
                                        if value and '@' in value:
                                            email = self.extract_email(value)
                                            if email and not result['asc_email']:
                                                result['asc_email'] = email
                                    
                                    # Look for phone inputs
                                    phone_inputs = form.find_all(['input', 'textarea'], {'type': 'tel', 'name': re.compile(r'phone|tel|contact', re.I)})
                                    for inp in phone_inputs:
                                        value = inp.get('value') or inp.get('placeholder', '')
                                        if value:
                                            phone = self.extract_phone(value)
                                            if phone and not result['asc_phone']:
                                                result['asc_phone'] = phone
                                
                                # Look for contact information in structured data (microdata, JSON-LD)
                                # Check for JSON-LD structured data
                                json_ld_scripts = soup.find_all('script', {'type': 'application/ld+json'})
                                for script in json_ld_scripts:
                                    try:
                                        data = json.loads(script.string)
                                        if isinstance(data, dict):
                                            # Look for ContactPoint
                                            contact_points = data.get('contactPoint', [])
                                            if not isinstance(contact_points, list):
                                                contact_points = [contact_points]
                                            
                                            for cp in contact_points:
                                                if isinstance(cp, dict):
                                                    email = cp.get('email')
                                                    phone = cp.get('telephone')
                                                    if email and not result['asc_email']:
                                                        result['asc_email'] = email
                                                    if phone and not result['asc_phone']:
                                                        result['asc_phone'] = phone
                                    except:
                                        pass
                                
                                # Look for assessment URL
                                for link in soup.find_all('a', href=True):
                                    href = link.get('href', '')
                                    text_lower = link.get_text().lower()
                                    
                                    if any(keyword in href or keyword in text_lower for keyword in [
                                        'assessment', 'request', 'apply', 'book', 'referral'
                                    ]):
                                        if href.startswith('http'):
                                            result['assessment_url'] = href
                                        elif href.startswith('/'):
                                            result['assessment_url'] = urljoin(url, href)
                                
                                # Look for address
                                address_patterns = [
                                    r'\d+[A-Za-z\s,]+(?:Street|Road|Avenue|Lane|Close|Way|Drive|Place)[A-Za-z\s,]*[A-Z]{1,2}\d{1,2}\s?\d[A-Z]{2}',
                                    r'[A-Za-z\s]+(?:County Hall|Town Hall|Civic Centre)[A-Za-z\s,]*[A-Z]{1,2}\d{1,2}\s?\d[A-Z]{2}',
                                ]
                                
                                for pattern in address_patterns:
                                    matches = re.findall(pattern, text)
                                    if matches:
                                        result['office_address'] = matches[0].strip()
                                        break
                                
                                # Look for opening hours
                                hours_pattern = r'(?:Mon|Mon-Fri|Monday|Monday-Friday)[\s\w:,-]+(?:am|pm)'
                                hours_matches = re.findall(hours_pattern, text, re.IGNORECASE)
                                if hours_matches:
                                    result['opening_hours'] = hours_matches[0].strip()
                            
                            return result
                        else:
                            self.stats['firecrawl_failed'] += 1
                            logger.warning(f"  ⚠️ Firecrawl returned no data for {url}")
                    except Exception as e:
                        self.stats['firecrawl_failed'] += 1
                        logger.warning(f"  ⚠️ Firecrawl error: {e}")
                # If no Firecrawl or it failed, return empty result
                return result
            
            if response.status_code != 200:
                return result
            
            soup = BeautifulSoup(response.content, 'html.parser')
            text = soup.get_text()
            html_content = str(soup)
            
            # Look for contact sections first (more comprehensive search)
            contact_selectors = [
                {'class': re.compile(r'contact|phone|email|tel', re.I)},
                {'id': re.compile(r'contact|phone|email|tel', re.I)},
                {'data-module': re.compile(r'contact', re.I)},
            ]
            
            contact_sections = []
            for selector in contact_selectors:
                contact_sections.extend(soup.find_all(['div', 'section', 'aside', 'article'], selector))
            
            # Also look for specific contact-related elements
            contact_sections.extend(soup.find_all(['address', 'dl', 'ul'], class_=re.compile(r'contact', re.I)))
            
            contact_text = ' '.join([s.get_text() for s in contact_sections]) if contact_sections else text
            
            # Extract phone - try contact sections first, then full text
            phone = self.extract_phone(contact_text) or self.extract_phone(text)
            
            # Also look for phone in links
            if not phone:
                for link in soup.find_all('a', href=True):
                    href = link.get('href', '')
                    if href.startswith('tel:'):
                        phone = href.replace('tel:', '').strip()
                        break
            
            if phone:
                result['asc_phone'] = phone
            
            # Extract email - try contact sections first
            email = self.extract_email(contact_text) or self.extract_email(text)
            
            # Also look for email in links
            if not email:
                for link in soup.find_all('a', href=True):
                    href = link.get('href', '')
                    if href.startswith('mailto:'):
                        email = href.replace('mailto:', '').strip()
                        break
            
            if email:
                result['asc_email'] = email
            
            # Look for contact forms and extract data from them
            forms = soup.find_all('form')
            for form in forms:
                form_text = form.get_text().lower()
                # Look for email inputs in forms
                email_inputs = form.find_all(['input', 'textarea'], {'type': 'email', 'name': re.compile(r'email|contact', re.I)})
                for inp in email_inputs:
                    value = inp.get('value') or inp.get('placeholder', '')
                    if value and '@' in value:
                        form_email = self.extract_email(value)
                        if form_email and not result['asc_email']:
                            result['asc_email'] = form_email
                
                # Look for phone inputs in forms
                phone_inputs = form.find_all(['input', 'textarea'], {'type': 'tel', 'name': re.compile(r'phone|tel|contact', re.I)})
                for inp in phone_inputs:
                    value = inp.get('value') or inp.get('placeholder', '')
                    if value:
                        form_phone = self.extract_phone(value)
                        if form_phone and not result['asc_phone']:
                            result['asc_phone'] = form_phone
            
            # Look for contact information in structured data (JSON-LD)
            json_ld_scripts = soup.find_all('script', {'type': 'application/ld+json'})
            for script in json_ld_scripts:
                try:
                    data = json.loads(script.string)
                    if isinstance(data, dict):
                        # Look for ContactPoint
                        contact_points = data.get('contactPoint', [])
                        if not isinstance(contact_points, list):
                            contact_points = [contact_points]
                        
                        for cp in contact_points:
                            if isinstance(cp, dict):
                                email = cp.get('email')
                                phone = cp.get('telephone')
                                if email and not result['asc_email']:
                                    result['asc_email'] = email
                                if phone and not result['asc_phone']:
                                    result['asc_phone'] = phone
                except:
                    pass
            
            # Look for assessment/booking links
            for link in soup.find_all('a', href=True):
                href = link.get('href', '').lower()
                text_lower = link.get_text().lower()
                
                if any(keyword in href or keyword in text_lower for keyword in [
                    'assessment', 'request', 'apply', 'book', 'referral'
                ]):
                    if href.startswith('http'):
                        result['assessment_url'] = href
                    elif href.startswith('/'):
                        result['assessment_url'] = urljoin(url, href)
            
            # Look for address
            address_patterns = [
                r'\d+[A-Za-z\s,]+(?:Street|Road|Avenue|Lane|Close|Way|Drive|Place)[A-Za-z\s,]*[A-Z]{1,2}\d{1,2}\s?\d[A-Z]{2}',
                r'[A-Za-z\s]+(?:County Hall|Town Hall|Civic Centre)[A-Za-z\s,]*[A-Z]{1,2}\d{1,2}\s?\d[A-Z]{2}',
            ]
            
            for pattern in address_patterns:
                matches = re.findall(pattern, text)
                if matches:
                    result['office_address'] = matches[0].strip()
                    break
            
            # Look for opening hours
            hours_pattern = r'(?:Mon|Mon-Fri|Monday|Monday-Friday)[\s\w:,-]+(?:am|pm)'
            hours_matches = re.findall(hours_pattern, text, re.IGNORECASE)
            if hours_matches:
                result['opening_hours'] = hours_matches[0].strip()
            
            # Set source for regular web scraping
            if not result.get('source'):
                result['source'] = 'web_scraping'
        
        except Exception as e:
            logger.warning(f"Error scraping {url}: {e}")
        
        return result
    
    async def collect_for_council(self, council: Dict[str, Any]) -> Dict[str, Any]:
        """Collect contact information for a single council"""
        council_name = council.get('council_name', '')
        
        # Skip if already has phone and email
        if council.get('asc_phone') and council.get('asc_email'):
            logger.info(f"✓ {council_name} - Already has complete data")
            self.stats['skipped'] += 1
            return council
        
        logger.info(f"Collecting data for {council_name}...")
        
        # Track if we got data from external sources
        external_source_used = None
        
        # Step 1: Try external sources first (faster, more reliable)
        if self.external_sources:
            try:
                logger.info(f"  🔍 Trying external sources...")
                enriched = await self.external_sources.enrich_council_data(council)
                
                # Check if enriched has a source
                if enriched.get('source'):
                    external_source_used = enriched['source']
                    logger.debug(f"  Source from external: {external_source_used}")
                    
                    # Check if Google Places actually found data (phone or website)
                    google_places_found_data = enriched.get('asc_phone') or enriched.get('asc_website_url')
                    
                    # If data came from Google Places AND it found actual data, skip web scraping completely
                    # Google Places provides phone numbers reliably, and we don't want to overwrite the source
                    if external_source_used == 'google_places' and google_places_found_data:
                        logger.info(f"  ✓ Google Places found data - skipping web scraping to preserve source")
                        # Update council with enriched data and source
                        if not council.get('source') or council.get('source') != 'google_places':
                            council['source'] = 'google_places'
                            council['last_updated'] = datetime.now().isoformat()
                        # Only update fields that are missing
                        updated_fields = False
                        for key in ['asc_phone', 'asc_email', 'asc_website_url', 'office_address']:
                            if enriched.get(key) and not council.get(key):
                                council[key] = enriched[key]
                                updated_fields = True
                        if updated_fields:
                            self.stats['updated'] += 1
                        await asyncio.sleep(random.uniform(*REQUEST_DELAY))
                        return council
                    elif external_source_used == 'google_places':
                        logger.debug(f"  Google Places returned source but no data found - will try web scraping")
                
                # Check if we got new data (for non-Google Places sources)
                if (enriched.get('asc_phone') and not council.get('asc_phone')) or \
                   (enriched.get('asc_email') and not council.get('asc_email')) or \
                   (enriched.get('asc_website_url') and not council.get('asc_website_url')):
                    logger.info(f"  ✓ Found data from external sources")
                    # Preserve source information BEFORE updating
                    if enriched.get('source'):
                        external_source_used = enriched['source']
                        council['source'] = enriched['source']
                    council['last_updated'] = datetime.now().isoformat()
                    council.update(enriched)
                    self.stats['updated'] += 1
            except Exception as e:
                logger.debug(f"  External sources error: {e}")
        
        # Step 2: Try to find and scrape website (only if we didn't get data from Google Places)
        website = council.get('asc_website_url')
        if not website:
            website = self.find_council_website(council_name)
        
        if website:
            logger.info(f"  Found website: {website}")
            scraped_data = await self.scrape_council_page(website)
            
            # Get source from scraped_data, default to 'web_scraping'
            source = scraped_data.get('source', 'web_scraping')
            
            # Update council data
            updated = False
            for key, value in scraped_data.items():
                # Skip internal fields
                if key in ['firecrawl_used', 'text', 'html', 'soup', 'source']:
                    continue
                if value and not council.get(key):
                    council[key] = value
                    updated = True
            
            if updated:
                # Set source and last_updated
                # Priority: external sources (google_places) > firecrawl > web_scraping
                # Don't overwrite external source if it was already set
                if external_source_used and external_source_used != 'google_places':
                    council['source'] = external_source_used
                elif scraped_data.get('source') and not council.get('source'):
                    council['source'] = scraped_data['source']
                elif not council.get('source'):
                    council['source'] = 'web_scraping'
                council['last_updated'] = datetime.now().isoformat()
                logger.info(f"  ✓ Updated with new data (source: {council.get('source', 'unknown')})")
                self.stats['updated'] += 1
            else:
                logger.info(f"  - No new data found")
        else:
            logger.warning(f"  ✗ Could not find website")
            self.stats['failed'] += 1
        
        # Rate limiting
        await asyncio.sleep(random.uniform(*REQUEST_DELAY))
        
        return council
    
    def collect_all(self, limit: Optional[int] = None):
        """Collect data for all councils"""
        self.data = self.load_data()
        
        if not self.data:
            logger.error("Failed to load data")
            return
        
        councils = self.data.get('councils', [])
        self.stats['total'] = len(councils)
        
        # Filter councils that need collection
        councils_to_process = [
            c for c in councils
            if not (c.get('asc_phone') and c.get('asc_email'))
        ]
        
        if limit:
            councils_to_process = councils_to_process[:limit]
        
        logger.info(f"Processing {len(councils_to_process)} councils...")
        
        # Create backup
        self.save_backup()
        
        # Process each council (async)
        async def process_councils():
            for i, council in enumerate(councils_to_process, 1):
                try:
                    logger.info(f"\n[{i}/{len(councils_to_process)}] Processing...")
                    await self.collect_for_council(council)
                    self.stats['processed'] += 1
                    
                    # Save progress every 10 councils
                    if i % 10 == 0:
                        logger.info("Saving progress...")
                        self.save_data()
                except KeyboardInterrupt:
                    logger.info("\nInterrupted by user. Saving progress...")
                    self.save_data()
                    break
                except Exception as e:
                    logger.error(f"Error processing {council.get('council_name')}: {e}")
                    self.stats['failed'] += 1
        
        # Run async processing
        asyncio.run(process_councils())
        
        # Final save
        self.save_data()
        
        # Print statistics
        logger.info("\n" + "="*60)
        logger.info("Collection Statistics:")
        logger.info(f"  Total councils: {self.stats['total']}")
        logger.info(f"  Processed: {self.stats['processed']}")
        logger.info(f"  Updated: {self.stats['updated']}")
        logger.info(f"  Skipped (already complete): {self.stats['skipped']}")
        logger.info(f"  Failed: {self.stats['failed']}")
        if self.stats.get('firecrawl_used', 0) > 0:
            logger.info(f"  🔥 Firecrawl used: {self.stats['firecrawl_used']}")
            if self.stats.get('firecrawl_failed', 0) > 0:
                logger.info(f"  ⚠️ Firecrawl failed: {self.stats['firecrawl_failed']}")
        logger.info("="*60)


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Collect LA contact information')
    parser.add_argument('--limit', type=int, help='Limit number of councils to process')
    parser.add_argument('--council', type=str, help='Process specific council by name')
    
    args = parser.parse_args()
    
    collector = LAContactsCollector()
    
    if args.council:
        # Process single council
        data = collector.load_data()
        councils = data.get('councils', [])
        council = next((c for c in councils if args.council.lower() in c.get('council_name', '').lower()), None)
        
        if council:
            collector.data = data
            collector.save_backup()
            # Use asyncio.run for async function
            asyncio.run(collector.collect_for_council(council))
            collector.save_data()
        else:
            logger.error(f"Council not found: {args.council}")
    else:
        # Process all councils
        collector.collect_all(limit=args.limit)


if __name__ == '__main__':
    main()

