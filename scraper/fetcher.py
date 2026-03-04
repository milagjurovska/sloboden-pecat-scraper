import logging
import asyncio
from typing import Any, List, Optional, Dict
import aiohttp

from config.scraper_settings import settings

logger = logging.getLogger(__name__)


class Fetcher:
    """Fetcher class for Sloboden Pechat using WordPress API."""

    def __init__(self):
        self.api_base_url = settings.api_base_url
        self.headers = settings.headers

    async def fetch_metadata(self) -> Optional[List[Dict[str, Any]]]:
        """Return configured categories as metadata."""
        categories = []
        for name, cat_id in settings.category_ids.items():
            categories.append({"name": name, "id": cat_id})
        return categories

    async def fetch_data(self, seen_ids: set, metadata: List[Dict[str, Any]]):
        """Fetch posts from all categories using a generator."""
        if not metadata:
            return

        async with aiohttp.ClientSession(headers=self.headers) as session:
            for category in metadata:
                logger.info("Processing category: %s (ID: %s)", category['name'], category['id'])
                async for page_posts in self._fetch_posts_from_category(session, category, seen_ids):
                    if page_posts:
                        yield page_posts

    async def _fetch_posts_from_category(self, session, category, seen_ids):
        """Paginate through category and fetch posts."""
        cat_id = category['id']
        cat_name = category['name']
        
        for page in range(1, settings.max_pages_per_category + 1):
            params = {
                'categories': cat_id,
                'page': page,
                'per_page': 20 
            }
            
            logger.info("Fetching posts from category %s, page %d", cat_name, page)
            
            try:
                async with session.get(self.api_base_url, params=params) as response:
                    if response.status == 400:
                        logger.info("Reached end of pagination for category %s at page %d", cat_name, page)
                        break
                    
                    if response.status != 200:
                        logger.error("Error fetching page %d for category %s: %s", page, cat_name, response.status)
                        break
                        
                    posts = await response.json()
                    
                    if not posts:
                        break
                        
                    posts_this_page = []
                    new_count = 0
                    for post in posts:
                        post_id = str(post.get('id'))
                        if post_id in seen_ids:
                            continue
                        
                        # Add category name to post for parser
                        post['category_name'] = cat_name
                        posts_this_page.append(post)
                        new_count += 1
                        
                    if posts_this_page:
                        yield posts_this_page
                        
                    if new_count == 0:
                        # If we find nothing new on the first few pages, we might want to stop
                        # But for now, let's keep it simple
                        pass
                        
                    await asyncio.sleep(1 / settings.requests_per_second)
                    
            except Exception as e:
                logger.error("Exception during fetch for category %s, page %d: %s", cat_name, page, e)
                break
