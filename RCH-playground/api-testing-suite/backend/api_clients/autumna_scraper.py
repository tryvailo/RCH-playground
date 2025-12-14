"""
Autumna Web Scraper
"""
import httpx
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import asyncio
import random


class AutumnaScraper:
    """Autumna Web Scraper"""
    
    def __init__(self, proxy: Optional[str] = None):
        self.base_url = "https://www.autumna.care"
        self.proxy = proxy
        
        proxies = None
        if proxy:
            proxies = {
                "http://": proxy,
                "https://": proxy
            }
        
        self.client = httpx.AsyncClient(
            timeout=30.0,
            proxies=proxies,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        )
    
    async def search_care_homes(
        self,
        location: str,
        page: int = 1
    ) -> List[Dict]:
        """Search care homes by location"""
        # Note: This is a placeholder implementation
        # Actual selectors need to be adapted based on Autumna's current HTML structure
        
        search_url = f"{self.base_url}/care-homes"
        params = {
            "location": location,
            "page": page
        }
        
        try:
            response = await self.client.get(search_url, params=params)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, "html.parser")
            homes = []
            
            # Placeholder: Adapt selectors based on actual site structure
            # Example selectors (need to be verified):
            home_cards = soup.find_all("div", class_="care-home-card") or \
                        soup.find_all("article", class_="care-home") or \
                        soup.find_all("div", {"data-testid": "care-home-card"})
            
            for card in home_cards[:10]:  # Limit to 10 for testing
                try:
                    name_elem = card.find("h3") or card.find("h2") or card.find("a", class_="home-name")
                    name = name_elem.text.strip() if name_elem else "Unknown"
                    
                    link_elem = card.find("a")
                    url = self.base_url + link_elem["href"] if link_elem and link_elem.get("href") else None
                    
                    price_elem = card.find("span", class_="price") or card.find("div", class_="price")
                    price = self._extract_price(price_elem.text if price_elem else "")
                    
                    homes.append({
                        "name": name,
                        "url": url,
                        "price_from": price,
                        "location": location
                    })
                except Exception as e:
                    continue
            
            # Rate limiting
            await asyncio.sleep(random.uniform(2, 4))
            
            return homes
        except Exception as e:
            # If scraping fails, return empty list
            return []
    
    def _extract_price(self, text: str) -> Optional[int]:
        """Extract price as integer from text"""
        import re
        match = re.search(r"£([\d,]+)", text)
        if match:
            return int(match.group(1).replace(",", ""))
        return None
    
    async def get_home_details(self, home_url: str) -> Dict:
        """Get detailed information about a specific home"""
        try:
            response = await self.client.get(home_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, "html.parser")
            
            details = {
                "name": None,
                "description": None,
                "amenities": [],
                "photos": [],
                "room_types": [],
                "contact": {}
            }
            
            # Extract name
            name_elem = soup.find("h1")
            if name_elem:
                details["name"] = name_elem.text.strip()
            
            # Extract description
            desc_elem = soup.find("div", class_="description") or soup.find("p", class_="description")
            if desc_elem:
                details["description"] = desc_elem.text.strip()
            
            # Extract amenities (adapt selectors)
            amenities_section = soup.find("section", id="amenities") or \
                              soup.find("div", class_="amenities")
            if amenities_section:
                amenity_items = amenities_section.find_all("li") or \
                              amenities_section.find_all("span", class_="amenity")
                details["amenities"] = [item.text.strip() for item in amenity_items]
            
            # Extract photos
            photo_gallery = soup.find("div", class_="gallery") or \
                          soup.find("div", class_="photo-gallery")
            if photo_gallery:
                images = photo_gallery.find_all("img")
                details["photos"] = [img.get("src", "") for img in images if img.get("src")]
            
            # Rate limiting
            await asyncio.sleep(random.uniform(3, 5))
            
            return details
        except Exception as e:
            return {
                "error": str(e),
                "name": None,
                "amenities": [],
                "photos": []
            }
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

