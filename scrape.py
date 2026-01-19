import requests
import json
import datetime
import time
import os
import sys
import html
from bs4 import BeautifulSoup

try:
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

API_BASE_URL = "https://www.slobodenpecat.mk/wp-json/wp/v2/posts"
DATA_DIR = "data"
MAX_PAGES_PER_CATEGORY = 9999  
DELAY = 0.2

def get_category_file(category_name):
    """Get the file path for a specific category."""
    os.makedirs(DATA_DIR, exist_ok=True)
    return os.path.join(DATA_DIR, f"{category_name}.json")

CATEGORY_IDS = {
    "makedonija": 57,
    "skopje": 1089,
    "region": 1090,
    "ekonomija": 67,
    "kultura": 1373,
    "hronika": 1092,
    "vi-preporachuvame": 9081,
    "svet": 1091,
    "milenici": 89861,
    "semejstvo": 78,
    "zena": 7497,
    "zabava": 1374,
    "tehnologija": 72,
    "zivot": 38079,
    "scena": 42379,
    "hrana": 76,
    "zdravje": 74,
    "retro": 42381,
    "horoskop": 81,
    "avtomagazin": 73,
    "film-i-muzika": 71,
    "kolumni": 31,
    "golemi-prikazni": 122889,
    "fudbal": 83,
    "kosarka": 84,
    "rakomet": 85,
    "ostanato-sport": 86
}

def clean_html_content(html_content):
    if not html_content:
        return ""
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    for unwanted in soup.select('.related-posts, .sharedaddy, .jp-relatedposts, script, style, iframe, figure, form'):
        unwanted.decompose()
        
    text_parts = []
    
    for p in soup.find_all(['p', 'h2', 'h3', 'ul', 'ol']):
        t = p.get_text(strip=True)
        if len(t) < 100 and ("Прочитајте" in t or "Read More" in t or "Ви препорачуваме" in t):
            continue
        if t:
            text_parts.append(t)
            
    return "\n\n".join(text_parts)

def fetch_category_posts(category_name, category_id, category_file):
    print(f"\n--- Scraping Category: {category_name} (ID: {category_id}) ---")
    
    existing_data = load_data(category_file)
    existing_urls = {item['url'] for item in existing_data}
    print(f"Loaded {len(existing_data)} existing articles for {category_name}")
    
    new_articles = []
    
    for page in range(1, MAX_PAGES_PER_CATEGORY + 1):
        params = {
            'categories': category_id,
            'page': page,
            'per_page': 20 
        }
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
            }
            r = requests.get(API_BASE_URL, params=params, headers=headers)
            
            if r.status_code == 400: 
                print(f"[{category_name}] Reached end of pagination at page {page}.")
                break
                
            r.raise_for_status()
            posts = r.json()
            
            if not posts:
                print(f"[{category_name}] No posts returned on page {page}.")
                break
                
            page_new = 0
            for post in posts:
                link = post.get('link')
                if link in existing_urls:
                    continue
                
                title = html.unescape(post['title']['rendered'])
                content_html = post['content']['rendered']
                text = clean_html_content(content_html)
                
                article = {
                    'url': link,
                    'title': title,
                    'text': text,
                    'categories': [category_name],
                    'page_id': post.get('id'),
                    'scraped_at': datetime.datetime.now().isoformat()
                }
                
                new_articles.append(article)
                existing_urls.add(link)
                page_new += 1
                
                try:
                    print(f"[{category_name}] Scraped: {title[:50]}...")
                except:
                    pass
                    
            print(f"[{category_name}] Page {page} finished. +{page_new} articles.")
            if page_new == 0 and page > 1:
                
                pass
                
            time.sleep(DELAY)
            
        except Exception as e:
            print(f"[{category_name}] Error on page {page}: {e}")
            break
    
    existing_data.extend(new_articles)
    return existing_data, len(new_articles)

def load_data(filepath):
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_data(data, filepath):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def main():
    print(f"Starting API scrape with category-based file storage.")
    print(f"Data directory: {DATA_DIR}/")
    
    os.makedirs(DATA_DIR, exist_ok=True)
    
    total_added = 0
    total_articles = 0
    
    for cat_name, cat_id in CATEGORY_IDS.items():
        category_file = get_category_file(cat_name)
        category_data, new_count = fetch_category_posts(cat_name, cat_id, category_file)
        
        save_data(category_data, category_file)
        
        total_added += new_count
        total_articles += len(category_data)
        
        print(f"[{cat_name}] Saved to {category_file}")
            
    print(f"\n{'='*60}")
    print(f"Scraping finished!")
    print(f"Added {total_added} new articles")
    print(f"Total articles across all categories: {total_articles}")
    print(f"Data stored in: {DATA_DIR}/")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
