# RightCareHome: Примеры Кода для API Тестирования
**Версия:** 1.0  
**Язык:** Python 3.9+  
**Dependencies**: requests, beautifulsoup4, pandas, google-cloud-bigquery

---

## 📦 SETUP И УСТАНОВКА

### 1. Установка Dependencies
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows

# Install packages
pip install requests beautifulsoup4 pandas google-cloud-bigquery \
    google-auth google-auth-oauthlib google-auth-httplib2 \
    python-dotenv textblob scrapy
```

### 2. Environment Variables (.env file)
```bash
# CQC API
CQC_PARTNER_CODE=RIGHTCAREHOME

# Companies House
COMPANIES_HOUSE_API_KEY=your_api_key_here

# Google APIs
GOOGLE_PLACES_API_KEY=your_google_api_key
GOOGLE_CLOUD_PROJECT=your-gcp-project-id

# Perplexity
PERPLEXITY_API_KEY=your_perplexity_key

# Database (optional for testing)
DATABASE_URL=postgresql://user:pass@localhost/rightcarehome

# Proxies (для Autumna scraping)
PROXY_URL=http://user:pass@proxy-server:port
```

---

## 🏛️ CQC API - Примеры

### Базовый класс для CQC API
```python
import requests
from typing import List, Dict, Optional
import os
from dotenv import load_dotenv

load_dotenv()

class CQCAPIClient:
    def __init__(self):
        self.base_url = "https://api.cqc.org.uk/public/v1"
        self.partner_code = os.getenv("CQC_PARTNER_CODE")
        self.session = requests.Session()
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """Make API request with partner code"""
        if params is None:
            params = {}
        params['partnerCode'] = self.partner_code
        
        url = f"{self.base_url}/{endpoint}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    def search_care_homes(self, region: str = "South East", 
                          per_page: int = 100, page: int = 1) -> List[Dict]:
        """Search for care homes in a region"""
        params = {
            'region': region,
            'careHome': 'true',
            'perPage': per_page,
            'page': page
        }
        
        data = self._make_request('locations', params)
        return data.get('locations', [])
    
    def get_location_details(self, location_id: str) -> Dict:
        """Get detailed info for a specific location"""
        return self._make_request(f'locations/{location_id}')
    
    def get_location_reports(self, location_id: str) -> List[Dict]:
        """Get inspection reports for a location"""
        data = self._make_request(f'locations/{location_id}/reports')
        return data.get('reports', [])
    
    def get_provider_locations(self, provider_id: str) -> List[Dict]:
        """Get all locations for a provider"""
        data = self._make_request(f'providers/{provider_id}/locations')
        return data.get('locations', [])
    
    def get_changes(self, start_date: str, end_date: str = None) -> List[Dict]:
        """Get changes since start_date (YYYY-MM-DD format)"""
        params = {'startDate': start_date}
        if end_date:
            params['endDate'] = end_date
        
        data = self._make_request('changes', params)
        return data.get('changes', [])


# USAGE EXAMPLE
if __name__ == "__main__":
    client = CQCAPIClient()
    
    # Search care homes in South East
    homes = client.search_care_homes(region="South East", per_page=10)
    print(f"Found {len(homes)} care homes")
    
    # Get details for first home
    if homes:
        first_home = homes[0]
        location_id = first_home['locationId']
        details = client.get_location_details(location_id)
        
        print(f"\nHome: {details['name']}")
        print(f"Rating: {details['currentRatings']['overall']['rating']}")
        print(f"Specialisms: {', '.join(details.get('specialisms', []))}")
```

---

## 🍽️ FSA FHRS API - Примеры

### FSA API Client
```python
import requests
from typing import List, Dict, Optional

class FSAAPIClient:
    def __init__(self):
        self.base_url = "http://api.ratings.food.gov.uk"
        self.headers = {
            'x-api-version': '2',
            'Accept-Language': 'en-GB'
        }
    
    def search_by_business_name(self, name: str, 
                                local_authority_id: Optional[int] = None) -> List[Dict]:
        """Search establishments by name"""
        url = f"{self.base_url}/Establishments"
        params = {'name': name}
        
        if local_authority_id:
            params['localAuthorityId'] = local_authority_id
        
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        
        data = response.json()
        return data.get('establishments', [])
    
    def search_by_location(self, latitude: float, longitude: float, 
                          max_distance: float = 1.0) -> List[Dict]:
        """Search by geolocation (max_distance in miles)"""
        url = f"{self.base_url}/Establishments"
        params = {
            'latitude': latitude,
            'longitude': longitude,
            'maxDistanceLimit': max_distance
        }
        
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        
        data = response.json()
        return data.get('establishments', [])
    
    def get_establishment_details(self, fhrs_id: int) -> Dict:
        """Get details for specific establishment"""
        url = f"{self.base_url}/Establishments/{fhrs_id}"
        
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        
        return response.json()
    
    def get_local_authorities(self) -> List[Dict]:
        """Get list of all local authorities"""
        url = f"{self.base_url}/Authorities"
        
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        
        data = response.json()
        return data.get('authorities', [])
    
    def match_with_cqc_location(self, cqc_location: Dict) -> Optional[Dict]:
        """
        Match CQC location with FSA establishment
        Uses name and coordinates
        """
        name = cqc_location['name']
        lat = cqc_location.get('latitude')
        lon = cqc_location.get('longitude')
        
        if not (lat and lon):
            # Fallback to name search
            results = self.search_by_business_name(name)
        else:
            # Use geolocation for better accuracy
            results = self.search_by_location(lat, lon, max_distance=0.5)
        
        # Find best match by name similarity
        if results:
            from difflib import SequenceMatcher
            
            best_match = None
            best_score = 0
            
            for est in results:
                score = SequenceMatcher(None, 
                                       name.lower(), 
                                       est['BusinessName'].lower()).ratio()
                if score > best_score and score > 0.7:  # 70% similarity threshold
                    best_score = score
                    best_match = est
            
            return best_match
        
        return None


# USAGE EXAMPLE
if __name__ == "__main__":
    fsa_client = FSAAPIClient()
    
    # Search near specific coordinates (Brighton example)
    results = fsa_client.search_by_location(50.8225, -0.1372, max_distance=2)
    
    print(f"Found {len(results)} establishments")
    
    for est in results[:5]:  # First 5
        print(f"\n{est['BusinessName']}")
        print(f"Rating: {est['RatingValue']}")
        print(f"Address: {est['AddressLine1']}, {est['PostCode']}")
        
        if est.get('RatingValue') in ['0', '1', '2']:
            print("⚠️ LOW RATING - CONCERN!")
```

---

## 🏢 Companies House API - Примеры

### Companies House Client
```python
import requests
from typing import Dict, List, Optional
import os
from requests.auth import HTTPBasicAuth

class CompaniesHouseAPIClient:
    def __init__(self):
        self.base_url = "https://api.company-information.service.gov.uk"
        self.api_key = os.getenv("COMPANIES_HOUSE_API_KEY")
        self.auth = HTTPBasicAuth(self.api_key, '')
    
    def search_companies(self, query: str, items_per_page: int = 20) -> List[Dict]:
        """Search for companies by name"""
        url = f"{self.base_url}/search/companies"
        params = {
            'q': query,
            'items_per_page': items_per_page
        }
        
        response = requests.get(url, params=params, auth=self.auth)
        response.raise_for_status()
        
        data = response.json()
        return data.get('items', [])
    
    def get_company_profile(self, company_number: str) -> Dict:
        """Get company profile"""
        url = f"{self.base_url}/company/{company_number}"
        
        response = requests.get(url, auth=self.auth)
        response.raise_for_status()
        
        return response.json()
    
    def get_company_officers(self, company_number: str) -> List[Dict]:
        """Get list of directors/officers"""
        url = f"{self.base_url}/company/{company_number}/officers"
        
        response = requests.get(url, auth=self.auth)
        response.raise_for_status()
        
        data = response.json()
        return data.get('items', [])
    
    def get_filing_history(self, company_number: str) -> List[Dict]:
        """Get filing history"""
        url = f"{self.base_url}/company/{company_number}/filing-history"
        
        response = requests.get(url, auth=self.auth)
        response.raise_for_status()
        
        data = response.json()
        return data.get('items', [])
    
    def get_charges(self, company_number: str) -> List[Dict]:
        """Get charges (mortgages, debts)"""
        url = f"{self.base_url}/company/{company_number}/charges"
        
        response = requests.get(url, auth=self.auth)
        response.raise_for_status()
        
        data = response.json()
        return data.get('items', [])
    
    def calculate_financial_stability_score(self, company_number: str) -> Dict:
        """Calculate financial stability score"""
        profile = self.get_company_profile(company_number)
        
        score = 100
        issues = []
        
        # Company status
        if profile['company_status'] != 'active':
            score -= 100
            issues.append(f"Company status: {profile['company_status']}")
        
        # Accounts overdue
        if profile.get('accounts', {}).get('overdue'):
            score -= 30
            issues.append("Accounts filing overdue")
        
        # Insolvency
        if profile.get('has_insolvency_history'):
            score -= 50
            issues.append("Has insolvency history")
        
        # Charges
        try:
            charges = self.get_charges(company_number)
            if len(charges) > 5:
                score -= 20
                issues.append(f"{len(charges)} charges registered")
        except:
            pass
        
        # Age of company
        from datetime import datetime
        creation_date = datetime.strptime(profile['date_of_creation'], '%Y-%m-%d')
        age_years = (datetime.now() - creation_date).days / 365
        
        if age_years < 3:
            score -= 15
            issues.append(f"Young company ({age_years:.1f} years)")
        
        return {
            'company_name': profile['company_name'],
            'company_number': company_number,
            'score': max(0, score),
            'risk_level': 'HIGH' if score < 50 else 'MEDIUM' if score < 70 else 'LOW',
            'issues': issues,
            'company_status': profile['company_status'],
            'age_years': age_years
        }


# USAGE EXAMPLE
if __name__ == "__main__":
    ch_client = CompaniesHouseAPIClient()
    
    # Search for a care home operator
    results = ch_client.search_companies("HC-One", items_per_page=5)
    
    if results:
        company = results[0]
        company_number = company['company_number']
        
        print(f"Company: {company['title']}")
        print(f"Number: {company_number}")
        print(f"Status: {company['company_status']}")
        
        # Get stability score
        stability = ch_client.calculate_financial_stability_score(company_number)
        
        print(f"\nFinancial Stability Score: {stability['score']}/100")
        print(f"Risk Level: {stability['risk_level']}")
        if stability['issues']:
            print("Issues:")
            for issue in stability['issues']:
                print(f"  - {issue}")
```

---

## 🗺️ Google Places API - Примеры

### Google Places Client
```python
import requests
from typing import Dict, List, Optional
import os

class GooglePlacesAPIClient:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_PLACES_API_KEY")
        self.base_url = "https://maps.googleapis.com/maps/api/place"
    
    def find_place(self, query: str, input_type: str = "textquery") -> Optional[Dict]:
        """Find place by name/query"""
        url = f"{self.base_url}/findplacefromtext/json"
        params = {
            'input': query,
            'inputtype': input_type,
            'fields': 'place_id,name,formatted_address,geometry',
            'key': self.api_key
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        candidates = data.get('candidates', [])
        
        return candidates[0] if candidates else None
    
    def get_place_details(self, place_id: str, 
                         fields: List[str] = None) -> Dict:
        """Get detailed information about a place"""
        if fields is None:
            fields = [
                'name', 'rating', 'user_ratings_total', 'reviews',
                'formatted_phone_number', 'website', 'opening_hours',
                'photos', 'formatted_address'
            ]
        
        url = f"{self.base_url}/details/json"
        params = {
            'place_id': place_id,
            'fields': ','.join(fields),
            'key': self.api_key
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        return data.get('result', {})
    
    def nearby_search(self, latitude: float, longitude: float,
                     radius: int = 5000, place_type: str = "nursing_home") -> List[Dict]:
        """Search for places nearby coordinates"""
        url = f"{self.base_url}/nearbysearch/json"
        params = {
            'location': f"{latitude},{longitude}",
            'radius': radius,
            'type': place_type,
            'keyword': 'care home',
            'key': self.api_key
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        return data.get('results', [])
    
    def get_photo(self, photo_reference: str, max_width: int = 400) -> bytes:
        """Download a place photo"""
        url = f"{self.base_url}/photo"
        params = {
            'photoreference': photo_reference,
            'maxwidth': max_width,
            'key': self.api_key
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        return response.content
    
    def analyze_reviews_sentiment(self, reviews: List[Dict]) -> Dict:
        """Analyze sentiment of reviews"""
        from textblob import TextBlob
        
        if not reviews:
            return {'error': 'No reviews to analyze'}
        
        sentiments = []
        positive_keywords = ['excellent', 'wonderful', 'caring', 'attentive', 'kind']
        negative_keywords = ['poor', 'terrible', 'neglect', 'dirty', 'rude']
        
        for review in reviews:
            text = review.get('text', '')
            blob = TextBlob(text)
            sentiment = blob.sentiment.polarity  # -1 to 1
            
            sentiments.append({
                'rating': review.get('rating'),
                'sentiment_score': sentiment,
                'text': text[:100],  # First 100 chars
                'has_positive_keywords': any(kw in text.lower() for kw in positive_keywords),
                'has_negative_keywords': any(kw in text.lower() for kw in negative_keywords)
            })
        
        avg_sentiment = sum(s['sentiment_score'] for s in sentiments) / len(sentiments)
        
        return {
            'average_sentiment': avg_sentiment,
            'sentiment_label': 'Positive' if avg_sentiment > 0.2 else 'Negative' if avg_sentiment < -0.2 else 'Neutral',
            'total_reviews': len(reviews),
            'reviews_analysis': sentiments
        }


# USAGE EXAMPLE
if __name__ == "__main__":
    gp_client = GooglePlacesAPIClient()
    
    # Find a care home
    place = gp_client.find_place("Manor House Care Home Brighton")
    
    if place:
        place_id = place['place_id']
        print(f"Found: {place['name']}")
        
        # Get detailed info
        details = gp_client.get_place_details(place_id)
        
        print(f"\nRating: {details.get('rating', 'N/A')}")
        print(f"Reviews: {details.get('user_ratings_total', 0)}")
        
        # Analyze reviews
        if 'reviews' in details:
            sentiment = gp_client.analyze_reviews_sentiment(details['reviews'])
            print(f"\nSentiment: {sentiment['sentiment_label']}")
            print(f"Score: {sentiment['average_sentiment']:.2f}")
```

---

## 🔍 Perplexity API - Примеры

### Perplexity Client
```python
import requests
from typing import Dict, List
import os

class PerplexityAPIClient:
    def __init__(self):
        self.api_key = os.getenv("PERPLEXITY_API_KEY")
        self.base_url = "https://api.perplexity.ai"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def search(self, query: str, model: str = "sonar-pro",
              max_tokens: int = 500, temperature: float = 0.2,
              search_recency_filter: str = "month") -> Dict:
        """Search with Perplexity API"""
        url = f"{self.base_url}/chat/completions"
        
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": query
                }
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "return_citations": True,
            "search_recency_filter": search_recency_filter
        }
        
        response = requests.post(url, json=payload, headers=self.headers)
        response.raise_for_status()
        
        return response.json()
    
    def monitor_care_home_reputation(self, home_name: str, 
                                    location: str = "") -> Dict:
        """Monitor reputation of a care home"""
        location_str = f"in {location}" if location else ""
        
        query = f"""Search for recent news, complaints, or concerns about 
        {home_name} {location_str} in the last 3 months. 
        
        Summarize:
        1. Any positive news (awards, improvements)
        2. Any negative news (complaints, issues, inspections)
        3. Overall reputation status
        
        Provide source links."""
        
        return self.search(query, search_recency_filter="month")
    
    def competitive_intelligence(self, region: str) -> Dict:
        """Get competitive intelligence for a region"""
        query = f"""Find information about new care homes that opened 
        in {region} England in the last 12 months.
        
        Include:
        - Name and location
        - Operator company
        - Any unique features
        
        Provide sources."""
        
        return self.search(query, search_recency_filter="year", max_tokens=800)
    
    def crisis_monitoring(self) -> Dict:
        """Monitor for crises in UK care homes"""
        query = """Search for recent COVID-19, norovirus, or other 
        infection outbreaks reported in UK care homes in the last month.
        
        List affected homes and severity.
        Provide news sources."""
        
        return self.search(query, search_recency_filter="week")
    
    def financial_distress_scan(self) -> Dict:
        """Scan for financially distressed operators"""
        query = """Search for news about care home companies in financial 
        difficulty, administration, or bankruptcy in UK in last 6 months.
        
        Include company names and affected homes."""
        
        return self.search(query, search_recency_filter="month")
    
    def extract_events(self, response: Dict) -> List[Dict]:
        """Extract structured events from narrative response"""
        import re
        
        content = response['choices'][0]['message']['content']
        citations = response.get('citations', [])
        
        events = []
        sentences = content.split('. ')
        
        event_patterns = {
            'award': r'(award|prize|accolade|recognition)',
            'complaint': r'(complaint|concern|allegation|issue)',
            'inspection': r'(inspection|visit|report|rating)',
            'ownership': r'(acquired|purchased|taken over|sold)',
            'outbreak': r'(outbreak|infection|covid|norovirus)'
        }
        
        for sentence in sentences:
            for event_type, pattern in event_patterns.items():
                if re.search(pattern, sentence, re.IGNORECASE):
                    events.append({
                        'type': event_type,
                        'description': sentence.strip(),
                        'sentiment': 'negative' if event_type in ['complaint', 'outbreak'] 
                                   else 'positive' if event_type == 'award' 
                                   else 'neutral'
                    })
        
        return events


# USAGE EXAMPLE
if __name__ == "__main__":
    pplx_client = PerplexityAPIClient()
    
    # Monitor a specific care home
    result = pplx_client.monitor_care_home_reputation(
        "Manor House Care",
        "Brighton"
    )
    
    print("PERPLEXITY RESPONSE:")
    print(result['choices'][0]['message']['content'])
    
    print("\n\nCITATIONS:")
    for citation in result.get('citations', []):
        print(f"- {citation}")
    
    # Extract events
    events = pplx_client.extract_events(result)
    print(f"\n\nEXTRACTED EVENTS: {len(events)}")
    for event in events:
        print(f"  [{event['type']}] {event['description'][:80]}...")
```

---

## 🌐 Autumna Web Scraping - Примеры

### Autumna Scraper
```python
import requests
from bs4 import BeautifulSoup
import time
import random
from typing import List, Dict

class AutumnaScraper:
    def __init__(self, proxy: str = None):
        self.base_url = "https://www.autumna.care"
        self.session = requests.Session()
        
        if proxy:
            self.session.proxies = {
                "http": proxy,
                "https": proxy
            }
        
        # Rotate user agents
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        ]
        
        self.session.headers.update({
            'User-Agent': random.choice(self.user_agents)
        })
    
    def search_care_homes(self, location: str, page: int = 1) -> List[Dict]:
        """
        Search care homes by location
        NOTE: Selectors need to be updated based on actual site structure
        """
        search_url = f"{self.base_url}/care-homes"
        params = {
            'location': location,
            'page': page
        }
        
        response = self.session.get(search_url, params=params)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        homes = []
        
        # ADAPT SELECTORS BASED ON ACTUAL SITE
        home_cards = soup.find_all('div', class_='care-home-card')
        
        for card in home_cards:
            try:
                home = {
                    'name': card.find('h3').text.strip(),
                    'url': self.base_url + card.find('a')['href'],
                    'location': card.find('span', class_='location').text.strip(),
                    'price_from': self._extract_price(card),
                    'specialisms': [s.text.strip() for s in card.find_all('span', class_='tag')]
                }
                homes.append(home)
            except Exception as e:
                print(f"Error parsing card: {e}")
                continue
        
        # Rate limiting - CRITICAL
        time.sleep(random.uniform(2, 4))
        
        return homes
    
    def _extract_price(self, element) -> int:
        """Extract price as integer from text"""
        import re
        
        price_elem = element.find('span', class_='price')
        if price_elem:
            text = price_elem.text
            match = re.search(r'£([\d,]+)', text)
            if match:
                return int(match.group(1).replace(',', ''))
        return None
    
    def get_home_details(self, home_url: str) -> Dict:
        """
        Get detailed information about a specific home
        """
        response = self.session.get(home_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        details = {
            'name': None,
            'description': None,
            'amenities': [],
            'photos': [],
            'room_types': [],
            'contact': {}
        }
        
        try:
            # Name
            details['name'] = soup.find('h1').text.strip()
            
            # Description
            desc_elem = soup.find('div', class_='description')
            if desc_elem:
                details['description'] = desc_elem.text.strip()
            
            # Amenities
            amenities_section = soup.find('section', id='amenities')
            if amenities_section:
                details['amenities'] = [
                    li.text.strip() 
                    for li in amenities_section.find_all('li')
                ]
            
            # Photos
            photo_gallery = soup.find('div', class_='gallery')
            if photo_gallery:
                details['photos'] = [
                    img['src'] for img in photo_gallery.find_all('img')
                ]
            
            # Contact
            phone = soup.find('a', href=lambda h: h and h.startswith('tel:'))
            if phone:
                details['contact']['phone'] = phone.text.strip()
            
            email = soup.find('a', href=lambda h: h and h.startswith('mailto:'))
            if email:
                details['contact']['email'] = email.text.strip()
        
        except Exception as e:
            print(f"Error parsing home details: {e}")
        
        # Longer wait for detail pages
        time.sleep(random.uniform(3, 5))
        
        return details
    
    def classify_amenities(self, amenities: List[str]) -> Dict[str, List[str]]:
        """Classify amenities into categories"""
        categories = {
            'outdoor': ['garden', 'terrace', 'patio', 'outdoor'],
            'accessibility': ['wheelchair', 'lift', 'ramp', 'ground floor'],
            'social': ['activities', 'cinema', 'library', 'lounge'],
            'tech': ['wifi', 'internet', 'tv', 'call system'],
            'food': ['dining', 'cafe', 'restaurant', 'kitchen'],
            'wellness': ['hairdresser', 'spa', 'fitness', 'therapy']
        }
        
        classified = {cat: [] for cat in categories}
        
        for amenity in amenities:
            amenity_lower = amenity.lower()
            for category, keywords in categories.items():
                if any(kw in amenity_lower for kw in keywords):
                    classified[category].append(amenity)
        
        return classified


# USAGE EXAMPLE
if __name__ == "__main__":
    # Initialize scraper (with proxy if needed)
    scraper = AutumnaScraper(proxy=os.getenv("PROXY_URL"))
    
    # Search homes
    homes = scraper.search_care_homes("Brighton", page=1)
    
    print(f"Found {len(homes)} care homes")
    
    if homes:
        # Get details for first home
        first_home = homes[0]
        print(f"\nScraping details for: {first_home['name']}")
        
        details = scraper.get_home_details(first_home['url'])
        
        print(f"Amenities: {len(details['amenities'])}")
        print(f"Photos: {len(details['photos'])}")
        
        # Classify amenities
        classified = scraper.classify_amenities(details['amenities'])
        
        print("\nAmenities by category:")
        for category, items in classified.items():
            if items:
                print(f"  {category}: {', '.join(items)}")
```

---

## 🔗 ИНТЕГРАЦИЯ: Comprehensive Profile Builder

### Multi-Source Data Fusion
```python
from dataclasses import dataclass
from typing import Optional
import json

@dataclass
class CareHomeProfile:
    # Basic Info
    name: str
    location_id: str
    address: str
    
    # Quality Data
    cqc_rating: str
    fsa_rating: Optional[int]
    
    # Financial
    operator_company: str
    financial_stability_score: int
    
    # Reputation
    google_rating: Optional[float]
    review_count: int
    
    # Behavioral (Places Insights)
    weekly_visitors: Optional[int]
    dwell_time: Optional[float]
    engagement_score: Optional[int]
    
    # Risk Assessment
    overall_risk_level: str
    risk_score: int


class DataIntegrator:
    def __init__(self):
        self.cqc_client = CQCAPIClient()
        self.fsa_client = FSAAPIClient()
        self.ch_client = CompaniesHouseAPIClient()
        self.gp_client = GooglePlacesAPIClient()
        self.pplx_client = PerplexityAPIClient()
    
    def build_comprehensive_profile(self, home_name: str, 
                                   location: str) -> CareHomeProfile:
        """
        Build complete profile from all data sources
        """
        print(f"Building profile for: {home_name}")
        
        # 1. CQC Data (foundation)
        print("  Fetching CQC data...")
        cqc_homes = self.cqc_client.search_care_homes()
        cqc_match = self._find_match(cqc_homes, home_name)
        
        if not cqc_match:
            raise ValueError(f"Home not found in CQC: {home_name}")
        
        cqc_details = self.cqc_client.get_location_details(cqc_match['locationId'])
        
        # 2. FSA Data
        print("  Matching with FSA...")
        fsa_match = self.fsa_client.match_with_cqc_location(cqc_details)
        fsa_rating = fsa_match['RatingValue'] if fsa_match else None
        
        # 3. Companies House
        print("  Checking financial stability...")
        provider_name = cqc_details['provider']['name']
        ch_companies = self.ch_client.search_companies(provider_name)
        
        financial_stability = 50  # Default
        if ch_companies:
            company_number = ch_companies[0]['company_number']
            stability_data = self.ch_client.calculate_financial_stability_score(
                company_number
            )
            financial_stability = stability_data['score']
        
        # 4. Google Places
        print("  Fetching Google reviews...")
        google_place = self.gp_client.find_place(f"{home_name} {location}")
        
        google_rating = None
        review_count = 0
        
        if google_place:
            google_details = self.gp_client.get_place_details(
                google_place['place_id']
            )
            google_rating = google_details.get('rating')
            review_count = google_details.get('user_ratings_total', 0)
        
        # 5. Calculate Risk
        risk_assessment = self._calculate_risk(
            cqc_rating=cqc_details['currentRatings']['overall']['rating'],
            fsa_rating=fsa_rating,
            financial_stability=financial_stability,
            google_rating=google_rating
        )
        
        # Build profile
        profile = CareHomeProfile(
            name=cqc_details['name'],
            location_id=cqc_details['locationId'],
            address=cqc_details['postalAddress'],
            cqc_rating=cqc_details['currentRatings']['overall']['rating'],
            fsa_rating=fsa_rating,
            operator_company=provider_name,
            financial_stability_score=financial_stability,
            google_rating=google_rating,
            review_count=review_count,
            weekly_visitors=None,  # Would come from Places Insights
            dwell_time=None,
            engagement_score=None,
            overall_risk_level=risk_assessment['level'],
            risk_score=risk_assessment['score']
        )
        
        return profile
    
    def _find_match(self, homes: List[Dict], name: str) -> Optional[Dict]:
        """Find best matching home by name"""
        from difflib import SequenceMatcher
        
        best_match = None
        best_score = 0
        
        for home in homes:
            score = SequenceMatcher(None, 
                                   name.lower(), 
                                   home['name'].lower()).ratio()
            if score > best_score:
                best_score = score
                best_match = home
        
        return best_match if best_score > 0.7 else None
    
    def _calculate_risk(self, cqc_rating: str, fsa_rating: Optional[int],
                       financial_stability: int, 
                       google_rating: Optional[float]) -> Dict:
        """Calculate overall risk assessment"""
        risk_score = 0
        
        # CQC
        cqc_risk = {
            'Outstanding': 0,
            'Good': 10,
            'Requires Improvement': 40,
            'Inadequate': 80
        }
        risk_score += cqc_risk.get(cqc_rating, 30)
        
        # FSA
        if fsa_rating and fsa_rating < 4:
            risk_score += 20
        
        # Financial
        if financial_stability < 50:
            risk_score += 30
        elif financial_stability < 70:
            risk_score += 15
        
        # Google rating
        if google_rating and google_rating < 3.5:
            risk_score += 20
        
        level = 'HIGH' if risk_score > 70 else 'MEDIUM' if risk_score > 40 else 'LOW'
        
        return {
            'score': min(100, risk_score),
            'level': level
        }


# USAGE EXAMPLE
if __name__ == "__main__":
    integrator = DataIntegrator()
    
    # Build comprehensive profile
    profile = integrator.build_comprehensive_profile(
        "Manor House Care Home",
        "Brighton"
    )
    
    print("\n" + "="*60)
    print("COMPREHENSIVE CARE HOME PROFILE")
    print("="*60)
    print(f"\nHome: {profile.name}")
    print(f"Location ID: {profile.location_id}")
    print(f"\nQUALITY:")
    print(f"  CQC Rating: {profile.cqc_rating}")
    print(f"  FSA Rating: {profile.fsa_rating}/5")
    print(f"\nFINANCIAL:")
    print(f"  Operator: {profile.operator_company}")
    print(f"  Stability Score: {profile.financial_stability_score}/100")
    print(f"\nREPUTATION:")
    print(f"  Google Rating: {profile.google_rating}/5")
    print(f"  Reviews: {profile.review_count}")
    print(f"\nRISK ASSESSMENT:")
    print(f"  Level: {profile.overall_risk_level}")
    print(f"  Score: {profile.risk_score}/100")
    
    # Export to JSON
    profile_dict = {
        'name': profile.name,
        'cqc_rating': profile.cqc_rating,
        'fsa_rating': profile.fsa_rating,
        'financial_stability': profile.financial_stability_score,
        'google_rating': profile.google_rating,
        'risk_level': profile.overall_risk_level,
        'risk_score': profile.risk_score
    }
    
    with open(f"profile_{profile.location_id}.json", 'w') as f:
        json.dump(profile_dict, f, indent=2)
    
    print(f"\n✓ Profile saved to profile_{profile.location_id}.json")
```

---

## 🚀 Quick Start Script

### Complete Testing Script
```bash
#!/bin/bash
# quick_start.sh - Run all API tests

echo "🏛️  RightCareHome API Testing"
echo "================================"

# Check environment variables
if [ -z "$CQC_PARTNER_CODE" ]; then
    echo "❌ Error: CQC_PARTNER_CODE not set"
    echo "Please create .env file with required API keys"
    exit 1
fi

echo "✓ Environment variables loaded"

# Run tests
echo ""
echo "1️⃣  Testing CQC API..."
python -c "
from api_clients import CQCAPIClient
client = CQCAPIClient()
homes = client.search_care_homes(per_page=5)
print(f'✓ Found {len(homes)} homes')
"

echo ""
echo "2️⃣  Testing FSA API..."
python -c "
from api_clients import FSAAPIClient
client = FSAAPIClient()
results = client.search_by_location(50.8225, -0.1372, max_distance=1)
print(f'✓ Found {len(results)} establishments')
"

echo ""
echo "3️⃣  Testing Companies House API..."
python -c "
from api_clients import CompaniesHouseAPIClient
client = CompaniesHouseAPIClient()
results = client.search_companies('HC-One', items_per_page=1)
if results:
    print(f\"✓ Found: {results[0]['title']}\")
"

echo ""
echo "4️⃣  Testing Google Places API..."
python -c "
from api_clients import GooglePlacesAPIClient
client = GooglePlacesAPIClient()
place = client.find_place('Care Home Brighton')
if place:
    print(f\"✓ Found: {place['name']}\")
"

echo ""
echo "================================"
echo "✅ All tests completed!"
echo "Next steps:"
echo "  1. Review test outputs"
echo "  2. Check API costs in respective dashboards"
echo "  3. Proceed with Week 1 Roadmap"
```

---

**📝 NOTE**: Эти примеры предоставляют базовую структуру. Вам нужно будет:
1. Адаптировать CSS селекторы для Autumna под актуальную структуру сайта
2. Добавить error handling и retry logic для production
3. Implement rate limiting и caching
4. Добавить logging для debugging

**Следующие шаги**: 
1. Сохраните код в отдельные модули (cqc_client.py, fsa_client.py, etc.)
2. Создайте .env file с API keys
3. Запустите quick_start.sh для начального тестирования
