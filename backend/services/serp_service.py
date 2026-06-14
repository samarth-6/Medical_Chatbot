from duckduckgo_search import DDGS
from urllib.parse import urlparse
import asyncio
import aiohttp
import os
from typing import List, Dict, Any, Optional

from backend.config import TRUSTED_DOMAINS
from backend.logger import logger


class SerpService:
    """
    Search trusted medical domains using Serper API (Google) with DuckDuckGo fallback.
    Includes rate limit handling, retry logic, and domain filtering.
    """

    def __init__(self):
        self.serper_api_key = os.getenv("SERPER_API_KEY")
        self.use_serper = bool(self.serper_api_key)
        
        if self.use_serper:
            logger.info("✅ Serper API (Google Search) configured")
        else:
            logger.warning("⚠️ SERPER_API_KEY not found, using DuckDuckGo fallback")

    @staticmethod
    def is_trusted(url: str) -> bool:
        """Check if URL belongs to a trusted medical domain"""
        try:
            domain = urlparse(url).netloc.lower()
            
            if domain.startswith('www.'):
                domain = domain[4:]
            
            return any(
                trusted in domain
                for trusted in TRUSTED_DOMAINS
            )
        except Exception:
            return False

    async def search(
        self,
        query: str,
        num_results: int = 5
    ) -> List[Dict[str, Any]]:
     
        if self.use_serper:
            results = await self._search_serper(query, num_results)
            if results:
                return results
            logger.warning("Serper API failed, falling back to DuckDuckGo")
        
        return await self._search_duckduckgo(query, num_results)

    async def _search_serper(
        self,
        query: str,
        num_results: int = 5
    ) -> List[Dict[str, Any]]:
       
        if not self.serper_api_key:
            return []
        
        max_retries = 2
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                async with aiohttp.ClientSession() as session:
                    headers = {
                        "X-API-KEY": self.serper_api_key,
                        "Content-Type": "application/json"
                    }
                    
                    payload = {
                        "q": f"site:({' OR '.join(TRUSTED_DOMAINS[:5])}) {query}",
                        "num": num_results
                    }
                    
                    async with session.post(
                        "https://google.serper.dev/search",
                        headers=headers,
                        json=payload
                    ) as response:
                        
                        if response.status == 200:
                            data = await response.json()
                            results = []
                            
                            for item in data.get("organic", []):
                                url = item.get("link", "")
                                if not url:
                                    continue
                                
                                if not self.is_trusted(url):
                                    continue
                                
                                results.append({
                                    "title": item.get("title", ""),
                                    "url": url,
                                    "snippet": item.get("snippet", "")
                                })
                            
                            logger.info(f"✅ Serper API found {len(results)} results for: {query}")
                            return results[:num_results]
                            
                        elif response.status == 429:  
                            logger.warning(f"Serper API rate limited (attempt {attempt + 1})")
                            await asyncio.sleep(retry_delay * (attempt + 1))
                        else:
                            logger.error(f"Serper API error: {response.status}")
                            return []
                            
            except Exception as e:
                logger.error(f"Serper API exception: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                    
        return []

    async def _search_duckduckgo(
        self,
        query: str,
        num_results: int = 3
    ) -> List[Dict[str, Any]]:
      
        all_results = []
        max_retries = 3
        base_delay = 3 
        
        for idx, domain in enumerate(TRUSTED_DOMAINS):
            delay = base_delay + (idx * 1.5) 
            await asyncio.sleep(delay)
            
            search_query = f"site:{domain} {query}"
            
            for attempt in range(max_retries):
                try:
                    with DDGS() as ddgs:
                        logger.info(f"🔍 Searching {domain} for: {query} (attempt {attempt + 1})")
                        
                        search_results = list(
                            ddgs.text(
                                search_query,
                                max_results=num_results,
                                region='wt-wt', 
                                safesearch='moderate'
                            )
                        )
                        
                        for item in search_results:
                            url = item.get("href", "")
                            if not url:
                                continue
                            
                            if not self.is_trusted(url):
                                continue
                            
                            all_results.append({
                                "title": item.get("title", ""),
                                "url": url,
                                "snippet": item.get("body", "")
                            })
                        
                        logger.info(f"✅ Found {len(search_results)} results from {domain}")
                        break
                        
                except Exception as e:
                    error_msg = str(e)
                    if "Ratelimit" in error_msg or "202" in error_msg:
                        wait_time = delay * (attempt + 1)
                        logger.warning(f"⚠️ DuckDuckGo rate limited on {domain}, waiting {wait_time}s...")
                        await asyncio.sleep(wait_time)
                    else:
                        logger.error(f"❌ Error searching {domain}: {e}")
                        break
                    
                    if attempt == max_retries - 1:
                        logger.error(f"Failed to search {domain} after {max_retries} attempts")
        
        seen = set()
        unique_results = []
        for r in all_results:
            if r["url"] not in seen:
                seen.add(r["url"])
                unique_results.append(r)
        
        logger.info(f"📊 DuckDuckGo found {len(unique_results)} unique results from trusted domains")
        return unique_results[:num_results * 2] 

    async def search_single_domain(
        self,
        query: str,
        domain: str,
        num_results: int = 3
    ) -> List[Dict[str, Any]]:
      
        max_retries = 2
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                with DDGS() as ddgs:
                    search_query = f"site:{domain} {query}"
                    
                    search_results = list(
                        ddgs.text(
                            search_query,
                            max_results=num_results
                        )
                    )
                    
                    results = []
                    for item in search_results:
                        url = item.get("href", "")
                        if url and self.is_trusted(url):
                            results.append({
                                "title": item.get("title", ""),
                                "url": url,
                                "snippet": item.get("body", "")
                            })
                    
                    return results
                    
            except Exception as e:
                if "Ratelimit" in str(e):
                    logger.warning(f"Rate limited on {domain}, attempt {attempt + 1}")
                    await asyncio.sleep(retry_delay * (attempt + 1))
                else:
                    logger.error(f"Error searching {domain}: {e}")
                    return []
        
        return []


serp_service = SerpService()