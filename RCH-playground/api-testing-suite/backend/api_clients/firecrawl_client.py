"""
Firecrawl API Client
Integrates with Firecrawl.dev for website scraping and data extraction
4-Phase Universal Semantic Scraping Approach
"""
import httpx
import re
import json
import asyncio
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from collections import defaultdict, Counter


class FirecrawlAPIClient:
    """Firecrawl API Client for website scraping - Uses API v2 with 4-Phase Universal Approach"""
    
    def __init__(self, api_key: str, anthropic_api_key: Optional[str] = None):
        self.api_key = api_key
        self.anthropic_api_key = anthropic_api_key
        self.base_url = "https://api.firecrawl.dev/v2"
        self.client = httpx.AsyncClient(
            timeout=60.0,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
        )
        # Инициализация Anthropic клиента если API key предоставлен
        self.anthropic_client = None
        if anthropic_api_key:
            try:
                from anthropic import AsyncAnthropic
                self.anthropic_client = AsyncAnthropic(api_key=anthropic_api_key)
                print("✅ Anthropic Claude client initialized")
            except ImportError:
                print("⚠️ Anthropic library not installed. Install with: pip install anthropic")
            except Exception as e:
                print(f"⚠️ Failed to initialize Anthropic client: {e}")
    
    async def map_website(
        self,
        url: str,
        limit: int = 100,
        include_subdomains: bool = False
    ) -> Dict[str, Any]:
        """Map all URLs on a website using Firecrawl API v2"""
        try:
            response = await self.client.post(
                f"{self.base_url}/map",
                json={
                    "url": url,
                    "limit": limit,
                    "includeSubdomains": include_subdomains
                }
            )
            response.raise_for_status()
            result = response.json()
            # API v2 returns data in response.data
            if result.get("success") and "data" in result:
                return result["data"]
            return result
        except httpx.HTTPStatusError as e:
            error_detail = ""
            try:
                error_body = e.response.json()
                error_msg = error_body.get('error') or error_body.get('message', str(e))
                error_detail = f" - {error_msg}"
            except:
                error_detail = f" - {e.response.text[:200]}"
            raise Exception(f"Firecrawl API error: {e.response.status_code}{error_detail}")
        except Exception as e:
            raise Exception(f"Firecrawl API error: {str(e)}")
    
    async def crawl_website(
        self,
        url: str,
        limit: int = 50,
        include_paths: Optional[List[str]] = None,
        exclude_paths: Optional[List[str]] = None,
        formats: Optional[List[Any]] = None
    ) -> Dict[str, Any]:
        """Crawl and scrape website pages using Firecrawl API v2"""
        payload = {
            "url": url,
            "limit": limit
        }
        
        if include_paths:
            payload["includePaths"] = include_paths
        if exclude_paths:
            payload["excludePaths"] = exclude_paths
        
        # Default formats for API v2
        if formats is None:
            formats = [
                {"type": "markdown"},
                {"type": "html"}
            ]
        else:
            # Convert string formats to format objects if needed
            formatted_formats = []
            for fmt in formats:
                if isinstance(fmt, str):
                    formatted_formats.append({"type": fmt})
                else:
                    formatted_formats.append(fmt)
            formats = formatted_formats
        
        payload["formats"] = formats
        
        try:
            response = await self.client.post(
                f"{self.base_url}/crawl",
                json=payload
            )
            response.raise_for_status()
            result = response.json()
            # API v2 returns data in response.data
            if result.get("success") and "data" in result:
                return result["data"]
            return result
        except httpx.HTTPStatusError as e:
            error_detail = ""
            try:
                error_body = e.response.json()
                error_msg = error_body.get('error') or error_body.get('message', str(e))
                error_detail = f" - {error_msg}"
            except:
                error_detail = f" - {e.response.text[:200]}"
            raise Exception(f"Firecrawl API error: {e.response.status_code}{error_detail}")
        except Exception as e:
            raise Exception(f"Firecrawl API error: {str(e)}")
    
    async def scrape_url(
        self,
        url: str,
        formats: Optional[List[Any]] = None,
        only_main_content: bool = True
    ) -> Dict[str, Any]:
        """Scrape a single URL using Firecrawl API v2"""
        # Default formats - API v2 expects array of format objects or strings
        if formats is None:
            formats = [
                {"type": "markdown"},
                {"type": "html"}
            ]
        else:
            # Convert string formats to format objects if needed
            formatted_formats = []
            for fmt in formats:
                if isinstance(fmt, str):
                    formatted_formats.append({"type": fmt})
                else:
                    formatted_formats.append(fmt)
            formats = formatted_formats
        
        payload = {
            "url": url,
            "formats": formats,
            "onlyMainContent": only_main_content
        }
        
        try:
            response = await self.client.post(
                f"{self.base_url}/scrape",
                json=payload
            )
            response.raise_for_status()
            result = response.json()
            # API v2 returns data in response.data
            if result.get("success") and "data" in result:
                return result["data"]
            return result
        except httpx.HTTPStatusError as e:
            error_detail = ""
            try:
                error_body = e.response.json()
                error_msg = error_body.get('error') or error_body.get('message', str(e))
                error_detail = f" - {error_msg}"
            except:
                error_detail = f" - {e.response.text[:200]}"
            raise Exception(f"Firecrawl API error: {e.response.status_code}{error_detail}")
        except Exception as e:
            raise Exception(f"Firecrawl API error: {str(e)}")
    
    async def extract(
        self,
        urls: List[str],
        prompt: str,
        schema: Optional[Dict[str, Any]] = None,
        extraction_type: str = "llm-extraction"
    ) -> Dict[str, Any]:
        """Extract structured data from URLs using Firecrawl API v2 extract endpoint"""
        payload = {
            "urls": urls,
            "prompt": prompt
        }
        
        if schema:
            payload["schema"] = schema
        
        if extraction_type:
            payload["extractionType"] = extraction_type
        
        try:
            response = await self.client.post(
                f"{self.base_url}/extract",
                json=payload
            )
            response.raise_for_status()
            result = response.json()
            # API v2 returns data in response.data
            if result.get("success") and "data" in result:
                return result["data"]
            return result
        except httpx.HTTPStatusError as e:
            error_detail = ""
            try:
                error_body = e.response.json()
                error_msg = error_body.get('error') or error_body.get('message', str(e))
                error_detail = f" - {error_msg}"
            except:
                error_detail = f" - {e.response.text[:200]}"
            raise Exception(f"Firecrawl API error: {e.response.status_code}{error_detail}")
        except Exception as e:
            raise Exception(f"Firecrawl API error: {str(e)}")
    
    async def search_website(
        self,
        query: str,
        url: Optional[str] = None,
        limit: int = 10
    ) -> Dict[str, Any]:
        """Search across website content"""
        payload = {
            "query": query,
            "limit": limit
        }
        
        if url:
            payload["url"] = url
        
        try:
            response = await self.client.post(
                f"{self.base_url}/search",
                json=payload
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            error_detail = ""
            try:
                error_body = e.response.json()
                error_detail = f" - {error_body.get('error', {}).get('message', str(e))}"
            except:
                error_detail = f" - {e.response.text[:200]}"
            raise Exception(f"Firecrawl API error: {e.response.status_code}{error_detail}")
        except Exception as e:
            raise Exception(f"Firecrawl API error: {str(e)}")
    
    async def web_search(
        self,
        query: str,
        limit: int = 10,
        sources: Optional[List[str]] = None,
        categories: Optional[List[str]] = None,
        location: Optional[str] = None,
        tbs: Optional[str] = None,
        timeout: Optional[int] = None,
        scrape_options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Perform web search using Firecrawl Search API"""
        payload = {
            "query": query,
            "limit": limit
        }
        
        if sources:
            payload["sources"] = sources
        if categories:
            payload["categories"] = categories
        if location:
            payload["location"] = location
        if tbs:
            payload["tbs"] = tbs
        if timeout:
            payload["timeout"] = timeout
        if scrape_options:
            payload["scrapeOptions"] = scrape_options
        
        try:
            response = await self.client.post(
                f"{self.base_url}/search",
                json=payload
            )
            response.raise_for_status()
            result = response.json()
            # API returns data in response.data
            if result.get("success") and "data" in result:
                return result["data"]
            return result
        except httpx.HTTPStatusError as e:
            error_detail = ""
            try:
                error_body = e.response.json()
                error_msg = error_body.get('error') or error_body.get('message', str(e))
                error_detail = f" - {error_msg}"
            except:
                error_detail = f" - {e.response.text[:200]}"
            raise Exception(f"Firecrawl Search API error: {e.response.status_code}{error_detail}")
        except Exception as e:
            raise Exception(f"Firecrawl Search API error: {str(e)}")
    
    async def _poll_job(
        self,
        job_id: str,
        job_type: str = "crawl",
        max_attempts: int = 60
    ) -> List[Dict]:
        """Polling для crawl/extract jobs"""
        import asyncio
        
        for attempt in range(max_attempts):
            await asyncio.sleep(5)
            
            response = await self.client.get(f"{self.base_url}/{job_type}/{job_id}")
            response.raise_for_status()
            status_data = response.json()
            
            status = status_data.get("status")
            completed = status_data.get("completed", 0)
            total = status_data.get("total", 0)
            
            # Progress messages removed per user request
            
            if status == "completed":
                return status_data.get("data", [])
            elif status == "failed":
                error_msg = status_data.get("error", "Unknown error")
                raise Exception(f"{job_type.title()} failed: {error_msg}")
        
        raise Exception(f"{job_type.title()} timeout after {max_attempts * 5} seconds")
    
    # ==================== ФАЗА 0: АНАЛИЗ СТРУКТУРЫ САЙТА ====================
    
    async def phase0_analyze_site_structure(self, url: str) -> Dict[str, Any]:
        """
        ФАЗА 0: Автоматический анализ структуры сайта
        - Определение CMS (WordPress, Wix, Custom)
        - Анализ паттернов URL
        - Определение типов страниц
        """
        print(f"📊 Phase 0: Analyzing site structure...")
        
        # Получаем homepage для анализа
        try:
            homepage_result = await self.scrape_url(
                url=url,
                formats=[{"type": "html"}]
            )
            homepage_html = homepage_result.get("html", "")
            if not homepage_html:
                # Fallback: используем markdown
                homepage_result = await self.scrape_url(
                    url=url,
                    formats=[{"type": "markdown"}]
                )
                homepage_html = homepage_result.get("markdown", "")
        except Exception as e:
            print(f"⚠️ Failed to fetch homepage: {e}")
            homepage_html = ""
        
        # Определение CMS
        cms_detected = self._detect_cms(homepage_html)
        print(f"   ✓ CMS detected: {cms_detected}")
        
        # Анализ структуры навигации
        url_patterns = self._analyze_url_patterns(homepage_html, url)
        
        # Определение пагинации
        pagination_info = self._detect_pagination(homepage_html)
        
        # Определение infinite scroll
        has_infinite_scroll = self._detect_infinite_scroll(homepage_html)
        
        return {
            "cms": cms_detected,
            "url_patterns": url_patterns,
            "pagination": pagination_info,
            "infinite_scroll": has_infinite_scroll,
            "base_url": url
        }
    
    def _detect_cms(self, html: str) -> str:
        """Определение CMS по сигнатурам"""
        if not html:
            return "Unknown"
        
        html_lower = html.lower()
        
        cms_signatures = {
            "WordPress": [
                'wp-content', 'wp-includes', 'wp-json',
                'wordpress', 'wp-admin'
            ],
            "Drupal": [
                '/sites/default/', 'drupal.settings',
                'drupal.js', 'drupal'
            ],
            "Wix": [
                'wix.com', '_wix', 'wixstatic',
                'x-wix-request-id'
            ],
            "Squarespace": [
                'squarespace', 'static.squarespace',
                'squarespace-cdn'
            ],
            "Webflow": [
                'webflow', 'assets.website-files.com',
                'webflow.io'
            ],
            "Shopify": [
                'shopify', 'cdn.shopify.com',
                'shopify-section'
            ]
        }
        
        for cms, patterns in cms_signatures.items():
            if any(pattern in html_lower for pattern in patterns):
                return cms
        
        return "Custom"
    
    def _analyze_url_patterns(self, html: str, base_url: str) -> Dict[str, List[str]]:
        """Анализ паттернов URL из HTML"""
        if not html:
            return {}
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            links = []
            
            for a in soup.find_all('a', href=True):
                href = a['href']
                # Нормализация URL
                if href.startswith('/'):
                    href = base_url.rstrip('/') + href
                elif not href.startswith('http'):
                    continue
                
                # Только внутренние ссылки
                if base_url in href:
                    links.append(href)
            
            # Классификация по паттернам
            patterns = {
                "listings": [],
                "detail": [],
                "regional": [],
                "services": [],
                "about": [],
                "news": [],
                "contact": [],
                "other": []
            }
            
            keywords = {
                "listings": ['homes', 'directory', 'find', 'search', 'list', 'locations', 'all-homes'],
                "detail": [],  # Определяется по глубине
                "regional": ['location', 'area', 'region', 'county', 'city', 'birmingham', 'london', 'manchester'],
                "services": ['services', 'care-types', 'nursing', 'dementia', 'residential', 'respite'],
                "about": ['about', 'company', 'who-we-are', 'our-story', 'team'],
                "news": ['news', 'blog', 'articles', 'stories', 'press'],
                "contact": ['contact', 'enquire', 'get-in-touch', 'book']
            }
            
            for link in links:
                url_lower = link.lower()
                classified = False
                
                for category, words in keywords.items():
                    if any(word in url_lower for word in words):
                        patterns[category].append(link)
                        classified = True
                        break
                
                if not classified:
                    # Эвристика для detail pages (глубокие URL)
                    path_parts = urlparse(link).path.strip('/').split('/')
                    if len(path_parts) >= 3:
                        patterns["detail"].append(link)
                    else:
                        patterns["other"].append(link)
            
            return patterns
            
        except Exception as e:
            print(f"⚠️ Error analyzing URL patterns: {e}")
            return {}
    
    def _detect_pagination(self, html: str) -> Optional[Dict[str, Any]]:
        """Определение паттерна пагинации"""
        if not html:
            return None
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            pagination_patterns = [
                r'\?page=(\d+)',
                r'/page/(\d+)/',
                r'\?offset=(\d+)',
                r'#page-(\d+)'
            ]
            
            # Поиск ссылок на следующие страницы
            pagination_links = soup.find_all('a', href=True, text=re.compile(r'next|›|»|>', re.I))
            pagination_links += soup.find_all('a', href=re.compile(r'page=\d+|/page/\d+'))
            
            if not pagination_links:
                # Проверка по HTML напрямую
                for pattern in pagination_patterns:
                    if re.search(pattern, html, re.IGNORECASE):
                        return {
                            "type": "url_parameter" if '?' in pattern else "path_segment",
                            "pattern": pattern
                        }
                return None
            
            # Определение паттерна из найденных ссылок
            for link in pagination_links:
                href = link.get('href', '')
                for pattern in pagination_patterns:
                    if re.search(pattern, href):
                        return {
                            "type": "url_parameter" if '?' in pattern else "path_segment",
                            "pattern": pattern,
                            "example": href
                        }
        except Exception as e:
            print(f"⚠️ Error detecting pagination: {e}")
        
        return None
    
    def _detect_infinite_scroll(self, html: str) -> bool:
        """Определение infinite scroll (JavaScript loading)"""
        if not html:
            return False
        
        indicators = [
            r'infinite[- ]?scroll',
            r'lazy[- ]?load',
            r'load[- ]?more',
            r'scroll[- ]?event'
        ]
        
        for indicator in indicators:
            if re.search(indicator, html, re.IGNORECASE):
                return True
        
        return False
    
    # ==================== ФАЗА 1: ИНТЕЛЛЕКТУАЛЬНОЕ ОБНАРУЖЕНИЕ ====================
    
    async def phase1_discover_structure(self, url: str, phase0_result: Optional[Dict] = None) -> Dict[str, Any]:
        """
        ФАЗА 1: Map - Быстрое обнаружение структуры сайта
        Map endpoint очень быстрый (15x быстрее в v2.5) и может обработать до 100k URLs
        Улучшено: использует результаты Фазы 0 для оптимизации
        """
        map_payload = {
            "url": url,
            "limit": 1000,  # Map может обработать до 100k URLs
            "includeSubdomains": False
        }
        
        response = await self.client.post(
            f"{self.base_url}/map",
            json=map_payload
        )
        response.raise_for_status()
        map_result = response.json()
        
        # Получаем список всех URL - проверяем разные форматы ответа
        all_urls = []
        
        # Формат 1: {"success": true, "links": [...]}
        if map_result.get("success") and "links" in map_result:
            links = map_result.get("links", [])
            # Если links - это массив объектов с полем "url"
            if links and isinstance(links[0], dict) and "url" in links[0]:
                all_urls = [link.get("url") for link in links if link.get("url")]
            # Если links - это массив строк
            elif links and isinstance(links[0], str):
                all_urls = links
        
        # Формат 2: {"data": {"urls": [...]}}
        if not all_urls:
            all_urls = map_result.get("data", {}).get("urls", [])
        
        # Формат 3: {"urls": [...]}
        if not all_urls:
            all_urls = map_result.get("urls", [])
        
        print(f"🗺️ Map: Found {len(all_urls)} URLs on site")
        
        # Классифицируем URL по типам (расширенная классификация)
        classified = {
            "staff": [],
            "facilities": [],
            "services": [],
            "pricing": [],
            "activities": [],
            "contact": [],
            "about": [],
            "nutrition": [],
            "reviews": [],
            "awards": [],
            "safety": [],
            "transport": [],
            "media": [],
            "policies": [],
            "events": [],
            "faq": [],
            "other": []
        }
        
        for url_item in all_urls:
            url_path = str(url_item).lower()
            
            if any(word in url_path for word in ['staff', 'team', 'our-people', 'care-team', 'people', 'management']):
                classified["staff"].append(url_item)
            elif any(word in url_path for word in ['facilities', 'amenities', 'rooms', 'accommodation', 'building']):
                classified["facilities"].append(url_item)
            elif any(word in url_path for word in ['services', 'care-types', 'what-we-offer', 'care-services', 'care']):
                classified["services"].append(url_item)
            elif any(word in url_path for word in ['fees', 'pricing', 'costs', 'fees-and-funding', 'funding', 'price', 'charge']):
                classified["pricing"].append(url_item)
            elif any(word in url_path for word in ['activities', 'lifestyle', 'events', 'daily-life', 'programs', 'entertainment']):
                classified["activities"].append(url_item)
            elif any(word in url_path for word in ['contact', 'get-in-touch', 'enquire', 'enquiry', 'location', 'find-us']):
                classified["contact"].append(url_item)
            elif any(word in url_path for word in ['menu', 'dining', 'nutrition', 'food', 'meals', 'catering', 'restaurant']):
                classified["nutrition"].append(url_item)
            elif any(word in url_path for word in ['review', 'testimonial', 'feedback', 'recommendation', 'rating']):
                classified["reviews"].append(url_item)
            elif any(word in url_path for word in ['award', 'accreditation', 'certification', 'recognition', 'achievement']):
                classified["awards"].append(url_item)
            elif any(word in url_path for word in ['safety', 'security', 'safeguarding', 'protection', 'emergency']):
                classified["safety"].append(url_item)
            elif any(word in url_path for word in ['transport', 'parking', 'access', 'directions', 'travel', 'bus']):
                classified["transport"].append(url_item)
            elif any(word in url_path for word in ['gallery', 'photo', 'video', 'image', 'media', 'virtual-tour', 'tour']):
                classified["media"].append(url_item)
            elif any(word in url_path for word in ['policy', 'procedure', 'terms', 'privacy', 'complaint', 'safeguarding', 'policies', 'legal', 'compliance']):
                classified["policies"].append(url_item)
            elif any(word in url_path for word in ['news', 'event', 'update', 'announcement', 'blog']):
                classified["events"].append(url_item)
            elif any(word in url_path for word in ['faq', 'question', 'answer', 'help', 'guide', 'frequently-asked', 'faqs']):
                classified["faq"].append(url_item)
            elif any(word in url_path for word in ['about', 'our-home', 'welcome', 'home', 'history', 'story']):
                classified["about"].append(url_item)
            else:
                classified["other"].append(url_item)
        
        return {
            "total_urls": len(all_urls),
            "classified": classified,
            "all_urls": all_urls
        }
    
    async def phase2_semantic_crawl(
        self,
        url: str,
        classified_urls: Dict[str, List[str]],
        phase0_result: Optional[Dict] = None,
        map_result: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        ФАЗА 2: Semantic crawl для получения КОНТЕНТА найденных страниц
        Улучшено: адаптивный prompt, URL templates для фильтрации, выбор стартовых URL
        """
        # Выбор оптимальных стартовых URL
        url_patterns = {}
        if map_result:
            url_patterns = {
                "listings": map_result.get('classified', {}).get('other', []),
                "regional": map_result.get('classified', {}).get('about', [])
            }
        
        start_urls = self._select_start_urls(url_patterns, url)
        start_url = start_urls[0] if start_urls else url
        
        # Собираем приоритетные URL для crawl (расширенный список)
        priority_urls = (
            classified_urls.get("staff", [])[:5] +
            classified_urls.get("facilities", [])[:5] +
            classified_urls.get("services", [])[:5] +
            classified_urls.get("pricing", [])[:3] +
            classified_urls.get("activities", [])[:3] +
            classified_urls.get("contact", [])[:2] +
            classified_urls.get("about", [])[:2] +
            classified_urls.get("nutrition", [])[:3] +
            classified_urls.get("reviews", [])[:3] +
            classified_urls.get("awards", [])[:2] +
            classified_urls.get("safety", [])[:2] +
            classified_urls.get("transport", [])[:2] +
            classified_urls.get("media", [])[:2] +
            classified_urls.get("policies", [])[:2] +
            classified_urls.get("events", [])[:2] +
            classified_urls.get("faq", [])[:2]
        )
        
        # Если нет приоритетных URL из Map или их очень мало, используем semantic crawl с discovery
        total_classified_urls = sum(len(urls) for urls in classified_urls.values())
        if not priority_urls or total_classified_urls < 5:
            if total_classified_urls < 5:
                print(f"⚠️ Map found only {total_classified_urls} URLs, using semantic crawl with discovery...")
            else:
                print(f"⚠️ No priority URLs from Map, using semantic crawl with discovery...")
            # Увеличиваем limit для semantic discovery
            crawl_limit = 30
            max_depth = 3  # Больше глубина для discovery
        else:
            crawl_limit = min(len(priority_urls) + 10, 50)
            max_depth = 2
        
        print(f"🕷️ Crawl: Starting from {start_url}, processing {len(priority_urls)} priority pages")
        
        # Генерация адаптивного prompt на основе Фазы 0
        crawl_prompt = self._generate_adaptive_prompt(phase0_result, classified_urls)
        
        # Определение waitFor на основе CMS
        wait_for = 2000  # По умолчанию
        if phase0_result:
            cms = phase0_result.get("cms", "")
            if cms == "Wix":
                wait_for = 3000  # Wix требует больше времени для JS
            elif cms == "WordPress":
                wait_for = 1500  # WordPress быстрее
            
            # Учитываем infinite scroll
            if phase0_result.get("infinite_scroll"):
                wait_for += 1000  # Дополнительное время для загрузки
        
        crawl_payload = {
            "url": start_url,
            "limit": crawl_limit,
            "prompt": crawl_prompt,
            "maxDiscoveryDepth": max_depth,
            "scrapeOptions": {
                "formats": [{"type": "markdown"}],
                "onlyMainContent": True,
                "waitFor": wait_for
            }
        }
        
        # Добавляем includePaths если есть URL templates
        if map_result and map_result.get('url_templates'):
            include_patterns = self._templates_to_regex(map_result['url_templates'])
            if include_patterns:
                crawl_payload["includePaths"] = include_patterns[:5]  # Ограничиваем до 5 паттернов
                print(f"   📋 Using {len(include_patterns)} URL templates for filtering")
        
        response = await self.client.post(
            f"{self.base_url}/crawl",
            json=crawl_payload
        )
        response.raise_for_status()
        crawl_job = response.json()
        
        # Ждем завершения crawl
        job_id = crawl_job.get("id")
        if not job_id:
            raise Exception("No job ID returned from crawl")
        
        crawl_data = await self._poll_job(job_id, job_type="crawl")
        
        print(f"✅ Crawl: Retrieved {len(crawl_data)} pages with content")
        
        return {
            "pages_crawled": len(crawl_data),
            "pages_data": crawl_data
        }
    
    async def phase3_extract_structured_data(
        self,
        pages_data: List[Dict],
        care_home_name: str,
        url: str,
        use_claude: bool = True,
        discovery_result: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        ФАЗА 3: AI-извлечение структурированных данных
        Улучшено: использует Claude API если доступен, фильтрует detail pages
        """
        # Фильтрация detail pages если есть discovery_result
        # Но не фильтруем если страниц мало (меньше 5), чтобы не потерять данные
        original_count = len(pages_data)
        if discovery_result and len(pages_data) >= 5:
            filtered_pages = self._filter_detail_pages(pages_data, discovery_result)
            # Используем отфильтрованные страницы только если их достаточно (больше 3)
            if len(filtered_pages) >= 3:
                pages_data = filtered_pages
                print(f"   📋 После фильтрации: {len(pages_data)} detail pages (из {original_count})")
            else:
                print(f"   ⚠️ Фильтрация дала слишком мало страниц ({len(filtered_pages)}), используем все {original_count} страниц")
        elif discovery_result:
            print(f"   ⚠️ Мало страниц ({len(pages_data)}), пропускаем фильтрацию")
        
        # Группируем страницы по категориям (расширенная классификация)
        pages_by_category = {
            "staff": [],
            "facilities": [],
            "services": [],
            "pricing": [],
            "activities": [],
            "contact": [],
            "about": [],
            "nutrition": [],
            "reviews": [],
            "awards": [],
            "safety": [],
            "transport": [],
            "media": [],
            "policies": [],
            "events": [],
            "faq": []
        }
        
        for page in pages_data:
            page_url = page.get("metadata", {}).get("sourceURL", "")
            if not page_url:
                continue
            url_lower = page_url.lower()
            
            if any(word in url_lower for word in ['staff', 'team', 'people', 'our-people', 'management']):
                pages_by_category["staff"].append(page)
            elif any(word in url_lower for word in ['facilities', 'rooms', 'amenities', 'accommodation', 'building']):
                pages_by_category["facilities"].append(page)
            elif any(word in url_lower for word in ['services', 'care', 'offer', 'care-types']):
                pages_by_category["services"].append(page)
            elif any(word in url_lower for word in ['fees', 'pricing', 'costs', 'funding', 'price', 'charge']):
                pages_by_category["pricing"].append(page)
            elif any(word in url_lower for word in ['activities', 'lifestyle', 'events', 'programs', 'entertainment']):
                pages_by_category["activities"].append(page)
            elif any(word in url_lower for word in ['contact', 'enquire', 'enquiry', 'location', 'find-us']):
                pages_by_category["contact"].append(page)
            elif any(word in url_lower for word in ['menu', 'dining', 'nutrition', 'food', 'meals', 'catering']):
                pages_by_category["nutrition"].append(page)
            elif any(word in url_lower for word in ['review', 'testimonial', 'feedback', 'recommendation']):
                pages_by_category["reviews"].append(page)
            elif any(word in url_lower for word in ['award', 'accreditation', 'certification', 'recognition']):
                pages_by_category["awards"].append(page)
            elif any(word in url_lower for word in ['safety', 'security', 'safeguarding', 'protection']):
                pages_by_category["safety"].append(page)
            elif any(word in url_lower for word in ['transport', 'parking', 'access', 'directions', 'travel']):
                pages_by_category["transport"].append(page)
            elif any(word in url_lower for word in ['gallery', 'photo', 'video', 'image', 'media', 'virtual-tour']):
                pages_by_category["media"].append(page)
            elif any(word in url_lower for word in ['policy', 'procedure', 'terms', 'complaint']):
                pages_by_category["policies"].append(page)
            elif any(word in url_lower for word in ['news', 'event', 'update', 'announcement', 'blog']):
                pages_by_category["events"].append(page)
            elif any(word in url_lower for word in ['faq', 'question', 'answer', 'help', 'guide']):
                pages_by_category["faq"].append(page)
            elif any(word in url_lower for word in ['about', 'our-home', 'welcome', 'history', 'story']):
                pages_by_category["about"].append(page)
        
        # Извлекаем данные по категориям с упрощенными схемами
        extracted_data = {}
        
        # Расширенная схема для всех категорий (150+ полей)
        full_schema = {
            "type": "object",
            "properties": {
                "care_home_name": {"type": "string"},
                "staff": {
                    "type": "object",
                    "properties": {
                        "team_size": {"type": "string"},
                        "qualifications": {"type": "array", "items": {"type": "string"}},
                        "specialist_roles": {"type": "array", "items": {"type": "string"}},
                        "key_staff": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "role": {"type": "string"},
                                    "qualifications": {"type": "string"},
                                    "bio": {"type": "string"}
                                }
                            }
                        },
                        "training_programs": {"type": "array", "items": {"type": "string"}},
                        "staff_ratios": {"type": "string"}
                    }
                },
                "facilities": {
                    "type": "object",
                    "properties": {
                        "rooms": {"type": "array", "items": {"type": "string"}},
                        "communal_areas": {"type": "array", "items": {"type": "string"}},
                        "outdoor_spaces": {"type": "array", "items": {"type": "string"}},
                        "special_facilities": {"type": "array", "items": {"type": "string"}},
                        "accessibility": {"type": "array", "items": {"type": "string"}},
                        "room_count": {"type": "string"},
                        "capacity": {"type": "string"},
                        "building_type": {"type": "string"},
                        "year_built": {"type": "string"},
                        "recent_renovations": {"type": "array", "items": {"type": "string"}}
                    }
                },
                "care_services": {
                    "type": "object",
                    "properties": {
                        "care_types": {"type": "array", "items": {"type": "string"}},
                        "specializations": {"type": "array", "items": {"type": "string"}},
                        "medical_services": {"type": "array", "items": {"type": "string"}},
                        "end_of_life_care": {"type": "boolean"},
                        "respite_care": {"type": "boolean"},
                        "day_care": {"type": "boolean"},
                        "emergency_admissions": {"type": "boolean"},
                        "care_plans": {"type": "string"}
                    }
                },
                "pricing": {
                    "type": "object",
                    "properties": {
                        "weekly_rate_range": {"type": "string"},
                        "included_services": {"type": "array", "items": {"type": "string"}},
                        "additional_fees": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "service": {"type": "string"},
                                    "cost": {"type": "string"},
                                    "frequency": {"type": "string"}
                                }
                            }
                        },
                        "funding_options": {"type": "array", "items": {"type": "string"}},
                        "deposit_required": {"type": "string"},
                        "payment_methods": {"type": "array", "items": {"type": "string"}},
                        "price_transparency": {"type": "string"}
                    }
                },
                "activities": {
                    "type": "object",
                    "properties": {
                        "daily_activities": {"type": "array", "items": {"type": "string"}},
                        "therapies": {"type": "array", "items": {"type": "string"}},
                        "outings": {"type": "array", "items": {"type": "string"}},
                        "special_events": {"type": "array", "items": {"type": "string"}},
                        "activity_coordinator": {"type": "string"},
                        "visitor_programs": {"type": "array", "items": {"type": "string"}}
                    }
                },
                "contact": {
                    "type": "object",
                    "properties": {
                        "phone": {"type": "string"},
                        "email": {"type": "string"},
                        "address": {"type": "string"},
                        "visiting_hours": {"type": "string"},
                        "website": {"type": "string"},
                        "emergency_contact": {"type": "string"},
                        "postcode": {"type": "string"},
                        "coordinates": {
                            "type": "object",
                            "properties": {
                                "latitude": {"type": "string"},
                                "longitude": {"type": "string"}
                            }
                        }
                    }
                },
                "registration": {
                    "type": "object",
                    "properties": {
                        "cqc_provider_id": {"type": "string"},
                        "cqc_location_id": {"type": "string"},
                        "registered_manager": {"type": "string"},
                        "registration_date": {"type": "string"},
                        "last_inspection_date": {"type": "string"},
                        "cqc_rating": {"type": "string"}
                    }
                },
                "nutrition": {
                    "type": "object",
                    "properties": {
                        "meal_times": {"type": "string"},
                        "dining_options": {"type": "array", "items": {"type": "string"}},
                        "dietary_accommodations": {"type": "array", "items": {"type": "string"}},
                        "menu_variety": {"type": "string"},
                        "snacks_available": {"type": "boolean"},
                        "special_diets": {"type": "array", "items": {"type": "string"}},
                        "dining_environment": {"type": "string"},
                        "nutritional_planning": {"type": "string"}
                    }
                },
                "reviews": {
                    "type": "object",
                    "properties": {
                        "testimonials": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "author": {"type": "string"},
                                    "relationship": {"type": "string"},
                                    "rating": {"type": "string"},
                                    "comment": {"type": "string"},
                                    "date": {"type": "string"}
                                }
                            }
                        },
                        "average_rating": {"type": "string"},
                        "review_count": {"type": "string"},
                        "review_sources": {"type": "array", "items": {"type": "string"}}
                    }
                },
                "awards": {
                    "type": "object",
                    "properties": {
                        "awards_list": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "year": {"type": "string"},
                                    "organization": {"type": "string"}
                                }
                            }
                        },
                        "accreditations": {"type": "array", "items": {"type": "string"}},
                        "certifications": {"type": "array", "items": {"type": "string"}},
                        "memberships": {"type": "array", "items": {"type": "string"}}
                    }
                },
                "safety": {
                    "type": "object",
                    "properties": {
                        "safeguarding_policies": {"type": "array", "items": {"type": "string"}},
                        "emergency_procedures": {"type": "string"},
                        "security_features": {"type": "array", "items": {"type": "string"}},
                        "fire_safety": {"type": "string"},
                        "infection_control": {"type": "string"},
                        "medication_management": {"type": "string"},
                        "risk_assessment": {"type": "string"}
                    }
                },
                "transport": {
                    "type": "object",
                    "properties": {
                        "parking_available": {"type": "boolean"},
                        "parking_spaces": {"type": "string"},
                        "public_transport": {"type": "array", "items": {"type": "string"}},
                        "accessibility_by_car": {"type": "string"},
                        "nearby_amenities": {"type": "array", "items": {"type": "string"}},
                        "directions": {"type": "string"}
                    }
                },
                "media": {
                    "type": "object",
                    "properties": {
                        "photo_gallery": {"type": "array", "items": {"type": "string"}},
                        "videos": {"type": "array", "items": {"type": "string"}},
                        "virtual_tour": {"type": "string"},
                        "brochure_download": {"type": "string"},
                        "social_media": {
                            "type": "object",
                            "properties": {
                                "facebook": {"type": "string"},
                                "twitter": {"type": "string"},
                                "instagram": {"type": "string"}
                            }
                        }
                    }
                },
                "policies": {
                    "type": "object",
                    "properties": {
                        "admission_policy": {"type": "string"},
                        "visiting_policy": {"type": "string"},
                        "complaints_procedure": {"type": "string"},
                        "privacy_policy": {"type": "string"},
                        "terms_and_conditions": {"type": "string"},
                        "safeguarding_policy": {"type": "string"}
                    }
                },
                "events": {
                    "type": "object",
                    "properties": {
                        "upcoming_events": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string"},
                                    "date": {"type": "string"},
                                    "description": {"type": "string"}
                                }
                            }
                        },
                        "news_updates": {"type": "array", "items": {"type": "string"}},
                        "announcements": {"type": "array", "items": {"type": "string"}}
                    }
                },
                "faq": {
                    "type": "object",
                    "properties": {
                        "questions": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "question": {"type": "string"},
                                    "answer": {"type": "string"}
                                }
                            }
                        }
                    }
                },
                "about": {
                    "type": "object",
                    "properties": {
                        "history": {"type": "string"},
                        "years_in_operation": {"type": "string"},
                        "mission_statement": {"type": "string"},
                        "values": {"type": "array", "items": {"type": "string"}},
                        "description": {"type": "string"},
                        "owner_operator": {"type": "string"}
                    }
                }
            },
            "required": ["care_home_name"]
        }
        
        # Собираем URL всех релевантных страниц
        all_relevant_urls = []
        for category_pages in pages_by_category.values():
            for page in category_pages[:3]:  # Берем до 3 страниц каждой категории
                page_url = page.get("metadata", {}).get("sourceURL")
                if page_url:
                    all_relevant_urls.append(page_url)
        
        # Fallback: если категоризация не дала результатов или дала мало URL, используем все страницы
        if not all_relevant_urls or len(all_relevant_urls) < 5:
            if not all_relevant_urls:
                print(f"   ⚠️ No categorized URLs, using all {len(pages_data)} pages for extraction")
            else:
                print(f"   ⚠️ Too few categorized URLs ({len(all_relevant_urls)}), adding more pages")
            
            # Добавляем страницы из всех категорий, даже если они не были категоризированы
            for page in pages_data[:20]:  # Увеличиваем до 20 страниц
                page_url = page.get("metadata", {}).get("sourceURL") or page.get("url", "")
                if page_url and page_url not in all_relevant_urls:
                    all_relevant_urls.append(page_url)
        
        # Если есть релевантные URL, используем Extract endpoint для извлечения
        if all_relevant_urls:
            # Используем до 15 URL для лучшего покрытия категорий
            urls_to_extract = all_relevant_urls[:15]
            print(f"   📄 Extracting from {len(urls_to_extract)} URLs")
            
            extract_payload = {
                "urls": urls_to_extract,
                "prompt": f"""Extract comprehensive information about {care_home_name} from these pages.

IMPORTANT: Extract REAL DATA only. Do NOT create empty structures (empty lists, empty strings, empty dictionaries). 
If information is not available, omit that field entirely rather than including it with empty values.

Focus on ALL available categories and extract ACTUAL CONTENT:
1. Staff: Extract actual qualifications, team size numbers, real staff member names and roles, specific training programs mentioned
2. Facilities: Extract actual room types, specific communal areas, real outdoor spaces, concrete special facilities, actual accessibility features
3. Care services: Extract actual care types offered, specific specializations, real medical services, concrete care plans
4. Pricing: Extract actual weekly rates (numbers), real included services, specific additional fees, actual funding options, deposit amounts
5. Activities: Extract actual daily activities listed, real therapies offered, specific outings mentioned, concrete special events
6. Contact: Extract actual phone numbers, real email addresses, full addresses, visiting hours, emergency contacts, coordinates
7. Registration: Extract actual CQC IDs, registered manager names, real inspection dates, actual ratings
8. Nutrition: Extract actual meal times, real dietary options, specific menu items, actual special diets supported
9. Reviews: Extract actual testimonials text, real ratings, specific review sources
10. Awards: Extract actual award names, real accreditations, specific certifications, actual memberships
11. Safety: Extract actual safeguarding policies text, real emergency procedures, specific security features
12. Transport: Extract actual parking information, real public transport details, specific directions, actual nearby amenities
13. Media: Extract actual photo galleries mentioned, real videos, virtual tours links, brochures, social media links
14. Policies: Extract actual admission policies, real visiting policies, complaints procedures, privacy policy links
15. Events: Extract actual upcoming events with dates, real news items, specific announcements
16. FAQ: Extract actual questions and their answers from FAQ sections
17. About: Extract actual history text, real mission statements, specific values, description text, owner/operator names

CRITICAL: Only include fields that have actual content. Do not include empty arrays, empty strings, or empty objects.""",
                "schema": full_schema,
                "enableWebSearch": False,
                "includeSubdomains": False
            }
            
            try:
                extract_response = await self.client.post(
                    f"{self.base_url}/extract",
                    json=extract_payload
                )
                extract_response.raise_for_status()
                extract_result = extract_response.json()
                
                # Обрабатываем результат Extract endpoint
                if extract_result.get("id"):
                    # Async job - poll for results
                    extract_data = await self._poll_job(extract_result.get("id"), job_type="extract")
                    if extract_data:
                        extracted_data = extract_data[0] if isinstance(extract_data, list) and extract_data else extract_data
                elif extract_result.get("success") and "data" in extract_result:
                    extracted_data = extract_result.get("data", {})
                else:
                    extracted_data = {}
            except Exception as e:
                print(f"⚠️ Extract endpoint error: {e}, falling back to scrape")
                extracted_data = {}
        else:
            extracted_data = {}
        
        # Fallback: если Extract не дал результатов или дал неполные данные, используем Scrape на нескольких страницах
        # Проверяем сколько категорий заполнено
        filled_categories = 0
        if extracted_data:
            filled_categories = sum(1 for cat in [
                "staff", "facilities", "services", "pricing", "activities", "contact",
                "nutrition", "reviews", "awards", "safety", "transport", "media",
                "policies", "events", "faq", "about"
            ] if extracted_data.get(cat))
            
            if filled_categories < 12:  # Если заполнено меньше 12 категорий, пробуем scrape
                print(f"   ⚠️ Only {filled_categories}/16 categories filled, trying scrape fallback...")
        
        if not extracted_data or filled_categories < 12:
            try:
                # Используем несколько страниц для scrape fallback
                scrape_urls = [url] + [page.get("metadata", {}).get("sourceURL") or page.get("url", "") 
                                      for page in pages_data[:3] 
                                      if page.get("metadata", {}).get("sourceURL") or page.get("url", "")]
                
                for scrape_url in scrape_urls[:3]:  # Пробуем до 3 страниц
                    try:
                        scrape_result = await self.scrape_url(
                            url=scrape_url,
                            formats=[{
                                "type": "json",
                                "schema": full_schema,
                                "prompt": f"""Extract comprehensive information about {care_home_name} from this page.

IMPORTANT: Extract REAL DATA only. Do NOT create empty structures (empty lists, empty strings, empty dictionaries). 
If information is not available, omit that field entirely rather than including it with empty values.

Focus on ALL categories and extract ACTUAL CONTENT:
- Staff: actual qualifications, team size numbers, real staff member names and roles
- Facilities: actual room types, specific communal areas, real outdoor spaces
- Care services: actual care types, specific specializations, real medical services
- Pricing: actual weekly rates (numbers), real included services, specific fees
- Activities: actual daily activities, real therapies, specific outings
- Contact: actual phone numbers, real email addresses, full addresses
- Nutrition: actual meal times, real dietary options, specific menu items
- Reviews: actual testimonials text, real ratings
- Awards: actual award names, real accreditations
- Safety: actual safeguarding policies text, real emergency procedures
- Transport: actual parking information, real public transport details
- Media: actual photo galleries, real videos, social media links
- Policies: actual admission policies, real visiting policies, complaints procedures
- Events: actual upcoming events with dates, real news items
- FAQ: actual questions and their answers
- About: actual history text, real mission statements, description text

CRITICAL: Only include fields that have actual content. Do not include empty arrays, empty strings, or empty objects."""
                            }]
                        )
                        if scrape_result.get("json"):
                            scrape_data = scrape_result.get("json", {})
                            # Объединяем данные, приоритет отдаем новым данным
                            if not extracted_data:
                                extracted_data = scrape_data
                            else:
                                # Мержим данные, заполняя пустые категории
                                for key, value in scrape_data.items():
                                    if not extracted_data.get(key) and value:
                                        extracted_data[key] = value
                            print(f"   ✅ Scrape fallback extracted data from {scrape_url}")
                            break  # Если получили данные, прекращаем попытки
                    except Exception as e:
                        print(f"   ⚠️ Scrape error for {scrape_url}: {e}")
                        continue
            except Exception as e:
                print(f"⚠️ Scrape fallback error: {e}")
        
        return extracted_data
    
    async def extract_care_home_complete(
        self,
        url: str,
        care_home_name: str
    ) -> Dict[str, Any]:
        """
        ПОЛНЫЙ 4-фазный метод извлечения данных о доме престарелых
        
        ФАЗА 0: Анализ структуры сайта (CMS, URL patterns)
        ФАЗА 1: Map - интеллектуальное обнаружение структуры
        ФАЗА 2: Crawl - адаптивный семантический сбор контента
        ФАЗА 3: Extract - AI-извлечение (Claude → Firecrawl → Regex fallback)
        """
        print(f"\n{'='*60}")
        print(f"🏥 4-PHASE UNIVERSAL EXTRACTION")
        print(f"🏥 Analyzing: {care_home_name}")
        print(f"🌐 URL: {url}")
        print(f"{'='*60}\n")
        
        # ФАЗА 0: Анализ структуры сайта
        print("📊 PHASE 0: Analyzing site structure...")
        phase0_result = None
        try:
            phase0_result = await self.phase0_analyze_site_structure(url)
            print(f"\n📊 Phase 0 Results:")
            print(f"   CMS: {phase0_result.get('cms', 'Unknown')}")
            if phase0_result.get('url_patterns'):
                for pattern_type, urls in phase0_result['url_patterns'].items():
                    if urls:
                        print(f"   - {pattern_type.title()}: {len(urls)} URLs")
        except Exception as e:
            print(f"⚠️ Phase 0 error: {e}, continuing...")
            phase0_result = {}
        
        # ФАЗА 1: Map
        print("\n📍 PHASE 1: Intelligent discovery...")
        map_result = None
        try:
            map_result = await self.phase1_discover_structure(url, phase0_result=phase0_result)
            
            print(f"\n📊 Phase 1 Results:")
            print(f"   Total URLs: {map_result['total_urls']}")
            for category, urls in map_result['classified'].items():
                if urls:
                    print(f"   - {category.title()}: {len(urls)} pages")
        except Exception as e:
            print(f"⚠️ Phase 1 error: {e}, continuing with crawl...")
            map_result = {"total_urls": 0, "classified": {}}
        
        # Fallback: если Map не нашел URL, используем старый метод (2-phase semantic crawl)
        if map_result and map_result.get('total_urls', 0) == 0:
            print(f"\n⚠️ Map found 0 URLs, falling back to 2-phase semantic crawl method...")
            try:
                old_method_result = await self.analyze_care_home_website(url, care_home_name)
                # Конвертируем формат старого метода в формат нового
                if old_method_result:
                    return {
                        "care_home_name": care_home_name or old_method_result.get("care_home_name", ""),
                        "website_url": url,
                        "extraction_method": "2-phase-semantic-crawl-fallback",
                        "scraped_at": datetime.now().isoformat(),
                        "phase0_summary": {
                            "cms": "Unknown",
                            "url_patterns_found": 0
                        },
                        "map_summary": {
                            "total_urls_found": 0,
                            "classified_categories": {}
                        },
                        "crawl_summary": {
                            "pages_crawled": old_method_result.get("pages_analyzed", 0)
                        },
                        "structured_data": old_method_result.get("structured_data", {}),
                        "completeness": {
                            "staff": bool(old_method_result.get("structured_data", {}).get("staff")),
                            "facilities": bool(old_method_result.get("structured_data", {}).get("facilities")),
                            "services": bool(old_method_result.get("structured_data", {}).get("care_services")),
                            "pricing": bool(old_method_result.get("structured_data", {}).get("pricing")),
                            "activities": bool(old_method_result.get("structured_data", {}).get("activities")),
                            "contact": bool(old_method_result.get("structured_data", {}).get("contact")),
                            "nutrition": bool(old_method_result.get("structured_data", {}).get("nutrition")),
                            "reviews": bool(old_method_result.get("structured_data", {}).get("reviews")),
                            "awards": bool(old_method_result.get("structured_data", {}).get("awards")),
                            "safety": bool(old_method_result.get("structured_data", {}).get("safety")),
                            "transport": bool(old_method_result.get("structured_data", {}).get("transport")),
                            "media": bool(old_method_result.get("structured_data", {}).get("media")),
                            "policies": bool(old_method_result.get("structured_data", {}).get("policies")),
                            "events": bool(old_method_result.get("structured_data", {}).get("events")),
                            "faq": bool(old_method_result.get("structured_data", {}).get("faq")),
                            "about": bool(old_method_result.get("structured_data", {}).get("about"))
                        }
                    }
            except Exception as fallback_error:
                print(f"⚠️ Fallback method also failed: {fallback_error}, continuing with 4-phase...")
                import traceback
                traceback.print_exc()
                map_result = {"total_urls": 0, "classified": {}}
        
        # ФАЗА 2: Crawl
        print(f"\n🕷️ PHASE 2: Adaptive semantic crawling...")
        try:
            crawl_result = await self.phase2_semantic_crawl(
                url=url,
                classified_urls=map_result.get('classified', {}),
                phase0_result=phase0_result,
                map_result=map_result
            )
            
            print(f"\n📊 Phase 2 Results:")
            print(f"   Pages with content: {crawl_result['pages_crawled']}")
        except Exception as e:
            print(f"⚠️ Phase 2 error: {e}, using single page scrape...")
            crawl_result = {"pages_crawled": 0, "pages_data": []}
        
        # ФАЗА 3: Extract
        print(f"\n🔍 PHASE 3: AI extraction (Claude → Firecrawl → Regex)...")
        try:
            extracted_data = await self.phase3_extract_structured_data(
                pages_data=crawl_result.get('pages_data', []),
                care_home_name=care_home_name,
                url=url,
                use_claude=bool(self.anthropic_client),
                discovery_result={
                    "url_patterns": map_result.get('classified', {}),
                    "url_templates": map_result.get('url_templates', {}),
                    "ai_classifications": map_result.get('ai_classifications', {})
                }
            )
            
            print(f"\n📊 Phase 3 Results:")
            if isinstance(extracted_data, dict):
                categories = [
                    "staff", "facilities", "services", "pricing", "activities", "contact",
                    "nutrition", "reviews", "awards", "safety", "transport", "media",
                    "policies", "events", "faq", "about"
                ]
                filled_count = sum(1 for cat in categories if extracted_data.get(cat))
                print(f"   Categories filled: {filled_count}/{len(categories)}")
                
                # Показываем confidence если есть
                if extracted_data.get('extraction_confidence'):
                    print(f"   Extraction confidence: {extracted_data['extraction_confidence']}")
        except Exception as e:
            print(f"⚠️ Phase 3 error: {e}")
            extracted_data = {}
        
        # Валидация и очистка данных
        structured_data = self._validate_and_clean(
            extracted_data if isinstance(extracted_data, dict) else {},
            care_home_name,
            url
        )
        
        # Определяем метод извлечения
        extraction_method = "4-phase-universal-v2.5"
        if extracted_data.get('extraction_confidence'):
            extraction_method += f"-claude-confidence-{extracted_data.get('extraction_confidence', 0)}"
        
        return {
            "care_home_name": care_home_name or structured_data.get("care_home_name", ""),
            "website_url": url,
            "extraction_method": extraction_method,
            "scraped_at": datetime.now().isoformat(),
            "phase0_summary": {
                "cms": phase0_result.get('cms', 'Unknown') if phase0_result else 'Unknown',
                "url_patterns_found": len(phase0_result.get('url_patterns', {})) if phase0_result else 0
            },
            "map_summary": {
                "total_urls_found": map_result.get('total_urls', 0),
                "classified_categories": {k: len(v) for k, v in map_result.get('classified', {}).items()}
            },
            "crawl_summary": {
                "pages_crawled": crawl_result.get('pages_crawled', 0)
            },
            "structured_data": structured_data,
            "completeness": {
                "staff": self._has_real_data(structured_data.get("staff")),
                "facilities": self._has_real_data(structured_data.get("facilities")),
                "services": self._has_real_data(structured_data.get("care_services")),
                "pricing": self._has_real_data(structured_data.get("pricing")),
                "activities": self._has_real_data(structured_data.get("activities")),
                "contact": self._has_real_data(structured_data.get("contact")),
                "nutrition": self._has_real_data(structured_data.get("nutrition")),
                "reviews": self._has_real_data(structured_data.get("reviews")),
                "awards": self._has_real_data(structured_data.get("awards")),
                "safety": self._has_real_data(structured_data.get("safety")),
                "transport": self._has_real_data(structured_data.get("transport")),
                "media": self._has_real_data(structured_data.get("media")),
                "policies": self._has_real_data(structured_data.get("policies")),
                "events": self._has_real_data(structured_data.get("events")),
                "faq": self._has_real_data(structured_data.get("faq")),
                "about": self._has_real_data(structured_data.get("about"))
            }
        }
    
    def _has_real_data(self, value: Any) -> bool:
        """Проверяет наличие реальных данных в значении"""
        if value is None:
            return False
        if isinstance(value, dict):
            # Словарь считается пустым если все значения пустые
            return any(self._has_real_data(v) for v in value.values())
        if isinstance(value, list):
            # Список считается пустым если пустой или все элементы пустые
            return len(value) > 0 and any(self._has_real_data(v) for v in value)
        if isinstance(value, str):
            # Строка считается пустой если пустая или только пробелы
            return bool(value.strip())
        # Для других типов проверяем просто наличие
        return bool(value)
    
    def _validate_and_clean(
        self,
        data: Dict[str, Any],
        care_home_name: str,
        url: str
    ) -> Dict[str, Any]:
        """Валидация и очистка извлеченных данных"""
        if not data:
            return {}
        
        # Обязательные поля - если нет названия, используем переданное
        if not data.get('care_home_name'):
            data['care_home_name'] = care_home_name
        
        # Confidence threshold - фильтруем данные с очень низкой уверенностью
        confidence = data.get('extraction_confidence', 1.0)
        if confidence < 0.2:  # Слишком низкая уверенность
            print(f"   ⚠️ Low confidence ({confidence}), applying basic validation only")
        
        # Очистка контактной информации
        if data.get('contact'):
            contact = data['contact']
            
            # Телефон - форматирование (удаляем пробелы, скобки, дефисы)
            if contact.get('phone'):
                phone = re.sub(r'[\s\(\)\-]', '', contact['phone'])
                contact['phone'] = phone
            
            # Email - lowercase
            if contact.get('email'):
                contact['email'] = contact['email'].lower()
            
            # URL - ensure full URL
            if contact.get('website') and not contact['website'].startswith('http'):
                contact['website'] = f"https://{contact['website']}"
        
        # Очистка названия
        if data.get('care_home_name'):
            name = data['care_home_name']
            # Удаляем префиксы "Welcome to", "About"
            name = re.sub(r'^(Welcome to|About)\s+', '', name, flags=re.I)
            # Удаляем суффиксы "Care Home", "Nursing Home"
            name = re.sub(r'\s+(Care Home|Nursing Home|Residential Home).*$', '', name, flags=re.I)
            data['care_home_name'] = name.strip()
        
        # Валидация массивов - удаляем пустые элементы
        for key, value in list(data.items()):
            if isinstance(value, list):
                cleaned = [v for v in value if v and (isinstance(v, str) and v.strip() or not isinstance(v, str))]
                data[key] = cleaned
                # Если список стал пустым, удаляем ключ
                if not cleaned:
                    del data[key]
            elif isinstance(value, dict):
                # Рекурсивная очистка вложенных словарей
                cleaned_dict = {}
                for sub_key, sub_value in value.items():
                    if isinstance(sub_value, list):
                        cleaned_list = [v for v in sub_value if v and (isinstance(v, str) and v.strip() or not isinstance(v, str))]
                        if cleaned_list:
                            cleaned_dict[sub_key] = cleaned_list
                    elif isinstance(sub_value, str):
                        if sub_value.strip():
                            cleaned_dict[sub_key] = sub_value
                    elif sub_value:  # Для других типов
                        cleaned_dict[sub_key] = sub_value
                
                # Если словарь стал пустым, удаляем ключ
                if cleaned_dict:
                    data[key] = cleaned_dict
                else:
                    del data[key]
            elif isinstance(value, str):
                # Если строка пустая, удаляем ключ
                if not value.strip():
                    del data[key]
        
        return data
    
    def _filter_detail_pages(
        self,
        pages: List[Dict],
        discovery_result: Dict
    ) -> List[Dict]:
        """Фильтрация только detail pages"""
        filtered = []
        
        url_patterns = discovery_result.get('url_patterns', {})
        url_templates = discovery_result.get('url_templates', {})
        ai_classifications = discovery_result.get('ai_classifications', {})
        
        detail_urls = []
        for category in ['detail', 'about']:
            if category in url_patterns:
                detail_urls.extend([str(u) for u in url_patterns[category]])
        
        for page in pages:
            page_url = page.get('metadata', {}).get('sourceURL', '') or page.get('url', '')
            if not page_url:
                continue
            
            # Метод 1: Прямое совпадение с обнаруженными detail URLs
            if page_url in detail_urls:
                filtered.append(page)
                continue
            
            # Метод 2: AI-классификация
            if page_url in ai_classifications:
                page_type = ai_classifications[page_url]
                if page_type == 'care_home_detail':
                    filtered.append(page)
                    continue
            
            # Метод 3: Совпадение с шаблоном
            if url_templates:
                template_match = URLPatternRecognizer.match_url_to_template(page_url, url_templates)
                if template_match:
                    filtered.append(page)
                    continue
            
            # Метод 4: Эвристика - глубокие URL с конкретным содержимым
            content = page.get('markdown', '') or page.get('html', '')
            if content:
                # Используем regex extractor для проверки
                phones = re.findall(r'\b0\d{4}\s?\d{6}\b|\b0\d{2,3}\s?\d{4}\s?\d{4}\b', content)
                postcodes = re.findall(r'\b[A-Z]{1,2}\d{1,2}\s?\d[A-Z]{2}\b', content)
                
                if phones and postcodes:
                    filtered.append(page)
        
        return filtered
    
    def _templates_to_regex(self, templates: Dict) -> List[str]:
        """Преобразование URL templates в regex паттерны для includePaths"""
        regex_patterns = []
        
        for template_name, template_data in templates.items():
            template = template_data.get('template', '')
            
            # /care-homes/{slug}/ -> ^/care-homes/[a-z0-9\-]+/$
            regex = template.replace('{slug}', '[a-z0-9\\-]+')
            regex = regex.replace('{id}', '\\d+')
            regex = '^' + regex + '$'
            
            regex_patterns.append(regex)
        
        return regex_patterns
    
    def _select_start_urls(self, url_patterns: Dict, base_url: str) -> List[str]:
        """Выбор оптимальных стартовых URL для crawl"""
        start_urls = []
        
        # Приоритет 1: Homepage
        start_urls.append(base_url)
        
        # Приоритет 2: Listing pages
        if url_patterns.get("listings"):
            start_urls.extend([str(u) for u in url_patterns["listings"][:2]])
        
        # Приоритет 3: Regional pages
        if url_patterns.get("regional"):
            start_urls.extend([str(u) for u in url_patterns["regional"][:2]])
        
        return start_urls[:3]  # Максимум 3 стартовые точки
    
    def _generate_adaptive_prompt(
        self,
        phase0_result: Optional[Dict],
        classified_urls: Dict[str, List[str]]
    ) -> str:
        """Генерация адаптивного prompt на основе анализа сайта"""
        prompt_parts = [
            "Extract content from pages about:",
            "- Staff qualifications, team members, care professionals, management",
            "- Facilities: rooms, gardens, communal areas, equipment, accessibility",
            "- Care services: types of care, specializations, medical support",
            "- Pricing: fees, costs, funding options, additional charges",
            "- Activities: daily programs, therapies, events, entertainment",
            "- Contact information, visiting hours, location, directions",
            "- Nutrition and dining: menus, meal times, dietary options",
            "- Reviews and testimonials: client feedback, family reviews",
            "- Awards and accreditations: certifications, recognitions",
            "- Safety and security: safeguarding, emergency procedures",
            "- Transportation: parking, access, public transport",
            "- Media: photos, videos, virtual tours, galleries",
            "- Policies: procedures, terms, complaints process",
            "- Events and news: announcements, updates, blog posts",
            "- FAQ: frequently asked questions, guides"
        ]
        
        # Адаптация на основе Фазы 0
        if phase0_result:
            url_patterns = phase0_result.get("url_patterns", {})
            cms = phase0_result.get("cms", "")
            
            if url_patterns.get("detail"):
                prompt_parts.append("\nFocus on individual care home detail pages with comprehensive information.")
            
            if url_patterns.get("listings"):
                prompt_parts.append("Include directory pages listing multiple care homes.")
            
            if url_patterns.get("regional"):
                prompt_parts.append("Include regional pages showing care homes by location.")
            
            # Адаптация под CMS
            if cms == "WordPress":
                prompt_parts.append("\nNote: This is a WordPress site. Look for standard WordPress content structure.")
            elif cms == "Wix":
                prompt_parts.append("\nNote: This is a Wix site. Content may load dynamically via JavaScript.")
        
        prompt_parts.append(
            "\nPrioritize pages with detailed information.\n"
            "Exclude: job vacancies, cookie policy (unless relevant), generic legal pages."
        )
        
        return "\n".join(prompt_parts)
    
    async def extract_care_home_data_full(
        self,
        url: str,
        care_home_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Full 3-phase extraction method
        Uses Map -> Crawl -> Extract approach for maximum data extraction
        """
        return await self.extract_care_home_complete(url, care_home_name or "Unknown")
    
    async def extract_dementia_care_quality(
        self,
        url: str,
        care_home_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Extract and evaluate dementia care quality from care home website
        
        Uses semantic scraping to analyze:
        1. Specialist dementia team credentials
        2. Dementia care unit design features
        3. Activity programs for dementia residents
        4. Family involvement in care planning
        5. Staff-to-resident ratio in dementia unit
        6. Behavioral support approach
        7. End-of-life dementia care approach
        
        Returns quality score (1-10) with detailed reasoning
        """
        print(f"\n🧠 DEMENTIA CARE QUALITY ANALYSIS")
        print(f"🏥 Analyzing: {care_home_name or 'Unknown'}")
        print(f"🌐 URL: {url}\n")
        
        # Ensure URL has protocol
        if not url.startswith("http"):
            url = f"https://{url}"
        
        # Use scrape with extraction prompt for dementia care analysis
        extraction_prompt = """
        Analyze the dementia care program at this care home.
        Extract and evaluate:
        
        1. Specialist dementia team credentials:
           - RGN (Registered General Nurse) qualifications
           - Dementia Care Certificate holders
           - Specialist dementia training programs
           - Years of experience in dementia care
        
        2. Dementia care unit design features:
           - Layout (secure, easy navigation)
           - Security features (door alarms, safe gardens)
           - Sensory design (lighting, colors, textures)
           - Memory aids and wayfinding
           - Quiet spaces and activity areas
        
        3. Activity programs specifically for dementia residents:
           - Reminiscence therapy
           - Music therapy
           - Art and craft activities
           - Physical activities adapted for dementia
           - Social interaction programs
        
        4. Family involvement in care planning:
           - Family meetings frequency
           - Care plan reviews with families
           - Open visiting hours
           - Family support groups
        
        5. Staff-to-resident ratio in dementia unit:
           - Number of staff per resident
           - 24/7 nursing coverage
           - Specialist dementia staff availability
        
        6. Behavioral support approach:
           - De-escalation training
           - Person-centered approach
           - Non-pharmacological interventions
           - Handling of challenging behaviors
        
        7. End-of-life dementia care approach:
           - Palliative care for dementia
           - Family support during end-of-life
           - Dignity and comfort focus
        
        Rate overall dementia care quality: 1-10
        Explain rating reasoning in detail.
        Provide specific evidence from the website for each evaluation point.
        """
        
        try:
            # First, scrape the URL to get markdown content
            scrape_result = await self.scrape_url(
                url=url,
                formats=[{"type": "markdown"}],
                only_main_content=True
            )
            
            # Extract markdown content
            markdown_content = ""
            if isinstance(scrape_result, dict):
                if 'markdown' in scrape_result:
                    markdown_content = scrape_result['markdown']
                elif 'content' in scrape_result:
                    markdown_content = scrape_result['content']
                elif 'data' in scrape_result:
                    if isinstance(scrape_result['data'], dict):
                        markdown_content = scrape_result['data'].get('markdown', '') or scrape_result['data'].get('content', '')
                    else:
                        markdown_content = str(scrape_result['data'])
                else:
                    # Try to get markdown from any text field
                    for key in ['text', 'html', 'raw']:
                        if key in scrape_result:
                            markdown_content = str(scrape_result[key])
                            break
            
            # Try to use Firecrawl extract endpoint for structured extraction (works without Claude)
            if markdown_content:
                try:
                    # Use Firecrawl extract endpoint with schema for structured extraction
                    extraction_schema = {
                        "type": "object",
                        "properties": {
                            "dementia_care_quality_score": {
                                "type": "number",
                                "description": "Overall dementia care quality score from 1-10"
                            },
                            "rating_reasoning": {
                                "type": "string",
                                "description": "Detailed explanation of the quality score"
                            },
                            "specialist_team": {
                                "type": "object",
                                "properties": {
                                    "score": {"type": "number"},
                                    "details": {"type": "string"},
                                    "strengths": {"type": "array", "items": {"type": "string"}},
                                    "gaps": {"type": "array", "items": {"type": "string"}}
                                }
                            },
                            "unit_design": {
                                "type": "object",
                                "properties": {
                                    "score": {"type": "number"},
                                    "details": {"type": "string"},
                                    "strengths": {"type": "array", "items": {"type": "string"}},
                                    "gaps": {"type": "array", "items": {"type": "string"}}
                                }
                            },
                            "activity_programs": {
                                "type": "object",
                                "properties": {
                                    "score": {"type": "number"},
                                    "details": {"type": "string"},
                                    "programs_mentioned": {"type": "array", "items": {"type": "string"}}
                                }
                            },
                            "family_involvement": {
                                "type": "object",
                                "properties": {
                                    "score": {"type": "number"},
                                    "details": {"type": "string"}
                                }
                            },
                            "staff_ratio": {
                                "type": "object",
                                "properties": {
                                    "score": {"type": "number"},
                                    "details": {"type": "string"}
                                }
                            },
                            "behavioral_support": {
                                "type": "object",
                                "properties": {
                                    "score": {"type": "number"},
                                    "details": {"type": "string"}
                                }
                            },
                            "end_of_life_care": {
                                "type": "object",
                                "properties": {
                                    "score": {"type": "number"},
                                    "details": {"type": "string"}
                                }
                            },
                            "overall_assessment": {"type": "string"},
                            "recommendations": {"type": "array", "items": {"type": "string"}}
                        }
                    }
                    
                    extract_result = await self.extract(
                        urls=[url],
                        prompt=extraction_prompt,
                        schema=extraction_schema,
                        extraction_type="llm-extraction"
                    )
                    
                    # Extract structured data from Firecrawl response
                    if extract_result and isinstance(extract_result, dict):
                        # Firecrawl extract returns data in different formats
                        extracted_data = None
                        if "data" in extract_result:
                            if isinstance(extract_result["data"], list) and len(extract_result["data"]) > 0:
                                extracted_data = extract_result["data"][0]
                            elif isinstance(extract_result["data"], dict):
                                extracted_data = extract_result["data"]
                        elif "extracted" in extract_result:
                            extracted_data = extract_result["extracted"]
                        else:
                            extracted_data = extract_result
                        
                        if extracted_data and isinstance(extracted_data, dict):
                            return {
                                "care_home_name": care_home_name or "Unknown",
                                "website_url": url,
                                "analysis_type": "dementia_care_quality",
                                "scraped_at": datetime.now().isoformat(),
                                "dementia_care_analysis": extracted_data,
                                "raw_content": markdown_content[:1000],
                                "extraction_method": "firecrawl-extract-structured"
                            }
                    
                except Exception as extract_error:
                    print(f"⚠️ Firecrawl extract error: {extract_error}, trying Claude or fallback")
            
            # If we have Anthropic client, use it for structured analysis
            if self.anthropic_client and markdown_content:
                try:
                    # Limit content to avoid token limits (8000 chars)
                    limited_content = markdown_content[:8000] if len(markdown_content) > 8000 else markdown_content
                    
                    analysis_prompt_text = f"""
                    Based on this dementia care information extracted from a care home website:
                    
                    {limited_content}
                    
                    Provide a structured analysis in JSON format:
                    {{
                        "dementia_care_quality_score": <number 1-10>,
                        "rating_reasoning": "<detailed explanation>",
                        "specialist_team": {{
                            "score": <1-10>,
                            "details": "<what was found>",
                            "strengths": ["<strength1>", "<strength2>"],
                            "gaps": ["<gap1>", "<gap2>"]
                        }},
                        "unit_design": {{
                            "score": <1-10>,
                            "details": "<what was found>",
                            "strengths": ["<strength1>"],
                            "gaps": ["<gap1>"]
                        }},
                        "activity_programs": {{
                            "score": <1-10>,
                            "details": "<what was found>",
                            "programs_mentioned": ["<program1>", "<program2>"]
                        }},
                        "family_involvement": {{
                            "score": <1-10>,
                            "details": "<what was found>"
                        }},
                        "staff_ratio": {{
                            "score": <1-10>,
                            "details": "<what was found or inferred>"
                        }},
                        "behavioral_support": {{
                            "score": <1-10>,
                            "details": "<what was found>"
                        }},
                        "end_of_life_care": {{
                            "score": <1-10>,
                            "details": "<what was found>"
                        }},
                        "overall_assessment": "<summary>",
                        "recommendations": ["<rec1>", "<rec2>"]
                    }}
                    """
                    
                    response = await self.anthropic_client.messages.create(
                        model="claude-3-5-sonnet-20241022",
                        max_tokens=2000,
                        messages=[{
                            "role": "user",
                            "content": analysis_prompt_text
                        }]
                    )
                    
                    analysis_text = response.content[0].text
                    
                    # Try to extract JSON from response
                    import json
                    import re
                    
                    # Look for JSON in the response
                    json_match = re.search(r'\{.*\}', analysis_text, re.DOTALL)
                    if json_match:
                        try:
                            analysis_json = json.loads(json_match.group(0))
                            return {
                                "care_home_name": care_home_name or "Unknown",
                                "website_url": url,
                                "analysis_type": "dementia_care_quality",
                                "scraped_at": datetime.now().isoformat(),
                                "dementia_care_analysis": analysis_json,
                                "raw_content": markdown_content[:1000],  # First 1000 chars
                                "extraction_method": "firecrawl-semantic-claude-analysis"
                            }
                        except json.JSONDecodeError:
                            pass
                    
                    # If JSON extraction failed, return text analysis
                    return {
                        "care_home_name": care_home_name or "Unknown",
                        "website_url": url,
                        "analysis_type": "dementia_care_quality",
                        "scraped_at": datetime.now().isoformat(),
                        "dementia_care_analysis": {
                            "analysis_text": analysis_text,
                            "raw_content": markdown_content[:1000]
                        },
                        "extraction_method": "firecrawl-semantic-claude-text"
                    }
                    
                except Exception as claude_error:
                    print(f"⚠️ Claude analysis error: {claude_error}, using basic analysis")
            
            # Fallback: Basic analysis without AI (keyword-based)
            if not markdown_content:
                raise Exception("No content extracted from website. The website may be inaccessible or have no relevant content.")
            
            # Perform basic keyword-based analysis
            content_lower = markdown_content.lower()
            
            # Search for dementia-related keywords
            dementia_keywords = {
                "specialist_team": ["dementia", "specialist", "trained", "qualified", "certificate", "rgn", "nurse"],
                "unit_design": ["secure", "safe", "garden", "sensory", "memory", "wayfinding", "layout"],
                "activity_programs": ["reminiscence", "music therapy", "art", "activities", "therapy", "program"],
                "family_involvement": ["family", "visiting", "meetings", "care plan", "involvement"],
                "behavioral_support": ["behavior", "de-escalation", "person-centered", "challenging"],
                "end_of_life_care": ["palliative", "end of life", "hospice", "dignity"]
            }
            
            # Determine if Claude was attempted but failed, or not available
            claude_available = bool(self.anthropic_client)
            if claude_available:
                reasoning_msg = "Basic keyword analysis performed. Claude AI analysis was attempted but encountered an error. Using keyword-based fallback."
                assessment_msg = "Basic analysis completed using keyword matching. Claude AI analysis unavailable due to processing error."
                recommendations_list = [
                    "Review website content manually for dementia care specifics",
                    "Contact care home directly for detailed information about dementia care programs",
                    "Retry analysis - Claude AI may be temporarily unavailable"
                ]
            else:
                reasoning_msg = "Basic keyword analysis performed. For detailed AI analysis, configure Anthropic Claude API key in config.json."
                assessment_msg = "Basic analysis completed. Website content extracted but detailed AI analysis unavailable. Configure Claude API key for comprehensive analysis."
                recommendations_list = [
                    "Configure Anthropic Claude API key for detailed structured analysis",
                    "Review website content manually for dementia care specifics",
                    "Contact care home directly for detailed information about dementia care programs"
                ]
            
            basic_analysis = {
                "dementia_care_quality_score": 5,  # Default neutral score
                "rating_reasoning": reasoning_msg,
                "specialist_team": {
                    "score": 5,
                    "details": "Keyword analysis: " + str(sum(1 for kw in dementia_keywords["specialist_team"] if kw in content_lower)) + " relevant terms found",
                    "strengths": [],
                    "gaps": []
                },
                "unit_design": {
                    "score": 5,
                    "details": "Keyword analysis: " + str(sum(1 for kw in dementia_keywords["unit_design"] if kw in content_lower)) + " relevant terms found",
                    "strengths": [],
                    "gaps": []
                },
                "activity_programs": {
                    "score": 5,
                    "details": "Keyword analysis: " + str(sum(1 for kw in dementia_keywords["activity_programs"] if kw in content_lower)) + " relevant terms found",
                    "programs_mentioned": []
                },
                "family_involvement": {
                    "score": 5,
                    "details": "Keyword analysis: " + str(sum(1 for kw in dementia_keywords["family_involvement"] if kw in content_lower)) + " relevant terms found"
                },
                "staff_ratio": {
                    "score": 5,
                    "details": "No specific information found about staff-to-resident ratios"
                },
                "behavioral_support": {
                    "score": 5,
                    "details": "Keyword analysis: " + str(sum(1 for kw in dementia_keywords["behavioral_support"] if kw in content_lower)) + " relevant terms found"
                },
                "end_of_life_care": {
                    "score": 5,
                    "details": "Keyword analysis: " + str(sum(1 for kw in dementia_keywords["end_of_life_care"] if kw in content_lower)) + " relevant terms found"
                },
                "overall_assessment": assessment_msg,
                "recommendations": recommendations_list
            }
            
            # Adjust scores based on keyword matches
            total_keywords_found = sum(
                sum(1 for kw in keywords if kw in content_lower)
                for keywords in dementia_keywords.values()
            )
            
            if total_keywords_found > 10:
                basic_analysis["dementia_care_quality_score"] = 7
                basic_analysis["rating_reasoning"] = f"Found {total_keywords_found} dementia-related keywords. Suggests good coverage of dementia care topics."
            elif total_keywords_found > 5:
                basic_analysis["dementia_care_quality_score"] = 6
                basic_analysis["rating_reasoning"] = f"Found {total_keywords_found} dementia-related keywords. Moderate coverage."
            elif total_keywords_found > 0:
                basic_analysis["dementia_care_quality_score"] = 4
                basic_analysis["rating_reasoning"] = f"Found only {total_keywords_found} dementia-related keywords. Limited information available."
            else:
                basic_analysis["dementia_care_quality_score"] = 3
                basic_analysis["rating_reasoning"] = "No dementia-specific keywords found. May not specialize in dementia care or information not clearly presented."
            
            return {
                "care_home_name": care_home_name or "Unknown",
                "website_url": url,
                "analysis_type": "dementia_care_quality",
                "scraped_at": datetime.now().isoformat(),
                "dementia_care_analysis": basic_analysis,
                "raw_content": markdown_content[:2000] if len(markdown_content) > 2000 else markdown_content,
                "extraction_method": "firecrawl-semantic-basic-keyword-analysis"
            }
            
        except Exception as e:
            print(f"❌ Dementia care analysis error: {e}")
            import traceback
            traceback.print_exc()
            error_msg = str(e)
            # Make error message more user-friendly
            if "No content extracted" in error_msg:
                raise Exception("Could not extract content from the website. Please check if the URL is correct and accessible.")
            elif "timeout" in error_msg.lower() or "timed out" in error_msg.lower():
                raise Exception("Request timed out. The website may be too large or slow. Please try again.")
            else:
                raise Exception(f"Dementia care analysis failed: {error_msg}")
    
    async def extract_pricing(
        self,
        url: str,
        care_home_name: Optional[str] = None,
        postcode: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Extract pricing information from care home website using Firecrawl + Claude AI
        
        Returns structured pricing data:
        - fee_residential_from/to
        - fee_nursing_from/to
        - fee_dementia_residential_from/to
        - fee_dementia_nursing_from/to
        - fee_respite_from/to
        - pricing_notes
        - pricing_confidence
        """
        print(f"\n💰 PRICING EXTRACTION")
        print(f"🏥 Analyzing: {care_home_name or 'Unknown'}")
        print(f"🌐 URL: {url}")
        if postcode:
            print(f"📮 Postcode: {postcode}\n")
        
        # Ensure URL has protocol
        if not url.startswith("http"):
            url = f"https://{url}"
        
        # Pricing extraction schema (enhanced with pricing_breakdown)
        pricing_schema = {
            "type": "object",
            "properties": {
                "fee_residential_from": {
                    "type": ["number", "null"],
                    "description": "Weekly residential care fee from (minimum) in GBP"
                },
                "fee_residential_to": {
                    "type": ["number", "null"],
                    "description": "Weekly residential care fee to (maximum) in GBP"
                },
                "fee_nursing_from": {
                    "type": ["number", "null"],
                    "description": "Weekly nursing care fee from (minimum) in GBP. Must be >= residential if both exist."
                },
                "fee_nursing_to": {
                    "type": ["number", "null"],
                    "description": "Weekly nursing care fee to (maximum) in GBP"
                },
                "fee_dementia_residential_from": {
                    "type": ["number", "null"],
                    "description": "Weekly dementia residential care fee from in GBP"
                },
                "fee_dementia_residential_to": {
                    "type": ["number", "null"],
                    "description": "Weekly dementia residential care fee to in GBP"
                },
                "fee_dementia_nursing_from": {
                    "type": ["number", "null"],
                    "description": "Weekly dementia nursing care fee from in GBP. Must be >= standard nursing if both exist."
                },
                "fee_dementia_nursing_to": {
                    "type": ["number", "null"],
                    "description": "Weekly dementia nursing care fee to in GBP"
                },
                "fee_respite_from": {
                    "type": ["number", "null"],
                    "description": "Weekly respite care fee from in GBP"
                },
                "fee_respite_to": {
                    "type": ["number", "null"],
                    "description": "Weekly respite care fee to in GBP"
                },
                "pricing_breakdown": {
                    "type": "object",
                    "properties": {
                        "meals_included": {
                            "type": ["boolean", "null"],
                            "description": "Whether meals are included in base price"
                        },
                        "activities_included": {
                            "type": ["boolean", "null"],
                            "description": "Whether activities are included in base price"
                        },
                        "activities_cost": {
                            "type": ["number", "null"],
                            "description": "Additional cost for activities per week if not included"
                        },
                        "transport_included": {
                            "type": ["boolean", "null"],
                            "description": "Whether transport is included"
                        },
                        "transport_cost": {
                            "type": ["number", "null"],
                            "description": "Additional cost for transport per week if not included"
                        },
                        "additional_services": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of additional paid services (e.g., Physiotherapy, Podiatry, Hairdressing)"
                        }
                    }
                },
                "pricing_notes": {
                    "type": "string",
                    "description": "Special conditions, notes, or additional information about pricing"
                },
                "pricing_confidence": {
                    "type": "number",
                    "description": "Confidence score 0-100: 90-100 = explicitly stated, 70-89 = clearly calculable, <70 = uncertain"
                },
                "currency": {
                    "type": "string",
                    "description": "Currency code (default: GBP)",
                    "default": "GBP"
                },
                "billing_period": {
                    "type": "string",
                    "description": "Billing period (default: weekly)",
                    "default": "weekly"
                }
            }
        }
        
        extraction_prompt = f"""Extract ALL pricing information from this care home website.

Care Home: {care_home_name or 'Unknown'}
Postcode: {postcode or 'Not provided'}

REQUIRED: Extract ONLY if explicitly stated. DO NOT estimate or assume prices.

Look for pricing information in:
- "Fees" or "Pricing" page
- "How much does it cost?" section
- Pricing tables or fee schedules
- "Cost" or "Rates" pages
- Contact page pricing information

Extract:
1. Residential care weekly fees (from/to range)
2. Nursing care weekly fees (from/to range)
3. Dementia residential care weekly fees (from/to range)
4. Dementia nursing care weekly fees (from/to range)
5. Respite care weekly fees (from/to range)
6. What's included in fees (meals, activities, transport)
7. Additional costs (activities, transport, services)
8. Special notes or conditions

CRITICAL RULES:
- Extract ONLY numbers (no £ symbol, no commas, no text)
- Extract WEEKLY prices only (not monthly or annual)
- If single price given (e.g., "£1,200 per week"), use it for both "from" and "to"
- If pricing is not found, use null (NOT 0)
- Nursing fees MUST be >= Residential fees (if both exist)
- Dementia fees MUST be >= Standard care fees (if both exist)
- Confidence scoring:
  * 90-100: Prices explicitly stated on dedicated pricing page
  * 70-89: Prices clearly calculable from stated information
  * 50-69: Prices mentioned but unclear or incomplete
  * <50: Uncertain or estimated

Return structured JSON with all pricing fields."""
        
        try:
            # First, scrape the URL to get markdown content
            scrape_result = await self.scrape_url(
                url=url,
                formats=[{"type": "markdown"}],
                only_main_content=True
            )
            
            # Extract markdown content
            markdown_content = ""
            if isinstance(scrape_result, dict):
                if 'markdown' in scrape_result:
                    markdown_content = scrape_result['markdown']
                elif 'content' in scrape_result:
                    markdown_content = scrape_result['content']
                elif 'data' in scrape_result:
                    if isinstance(scrape_result['data'], dict):
                        markdown_content = scrape_result['data'].get('markdown', '') or scrape_result['data'].get('content', '')
                    else:
                        markdown_content = str(scrape_result['data'])
            
            if not markdown_content:
                raise Exception("No content extracted from website")
            
            # Try Firecrawl extract endpoint first
            try:
                extract_result = await self.extract(
                    urls=[url],
                    prompt=extraction_prompt,
                    schema=pricing_schema,
                    extraction_type="llm-extraction"
                )
                
                if extract_result and isinstance(extract_result, dict):
                    extracted_data = None
                    if "data" in extract_result:
                        if isinstance(extract_result["data"], list) and len(extract_result["data"]) > 0:
                            extracted_data = extract_result["data"][0]
                        elif isinstance(extract_result["data"], dict):
                            extracted_data = extract_result["data"]
                    elif "extracted" in extract_result:
                        extracted_data = extract_result["extracted"]
                    else:
                        extracted_data = extract_result
                    
                    if extracted_data and isinstance(extracted_data, dict) and (extracted_data.get("fee_residential_from") or extracted_data.get("fee_nursing_from")):
                        # Validate pricing relationships
                        extracted_data = self._validate_pricing_data(extracted_data)
                        
                        return {
                            "care_home_name": care_home_name or "Unknown",
                            "website_url": url,
                            "postcode": postcode,
                            "extraction_method": "firecrawl-extract-structured",
                            "scraped_at": datetime.now().isoformat(),
                            "pricing": extracted_data
                        }
            except Exception as extract_error:
                print(f"⚠️ Firecrawl extract error: {extract_error}, trying Claude analysis")
            
            # If we have Anthropic client, use it for structured analysis
            if self.anthropic_client and markdown_content:
                try:
                    # Limit content to avoid token limits (12000 chars for pricing)
                    limited_content = markdown_content[:12000] if len(markdown_content) > 12000 else markdown_content
                    
                    analysis_prompt_text = f"""Extract pricing information from this care home website content:

{limited_content}

Care Home: {care_home_name or 'Unknown'}
Postcode: {postcode or 'Not provided'}

Extract ALL pricing information and return as JSON:
{{
  "fee_residential_from": <number or null>,
  "fee_residential_to": <number or null>,
  "fee_nursing_from": <number or null>,
  "fee_nursing_to": <number or null>,
  "fee_dementia_residential_from": <number or null>,
  "fee_dementia_residential_to": <number or null>,
  "fee_dementia_nursing_from": <number or null>,
  "fee_dementia_nursing_to": <number or null>,
  "fee_respite_from": <number or null>,
  "fee_respite_to": <number or null>,
  "pricing_breakdown": {{
    "meals_included": <boolean or null>,
    "activities_included": <boolean or null>,
    "activities_cost": <number or null>,
    "transport_included": <boolean or null>,
    "transport_cost": <number or null>,
    "additional_services": ["<service1>", "<service2>"]
  }},
  "pricing_notes": "<any notes about pricing, conditions, or additional fees>",
  "pricing_confidence": <0-100>,
  "currency": "GBP",
  "billing_period": "weekly"
}}

CRITICAL RULES:
- Extract ONLY actual numbers found (no £, no commas, no text)
- Extract WEEKLY prices only (convert monthly/annual if needed: monthly/4.33, annual/52)
- If single price mentioned, use for both "from" and "to"
- If not found, use null (NOT 0)
- Validate: nursing >= residential, dementia >= standard
- Confidence: 90-100 = explicit, 70-89 = calculable, <70 = uncertain
- Include what's covered (meals, activities) and additional costs"""
                    
                    response = await self.anthropic_client.messages.create(
                        model="claude-3-5-sonnet-20241022",
                        max_tokens=1000,
                        messages=[{
                            "role": "user",
                            "content": analysis_prompt_text
                        }]
                    )
                    
                    analysis_text = response.content[0].text
                    
                    # Try to extract JSON from response
                    json_match = re.search(r'\{.*\}', analysis_text, re.DOTALL)
                    if json_match:
                        try:
                            pricing_json = json.loads(json_match.group(0))
                            
                            # Ensure pricing_breakdown structure exists
                            if "pricing_breakdown" not in pricing_json:
                                pricing_json["pricing_breakdown"] = {}
                            
                            # Ensure currency and billing_period
                            if "currency" not in pricing_json:
                                pricing_json["currency"] = "GBP"
                            if "billing_period" not in pricing_json:
                                pricing_json["billing_period"] = "weekly"
                            
                            # Validate pricing relationships
                            pricing_json = self._validate_pricing_data(pricing_json)
                            
                            return {
                                "care_home_name": care_home_name or "Unknown",
                                "website_url": url,
                                "postcode": postcode,
                                "extraction_method": "firecrawl-semantic-claude-analysis",
                                "scraped_at": datetime.now().isoformat(),
                                "pricing": pricing_json
                            }
                        except json.JSONDecodeError as e:
                            print(f"⚠️ JSON decode error: {e}")
                            pass
                    
                except Exception as claude_error:
                    print(f"⚠️ Claude analysis error: {claude_error}")
            
            # Fallback: Basic regex extraction
            content_lower = markdown_content.lower()
            pricing_data = {}
            
            # Try to extract prices using regex patterns
            price_patterns = {
                "residential": r"residential[^\d]*(\d{3,5})",
                "nursing": r"nursing[^\d]*(\d{3,5})",
                "dementia": r"dementia[^\d]*(\d{3,5})",
            }
            
            for key, pattern in price_patterns.items():
                matches = re.findall(pattern, content_lower)
                if matches:
                    prices = [int(m) for m in matches if m.isdigit()]
                    if prices:
                        pricing_data[f"fee_{key}_from"] = min(prices)
                        pricing_data[f"fee_{key}_to"] = max(prices)
            
            # Set confidence based on how much we found
            found_fields = sum(1 for k in pricing_data.keys() if pricing_data.get(k) is not None and 'confidence' not in k)
            pricing_data["pricing_confidence"] = min(100, found_fields * 15)  # Rough estimate
            pricing_data["currency"] = "GBP"
            pricing_data["billing_period"] = "weekly"
            
            # Validate pricing relationships
            pricing_data = self._validate_pricing_data(pricing_data)
            
            return {
                "care_home_name": care_home_name or "Unknown",
                "website_url": url,
                "postcode": postcode,
                "extraction_method": "firecrawl-regex-fallback",
                "scraped_at": datetime.now().isoformat(),
                "pricing": pricing_data
            }
            
        except Exception as e:
            print(f"❌ Pricing extraction error: {e}")
            import traceback
            traceback.print_exc()
            raise Exception(f"Failed to extract pricing: {str(e)}")
    
    def _validate_pricing_data(self, pricing_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate pricing data relationships and reasonable values:
        - Nursing >= Residential
        - Dementia >= Standard care
        - Ensure currency and billing_period are set
        - Filter unrealistic prices (too high or too low)
        """
        validated = pricing_data.copy()
        
        # Ensure currency and billing_period
        if "currency" not in validated:
            validated["currency"] = "GBP"
        if "billing_period" not in validated:
            validated["billing_period"] = "weekly"
        
        # Reasonable price ranges for UK care homes (weekly in GBP)
        MIN_PRICE = 300  # Minimum reasonable weekly fee
        MAX_PRICE = 4000  # Maximum reasonable weekly fee (premium care homes)
        
        def validate_price_range(value: Optional[float], field_name: str) -> Optional[float]:
            """Validate and filter unrealistic prices"""
            if value is None:
                return None
            
            if value < MIN_PRICE:
                print(f"⚠️ Warning: {field_name} ({value}) is below minimum ({MIN_PRICE}). Filtering out.")
                return None
            
            if value > MAX_PRICE:
                print(f"⚠️ Warning: {field_name} ({value}) exceeds maximum ({MAX_PRICE}). Filtering out.")
                return None
            
            return value
        
        # Validate all price fields
        price_fields = [
            "fee_residential_from", "fee_residential_to",
            "fee_nursing_from", "fee_nursing_to",
            "fee_dementia_residential_from", "fee_dementia_residential_to",
            "fee_dementia_nursing_from", "fee_dementia_nursing_to",
            "fee_respite_from", "fee_respite_to"
        ]
        
        for field in price_fields:
            if field in validated:
                validated[field] = validate_price_range(validated[field], field)
        
        # Validate: from <= to for each category
        def validate_range(from_val: Optional[float], to_val: Optional[float], category: str):
            """Ensure from <= to"""
            if from_val is not None and to_val is not None:
                if from_val > to_val:
                    print(f"⚠️ Warning: {category} from ({from_val}) > to ({to_val}). Swapping.")
                    return to_val, from_val
            return from_val, to_val
        
        validated["fee_residential_from"], validated["fee_residential_to"] = validate_range(
            validated.get("fee_residential_from"), validated.get("fee_residential_to"), "Residential"
        )
        validated["fee_nursing_from"], validated["fee_nursing_to"] = validate_range(
            validated.get("fee_nursing_from"), validated.get("fee_nursing_to"), "Nursing"
        )
        validated["fee_dementia_residential_from"], validated["fee_dementia_residential_to"] = validate_range(
            validated.get("fee_dementia_residential_from"), validated.get("fee_dementia_residential_to"), "Dementia Residential"
        )
        validated["fee_dementia_nursing_from"], validated["fee_dementia_nursing_to"] = validate_range(
            validated.get("fee_dementia_nursing_from"), validated.get("fee_dementia_nursing_to"), "Dementia Nursing"
        )
        validated["fee_respite_from"], validated["fee_respite_to"] = validate_range(
            validated.get("fee_respite_from"), validated.get("fee_respite_to"), "Respite"
        )
        
        # Validate: nursing >= residential
        res_from = validated.get("fee_residential_from")
        res_to = validated.get("fee_residential_to")
        nur_from = validated.get("fee_nursing_from")
        nur_to = validated.get("fee_nursing_to")
        
        if res_from and nur_from and nur_from < res_from:
            print(f"⚠️ Warning: Nursing fee ({nur_from}) < Residential fee ({res_from}). This may indicate data quality issues.")
        
        # Validate: dementia >= standard
        dem_res_from = validated.get("fee_dementia_residential_from")
        dem_nur_from = validated.get("fee_dementia_nursing_from")
        
        if res_from and dem_res_from and dem_res_from < res_from:
            print(f"⚠️ Warning: Dementia residential ({dem_res_from}) < Residential ({res_from})")
        
        if nur_from and dem_nur_from and dem_nur_from < nur_from:
            print(f"⚠️ Warning: Dementia nursing ({dem_nur_from}) < Nursing ({nur_from})")
        
        return validated
    
    async def analyze_care_home_website(
        self,
        url: str,
        care_home_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze care home website using Firecrawl v2.5 semantic crawling
        TWO-PHASE APPROACH: 
        1. Discover relevant pages with semantic prompt
        2. Extract structured data with detailed schema
        """
        import asyncio
        
        try:
            # PHASE 1: Semantic crawl to discover relevant pages
            print(f"🕷️ Phase 1: Discovering relevant pages on {url}...")
            
            crawl_payload = {
                "url": url,
                "limit": 30,
                # ✅ CORRECT PARAMETER: "prompt" not "crawlPrompt"
                "prompt": """Find pages containing information about:
                - Staff qualifications and team members
                - Facilities and amenities (rooms, gardens, equipment)
                - Care services and specializations
                - Pricing and fees
                - Activities and daily programs
                - Contact information
                
                Exclude: Privacy policy, cookie policy, terms of service, careers/jobs pages""",
                "maxDiscoveryDepth": 3,
                "scrapeOptions": {
                    "formats": [{"type": "markdown"}],
                    "onlyMainContent": True
                }
            }
            
            response = await self.client.post(
                f"{self.base_url}/crawl",
                json=crawl_payload
            )
            response.raise_for_status()
            crawl_job = response.json()
            
            # Poll for crawl completion
            job_id = crawl_job.get("id")
            if not job_id:
                raise Exception("No job ID returned from crawl")
            
            print(f"⏳ Crawl job started: {job_id}")
            
            # Wait for completion (max 5 minutes)
            max_attempts = 60  # 60 attempts * 5 seconds = 5 minutes
            attempt = 0
            crawl_data = []
            
            while attempt < max_attempts:
                await asyncio.sleep(5)  # Wait 5 seconds between checks
                
                status_response = await self.client.get(f"{self.base_url}/crawl/{job_id}")
                status_response.raise_for_status()
                status_data = status_response.json()
                
                status = status_data.get("status")
                completed = status_data.get("completed", 0)
                total = status_data.get("total", 0)
                
                # Progress messages removed per user request
                
                if status == "completed":
                    crawl_data = status_data.get("data", [])
                    print(f"✅ Phase 1 complete: {len(crawl_data)} relevant pages found")
                    break
                elif status == "failed":
                    error_msg = status_data.get("error", "Unknown error")
                    raise Exception(f"Crawl failed: {error_msg}")
                
                attempt += 1
            else:
                raise Exception("Crawl timeout after 5 minutes")
            
            if not crawl_data:
                raise Exception(f"No relevant pages found on {url}")
            
            # PHASE 2: Extract structured data from discovered pages
            print(f"📄 Phase 2: Extracting structured data from {len(crawl_data)} pages...")
            
            # Combine markdown content from all pages
            combined_content = "\n\n---\n\n".join([
                page.get("markdown", "") for page in crawl_data if page.get("markdown")
            ])
            
            # Use extract endpoint for structured extraction
            extraction_schema = {
                "type": "object",
                "properties": {
                    "care_home_name": {
                        "type": "string",
                        "description": "Official name of the care home"
                    },
                    "staff": {
                        "type": "object",
                        "properties": {
                            "team_size": {"type": "string"},
                            "qualifications": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                            "specialist_roles": {
                                "type": "array",
                                "items": {"type": "string"}
                            }
                        }
                    },
                    "facilities": {
                        "type": "object",
                        "properties": {
                            "rooms": {"type": "array", "items": {"type": "string"}},
                            "communal_areas": {"type": "array", "items": {"type": "string"}},
                            "outdoor_spaces": {"type": "array", "items": {"type": "string"}},
                            "special_facilities": {"type": "array", "items": {"type": "string"}},
                            "accessibility": {"type": "array", "items": {"type": "string"}}
                        }
                    },
                    "care_services": {
                        "type": "object",
                        "properties": {
                            "care_types": {"type": "array", "items": {"type": "string"}},
                            "specializations": {"type": "array", "items": {"type": "string"}},
                            "medical_services": {"type": "array", "items": {"type": "string"}}
                        }
                    },
                    "pricing": {
                        "type": "object",
                        "properties": {
                            "weekly_rate_range": {"type": "string"},
                            "included_services": {"type": "array", "items": {"type": "string"}},
                            "additional_fees": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "service": {"type": "string"},
                                        "cost": {"type": "string"}
                                    }
                                }
                            },
                            "funding_options": {"type": "array", "items": {"type": "string"}}
                        }
                    },
                    "activities": {
                        "type": "object",
                        "properties": {
                            "daily_activities": {"type": "array", "items": {"type": "string"}},
                            "therapies": {"type": "array", "items": {"type": "string"}},
                            "outings": {"type": "array", "items": {"type": "string"}}
                        }
                    },
                    "contact": {
                        "type": "object",
                        "properties": {
                            "phone": {"type": "string"},
                            "email": {"type": "string"},
                            "address": {"type": "string"},
                            "visiting_hours": {"type": "string"},
                            "website": {"type": "string"}
                        }
                    }
                },
                "required": ["care_home_name"]
            }
            
            # Extract from discovered URLs
            discovered_urls = [page.get("metadata", {}).get("sourceURL", url) for page in crawl_data[:10]]  # Limit to first 10 pages
            
            extract_payload = {
                "urls": discovered_urls,
                "prompt": f"""Extract comprehensive information about {care_home_name or 'this care home'} from the provided content.
                Focus on:
                1. Staff qualifications and team composition
                2. Physical facilities and amenities
                3. Care services and specializations
                4. Pricing structure and funding options
                5. Activities and therapy programs
                6. Contact and registration details
                
                Extract ALL available information. If data is not found for a section, leave it empty rather than guessing.""",
                "schema": extraction_schema,
                "enableWebSearch": False,
                "includeSubdomains": False
            }
            
            extract_response = await self.client.post(
                f"{self.base_url}/extract",
                json=extract_payload
            )
            extract_response.raise_for_status()
            extract_result = extract_response.json()
            
            # Process extract result
            extracted_data = {}
            if extract_result.get("success") and "data" in extract_result:
                extracted_data = extract_result.get("data", {})
            elif extract_result.get("id"):
                # Async job - poll for results
                extract_job_id = extract_result.get("id")
                for attempt in range(60):
                    await asyncio.sleep(5)
                    status_response = await self.client.get(f"{self.base_url}/extract/{extract_job_id}")
                    status_response.raise_for_status()
                    status_data = status_response.json()
                    if status_data.get("status") == "completed":
                        extracted_data = status_data.get("data", {})
                        break
                    elif status_data.get("status") == "failed":
                        raise Exception(f"Extraction failed: {status_data.get('error')}")
            
            return {
                "care_home_name": care_home_name or self._extract_name(combined_content, url),
                "website_url": url,
                "pages_analyzed": len(crawl_data),
                "scraped_at": datetime.now().isoformat(),
                "structured_data": extracted_data if extracted_data else {
                    "discovery_successful": True,
                    "pages_found": [page.get("metadata", {}).get("sourceURL") for page in crawl_data],
                    "combined_content_length": len(combined_content)
                },
                "extraction_method": "semantic-crawl-v2.5",
                "raw_pages": crawl_data[:5]  # Include first 5 pages for reference
            }
            
        except Exception as e:
            raise Exception(f"Error analyzing care home website: {str(e)}")
    
    def _extract_name(self, content: str, url: str) -> str:
        """Extract care home name from content"""
        # Try to find name in first few lines
        lines = content.split("\n")[:10]
        for line in lines:
            if "care home" in line.lower() or "care" in line.lower():
                # Clean up the line
                name = line.strip().replace("#", "").strip()
                if len(name) > 5 and len(name) < 100:
                    return name
        # Fallback to URL domain
        domain = urlparse(url).netloc
        return domain.replace("www.", "").split(".")[0].title()
    
    def _extract_staff_info(self, content: str) -> List[str]:
        """Extract staff qualifications and team info"""
        qualifications = []
        content_lower = content.lower()
        
        # Common qualifications
        qual_keywords = ["rgn", "rn", "nvq", "level", "certificate", "qualified", "registered", "nurse", "dementia", "specialist"]
        
        # Look for qualification mentions
        lines = content.split("\n")
        for line in lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in qual_keywords):
                # Clean and add
                cleaned = line.strip()[:200]
                if cleaned and len(cleaned) > 10:
                    qualifications.append(cleaned)
        
        return qualifications[:10]  # Limit to 10
    
    def _extract_facilities(self, content: str) -> List[str]:
        """Extract facilities mentioned"""
        facilities = []
        content_lower = content.lower()
        
        # Common facilities
        facility_keywords = ["garden", "pool", "gym", "cinema", "salon", "library", "dining", "lounge", "activity", "therapy"]
        
        lines = content.split("\n")
        for line in lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in facility_keywords):
                cleaned = line.strip()[:150]
                if cleaned and len(cleaned) > 5:
                    facilities.append(cleaned)
        
        return list(set(facilities))[:15]  # Remove duplicates, limit to 15
    
    def _extract_services(self, content: str) -> List[str]:
        """Extract care services"""
        services = []
        content_lower = content.lower()
        
        service_keywords = ["dementia", "nursing", "residential", "respite", "palliative", "end of life", "physical", "disability", "alzheimer"]
        
        lines = content.split("\n")
        for line in lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in service_keywords):
                cleaned = line.strip()[:150]
                if cleaned and len(cleaned) > 5:
                    services.append(cleaned)
        
        return list(set(services))[:10]
    
    def _extract_pricing(self, content: str) -> Optional[str]:
        """Extract pricing information"""
        content_lower = content.lower()
        
        # Look for price patterns
        import re
        price_patterns = [
            r"£[\d,]+(?:\.\d{2})?\s*(?:per|/|week|month)",
            r"from\s+£[\d,]+",
            r"£[\d,]+(?:-|to)\s*£[\d,]+"
        ]
        
        for pattern in price_patterns:
            matches = re.findall(pattern, content_lower)
            if matches:
                return matches[0]
        
        return None
    
    def _extract_activities(self, content: str) -> List[str]:
        """Extract activities mentioned"""
        activities = []
        content_lower = content.lower()
        
        activity_keywords = ["activity", "entertainment", "exercise", "art", "music", "outings", "events", "program"]
        
        lines = content.split("\n")
        for line in lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in activity_keywords):
                cleaned = line.strip()[:150]
                if cleaned and len(cleaned) > 5:
                    activities.append(cleaned)
        
        return list(set(activities))[:10]
    
    def _extract_contact_info(self, content: str) -> Dict[str, Optional[str]]:
        """Extract contact information"""
        import re
        
        contact = {
            "phone": None,
            "email": None,
            "address": None
        }
        
        # Phone patterns
        phone_patterns = [
            r"0\d{2,3}\s?\d{3,4}\s?\d{3,4}",
            r"\+44\s?\d{2,3}\s?\d{3,4}\s?\d{3,4}"
        ]
        
        for pattern in phone_patterns:
            match = re.search(pattern, content)
            if match:
                contact["phone"] = match.group(0)
                break
        
        # Email pattern
        email_match = re.search(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", content)
        if email_match:
            contact["email"] = email_match.group(0)
        
        return contact
    
    # ==================== ВСПОМОГАТЕЛЬНЫЕ КЛАССЫ ИЗ ТЗ ====================
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


# ==================== ПРИОРИТЕТ 1: КРИТИЧНЫЕ КОМПОНЕНТЫ ====================

class ContentTypeClassifier:
    """AI-классификация типа контента страницы через Claude"""
    
    def __init__(self, anthropic_client):
        self.client = anthropic_client
    
    async def classify_page_type(self, url: str, html_snippet: str) -> str:
        """Определение типа страницы через Claude"""
        if not self.client:
            return "other"
        
        # Берем первые 5000 символов HTML для анализа
        snippet = html_snippet[:5000]
        
        prompt = f"""Analyze this webpage and classify its type.

URL: {url}

HTML snippet:
{snippet}

Classify this page into ONE of these categories:
1. care_home_listing - A page listing multiple care homes (directory, search results)
2. care_home_detail - Detailed page about a SINGLE care home facility
3. regional_page - Page about care homes in a specific region/city
4. service_page - Page describing types of care services
5. news_article - News article or blog post
6. about_page - About the company/organization
7. contact_page - Contact information
8. homepage - Main homepage
9. other - None of the above

Respond with ONLY the category name, nothing else."""

        try:
            response = await self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=50,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return response.content[0].text.strip()
        except Exception as e:
            print(f"⚠️ Classification error for {url}: {e}")
            return "other"
    
    async def classify_batch(self, pages: List[Dict[str, str]]) -> Dict[str, str]:
        """Пакетная классификация страниц"""
        classifications = {}
        
        for page in pages:
            try:
                page_type = await self.classify_page_type(
                    page.get('url', ''),
                    page.get('html', '')
                )
                classifications[page.get('url', '')] = page_type
            except Exception as e:
                print(f"Classification error: {e}")
                classifications[page.get('url', '')] = "other"
        
        return classifications


class URLPatternRecognizer:
    """Распознавание паттернов URL для любого сайта"""
    
    @staticmethod
    def extract_url_template(urls: List[str]) -> Dict[str, Dict]:
        """Извлечение шаблонов URL из списка"""
        templates = {}
        pattern_groups = defaultdict(list)
        
        for url in urls:
            parsed = urlparse(url)
            path = parsed.path
            
            # Замена чисел на {id}, слагов на {slug}
            template = path
            template = re.sub(r'/\d+/', '/{id}/', template)
            template = re.sub(r'/[a-z0-9\-]+/', '/{slug}/', template)
            
            pattern_groups[template].append(url)
        
        # Выбор наиболее частых шаблонов
        sorted_patterns = sorted(
            pattern_groups.items(),
            key=lambda x: len(x[1]),
            reverse=True
        )
        
        for i, (template, template_urls) in enumerate(sorted_patterns[:5]):
            templates[f"pattern_{i+1}"] = {
                "template": template,
                "count": len(template_urls),
                "examples": template_urls[:3]
            }
        
        return templates
    
    @staticmethod
    def match_url_to_template(url: str, templates: Dict) -> Optional[str]:
        """Определение, какому шаблону соответствует URL"""
        parsed = urlparse(url)
        path = parsed.path
        
        for template_name, template_data in templates.items():
            template = template_data['template']
            
            # Создание regex из шаблона
            regex_pattern = template.replace('{id}', r'\d+')
            regex_pattern = regex_pattern.replace('{slug}', r'[a-z0-9\-]+')
            regex_pattern = '^' + regex_pattern + '$'
            
            if re.match(regex_pattern, path):
                return template_name
        
        return None


class ListingPageDetector:
    """Определение страниц со списками домов престарелых"""
    
    @staticmethod
    def detect_listing_indicators(html: str) -> Dict[str, Any]:
        """Поиск индикаторов listing page"""
        soup = BeautifulSoup(html, 'html.parser')
        
        indicators = {
            "has_multiple_cards": False,
            "has_grid_layout": False,
            "has_phone_numbers": False,
            "has_addresses": False,
            "card_count": 0
        }
        
        # Поиск повторяющихся блоков (карточки)
        divs = soup.find_all(['div', 'article', 'section'])
        class_counter = Counter()
        
        for div in divs:
            classes = div.get('class', [])
            if classes:
                class_key = ' '.join(sorted(classes))
                class_counter[class_key] += 1
        
        # Если есть класс, повторяющийся 3+ раза
        for class_key, count in class_counter.items():
            if count >= 3:
                indicators["has_multiple_cards"] = True
                indicators["card_count"] = count
                break
        
        # Поиск grid/flex layout
        if re.search(r'display:\s*grid|display:\s*flex', str(soup), re.I):
            indicators["has_grid_layout"] = True
        
        # Поиск множественных телефонов
        phone_links = soup.find_all('a', href=re.compile(r'tel:'))
        if len(phone_links) >= 3:
            indicators["has_phone_numbers"] = True
        
        # Поиск множественных адресов (UK postcodes)
        postcodes = re.findall(
            r'[A-Z]{1,2}\d{1,2}\s?\d[A-Z]{2}',
            soup.get_text()
        )
        if len(postcodes) >= 3:
            indicators["has_addresses"] = True
        
        # Оценка уверенности
        confidence = sum([
            indicators["has_multiple_cards"] * 0.4,
            indicators["has_grid_layout"] * 0.2,
            indicators["has_phone_numbers"] * 0.2,
            indicators["has_addresses"] * 0.2
        ])
        
        indicators["confidence"] = confidence
        indicators["is_likely_listing"] = confidence >= 0.6
        
        return indicators


class RateLimitedCrawler:
    """Crawler с интеллектуальным rate limiting"""
    
    def __init__(self, firecrawl_client, base_delay: float = 2.0):
        self.firecrawl_client = firecrawl_client
        self.base_delay = base_delay
        self.delay_multiplier = 1.0
        self.last_request_time = None
    
    async def adaptive_delay(self):
        """Адаптивная задержка на основе истории запросов"""
        if self.last_request_time:
            elapsed = time.time() - self.last_request_time
            required_delay = self.base_delay * self.delay_multiplier
            
            if elapsed < required_delay:
                wait_time = required_delay - elapsed
                await asyncio.sleep(wait_time)
        
        self.last_request_time = time.time()
    
    async def scrape_with_retry(
        self,
        url: str,
        max_retries: int = 3,
        formats: Optional[List] = None
    ) -> Optional[Dict]:
        """Scrape с exponential backoff"""
        if formats is None:
            formats = [{"type": "markdown"}]
        
        for attempt in range(max_retries):
            await self.adaptive_delay()
            
            try:
                result = await self.firecrawl_client.scrape_url(
                    url=url,
                    formats=formats
                )
                
                # Успех - снижаем delay multiplier
                self.delay_multiplier = max(1.0, self.delay_multiplier * 0.9)
                
                return result
                
            except Exception as e:
                error_msg = str(e).lower()
                
                if 'rate limit' in error_msg or '429' in error_msg:
                    # Rate limit hit - увеличиваем задержку
                    self.delay_multiplier *= 2.0
                    backoff = self.base_delay * (2 ** attempt) * self.delay_multiplier
                    
                    print(f"⚠️ Rate limit hit. Backoff: {backoff:.1f}s")
                    await asyncio.sleep(backoff)
                    
                elif 'timeout' in error_msg:
                    print(f"⚠️ Timeout on {url}. Retry {attempt+1}/{max_retries}")
                    await asyncio.sleep(5)
                    
                else:
                    print(f"❌ Error: {e}")
                    if attempt == max_retries - 1:
                        return None
        
        return None


# ==================== ПРИОРИТЕТ 2: АДАПТИВНЫЕ АЛГОРИТМЫ ====================

class NameExtractor:
    """Интеллектуальное извлечение названия дома престарелых"""
    
    @staticmethod
    def extract_from_html(soup: BeautifulSoup, url: str) -> Optional[str]:
        """Многоступенчатое извлечение названия"""
        # Стратегия 1: H1 tag (наивысший приоритет)
        h1 = soup.find('h1')
        if h1:
            name = h1.get_text(strip=True)
            name = re.sub(r'^(Welcome to|About)\s+', '', name, flags=re.I)
            name = re.sub(r'\s+(Care Home|Nursing Home|Residential Home).*$', '', name, flags=re.I)
            if len(name) > 3:
                return name
        
        # Стратегия 2: Title tag
        title = soup.find('title')
        if title:
            name = title.get_text(strip=True)
            name = name.split('|')[0].split('-')[0].strip()
            name = re.sub(r'\s+(Care Home|Nursing Home).*$', '', name, flags=re.I)
            if len(name) > 3:
                return name
        
        # Стратегия 3: Open Graph meta
        og_title = soup.find('meta', property='og:title')
        if og_title and og_title.get('content'):
            return og_title['content']
        
        # Стратегия 4: URL slug
        slug = url.rstrip('/').split('/')[-1]
        if slug and slug not in ['care-homes', 'homes', 'directory']:
            name = slug.replace('-', ' ').title()
            return name
        
        return None


class AddressParser:
    """Парсинг UK адресов любого формата"""
    
    @staticmethod
    def parse_uk_address(text: str) -> Dict[str, Optional[str]]:
        """Разбор UK адреса на компоненты"""
        # Извлечение postcode
        postcode_match = re.search(
            r'\b([A-Z]{1,2}\d{1,2}\s?\d[A-Z]{2})\b',
            text
        )
        postcode = postcode_match.group(1) if postcode_match else None
        
        components = {
            "street": None,
            "city": None,
            "county": None,
            "postcode": postcode,
            "full_address": text.strip()
        }
        
        if not postcode:
            return components
        
        # Разбиение на части через запятую
        parts = [p.strip() for p in text.split(',')]
        
        if len(parts) >= 3:
            components["street"] = parts[0]
            components["city"] = parts[1]
            
            last_part = parts[-1]
            if postcode in last_part:
                county_part = last_part.replace(postcode, '').strip()
                if county_part:
                    components["county"] = county_part
            elif len(parts) > 3:
                components["county"] = parts[2]
        
        elif len(parts) == 2:
            components["street"] = parts[0]
            city_postcode = parts[1]
            components["city"] = city_postcode.replace(postcode, '').strip()
        
        else:
            text_without_postcode = text.replace(postcode, '').strip(' ,')
            parts = [p.strip() for p in text_without_postcode.split(',')]
            
            if parts:
                components["street"] = parts[0]
                if len(parts) > 1:
                    components["city"] = parts[-1]
        
        return components


class FacilityDetector:
    """Определение удобств и услуг из текста"""
    
    FACILITY_PATTERNS = {
        "Garden": ["garden", "outdoor space", "landscaped grounds", "patio", "terrace"],
        "Cinema Room": ["cinema", "movie room", "film screening", "theatre room"],
        "Hair Salon": ["hair salon", "hairdresser", "barber", "hair care"],
        "Library": ["library", "reading room", "book collection"],
        "Café": ["café", "coffee shop", "bistro", "refreshment"],
        "Gym": ["gym", "fitness", "exercise room", "workout"],
        "Swimming Pool": ["pool", "swimming", "hydrotherapy pool"],
        "Activities Room": ["activities room", "recreation", "hobby room"],
        "WiFi": ["wi-fi", "wifi", "internet access", "wireless"],
        "Parking": ["parking", "car park", "visitor parking"],
        "Lift": ["lift", "elevator", "accessible"],
        "Minibus": ["minibus", "transport", "trips", "outings"],
        "Chapel": ["chapel", "prayer room", "spiritual"],
        "Restaurant": ["restaurant", "dining room", "meal service"],
        "24-hour Care": ["24 hour", "24/7", "round the clock", "24-hour nursing"]
    }
    
    @classmethod
    def detect_facilities(cls, text: str) -> List[str]:
        """Обнаружение удобств из текста"""
        text_lower = text.lower()
        detected = []
        
        for facility, keywords in cls.FACILITY_PATTERNS.items():
            if any(kw in text_lower for kw in keywords):
                detected.append(facility)
        
        return detected
    
    @classmethod
    def detect_from_images(cls, soup: BeautifulSoup) -> List[str]:
        """Обнаружение удобств по alt текстам изображений"""
        detected = []
        images = soup.find_all('img', alt=True)
        
        for img in images:
            alt = img['alt'].lower()
            
            for facility, keywords in cls.FACILITY_PATTERNS.items():
                if any(kw in alt for kw in keywords):
                    if facility not in detected:
                        detected.append(facility)
        
        return detected


# ==================== ПРИОРИТЕТ 3: СПЕЦИАЛИЗИРОВАННЫЕ ЭКСТРАКТОРЫ ====================

class WordPressExtractor:
    """Специализированный экстрактор для WordPress"""
    
    @staticmethod
    def detect_wordpress(html: str) -> bool:
        indicators = ['wp-content', 'wp-includes', 'wordpress']
        return any(ind in html.lower() for ind in indicators)
    
    @staticmethod
    def extract_featured_image(soup: BeautifulSoup) -> Optional[str]:
        """Извлечение featured image WordPress"""
        # Паттерн 1: wp-post-image class
        img = soup.find('img', class_=re.compile(r'wp-post-image'))
        if img and img.get('src'):
            return img['src']
        
        # Паттерн 2: wp-content uploads
        img = soup.find('img', src=re.compile(r'/wp-content/uploads/'))
        if img:
            return img['src']
        
        return None
    
    @staticmethod
    def extract_custom_fields(soup: BeautifulSoup) -> Dict:
        """Извлечение WordPress custom fields"""
        custom_data = {}
        
        elements_with_data = soup.find_all(attrs={"data-acf": True})
        for el in elements_with_data:
            for attr, value in el.attrs.items():
                if attr.startswith('data-'):
                    field_name = attr.replace('data-', '')
                    custom_data[field_name] = value
        
        return custom_data


class WixExtractor:
    """Специализированный экстрактор для Wix"""
    
    @staticmethod
    def detect_wix(html: str) -> bool:
        return 'wix.com' in html.lower() or '_wix' in html.lower()
    
    @staticmethod
    async def scrape_wix_site(url: str, firecrawl_client) -> Dict:
        """Scraping Wix с JavaScript rendering"""
        result = await firecrawl_client.scrape_url(
            url=url,
            formats=[{"type": "markdown"}],
            wait_for=3000  # Wix требует больше времени для JS
        )
        return result


class StaticHTMLExtractor:
    """Экстрактор для статичных HTML сайтов"""
    
    @staticmethod
    def extract_with_beautifulsoup(html: str) -> Dict:
        """Извлечение через BeautifulSoup"""
        soup = BeautifulSoup(html, 'html.parser')
        data = {}
        
        # Название - первый H1
        h1 = soup.find('h1')
        if h1:
            data['name'] = h1.get_text(strip=True)
        
        # Телефон - ссылка tel:
        phone_link = soup.find('a', href=re.compile(r'^tel:'))
        if phone_link:
            data['phone'] = phone_link['href'].replace('tel:', '')
        
        # Email - ссылка mailto:
        email_link = soup.find('a', href=re.compile(r'^mailto:'))
        if email_link:
            data['email'] = email_link['href'].replace('mailto:', '')
        
        # Адрес - ищем postcode
        text = soup.get_text()
        postcode_pattern = r'\b[A-Z]{1,2}\d{1,2}\s?\d[A-Z]{2}\b'
        postcode_match = re.search(postcode_pattern, text)
        if postcode_match:
            data['postcode'] = postcode_match.group(0)
            # Извлечение адреса вокруг postcode
            start = max(0, postcode_match.start() - 200)
            address_text = text[start:postcode_match.end()].strip()
            data['address'] = address_text
        
        return data

