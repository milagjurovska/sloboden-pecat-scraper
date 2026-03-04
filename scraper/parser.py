import logging
from typing import Any, List
from bs4 import BeautifulSoup
from datetime import datetime
import html as html_lib
from vezilka_schemas import Record, RecordMeta, RecordType

logger = logging.getLogger(__name__)


class Parser:
    """Parser class for Sloboden Pechat WordPress API responses."""
    
    def __init__(self):
        pass

    def parse(self, raw_data: List[dict], metadata: Any = None) -> List[Record]:
        """Parse WordPress API results into structured Record objects."""
        records = []
        
        for post in raw_data:
            post_id = str(post['id'])
            url = post.get('link')
            title = html_lib.unescape(post['title']['rendered'])
            content_html = post['content']['rendered']
            category = post.get('category_name', 'uncategorized')
            published_at_str = post.get('date')
            
            text = self._clean_content(content_html)
            
            if not text:
                logger.warning("Empty content for post %s", post_id)
                continue

            # Create metadata
            published_at = None
            if published_at_str:
                try:
                    published_at = datetime.fromisoformat(published_at_str)
                except:
                    pass

            record_meta = RecordMeta(
                source="https://www.slobodenpecat.mk/",
                url=url,
                tags=[category],
                labels=[],
                scraped_at=datetime.now(),
                published_at=published_at
            )
            
            # Create record
            records.append(Record(
                id=post_id,
                text=text,
                type=RecordType.NARRATIVE,
                last_modified_at=datetime.now(),
                meta=record_meta
            ))
        
        return records

    def _clean_content(self, html_content: str) -> str:
        """Clean HTML content from WordPress posts."""
        if not html_content:
            return ""
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove unwanted elements
        for unwanted in soup.select('.related-posts, .sharedaddy, .jp-relatedposts, script, style, iframe, figure, form'):
            unwanted.decompose()
            
        text_parts = []
        
        for p in soup.find_all(['p', 'h2', 'h3', 'ul', 'ol']):
            t = p.get_text(separator=" ", strip=True)
            # Filter out "Read More" and similar links
            if len(t) < 100 and ("Прочитајте" in t or "Read More" in t or "Ви препорачуваме" in t):
                continue
            if t:
                text_parts.append(" ".join(t.split()))
                
        return "\n\n".join(text_parts)
