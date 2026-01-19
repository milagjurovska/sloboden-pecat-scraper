"""
Query utility for searching across category-based article files.

This script allows you to search, filter, and analyze articles stored
in category-specific JSON files.

Usage:
    python utils/query_data.py --stats
    python utils/query_data.py --search "keyword"
    python utils/query_data.py --category sport
    python utils/query_data.py --search "keyword" --category sport --export results.json
"""

import json
import os
import argparse
from datetime import datetime
from collections import defaultdict


def load_category_file(category_file):
    """Load a single category file."""
    try:
        with open(category_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Warning: Failed to load {category_file}: {e}")
        return []


def load_all_categories(data_dir):
    """Load all category files from the data directory."""
    if not os.path.exists(data_dir):
        print(f"Error: Data directory '{data_dir}' not found!")
        return {}
    
    category_data = {}
    json_files = [f for f in os.listdir(data_dir) if f.endswith('.json')]
    
    print(f"Loading {len(json_files)} category files from '{data_dir}/'...")
    
    for filename in json_files:
        category_name = filename[:-5]  # Remove .json extension
        filepath = os.path.join(data_dir, filename)
        articles = load_category_file(filepath)
        category_data[category_name] = articles
        print(f"  ✓ {category_name}: {len(articles):,} articles")
    
    return category_data


def search_articles(category_data, query, category_filter=None):
    """Search for articles matching the query."""
    query_lower = query.lower()
    results = []
    
    for category, articles in category_data.items():
        # Skip if category filter is set and doesn't match
        if category_filter and category != category_filter:
            continue
        
        for article in articles:
            # Search in title and text
            title = article.get('title', '').lower()
            text = article.get('text', '').lower()
            
            if query_lower in title or query_lower in text:
                results.append({
                    'category': category,
                    'article': article
                })
    
    return results


def filter_by_date_range(category_data, start_date=None, end_date=None):
    """Filter articles by date range."""
    results = []
    
    for category, articles in category_data.items():
        for article in articles:
            scraped_at = article.get('scraped_at', '')
            if not scraped_at:
                continue
            
            article_date = datetime.fromisoformat(scraped_at)
            
            if start_date and article_date < start_date:
                continue
            if end_date and article_date > end_date:
                continue
            
            results.append({
                'category': category,
                'article': article
            })
    
    return results


def get_statistics(category_data):
    """Get statistics about the data."""
    stats = {
        'total_articles': 0,
        'total_categories': len(category_data),
        'categories': {},
        'date_range': {'earliest': None, 'latest': None}
    }
    
    all_dates = []
    
    for category, articles in category_data.items():
        count = len(articles)
        stats['total_articles'] += count
        stats['categories'][category] = count
        
        # Collect dates
        for article in articles:
            scraped_at = article.get('scraped_at')
            if scraped_at:
                try:
                    date = datetime.fromisoformat(scraped_at)
                    all_dates.append(date)
                except:
                    pass
    
    if all_dates:
        stats['date_range']['earliest'] = min(all_dates).isoformat()
        stats['date_range']['latest'] = max(all_dates).isoformat()
    
    return stats


def print_statistics(stats):
    """Print statistics in a readable format."""
    print("\n" + "="*60)
    print("DATA STATISTICS")
    print("="*60)
    
    print(f"\nTotal articles: {stats['total_articles']:,}")
    print(f"Total categories: {stats['total_categories']}")
    
    if stats['date_range']['earliest']:
        print(f"\nDate range:")
        print(f"  Earliest: {stats['date_range']['earliest']}")
        print(f"  Latest: {stats['date_range']['latest']}")
    
    print(f"\nArticles per category:")
    sorted_cats = sorted(stats['categories'].items(), 
                        key=lambda x: x[1], 
                        reverse=True)
    
    for category, count in sorted_cats:
        percentage = (count / stats['total_articles']) * 100
        print(f"  {category:25s}: {count:6,} ({percentage:5.1f}%)")
    
    print("\n" + "="*60)


def print_search_results(results, limit=10):
    """Print search results."""
    print(f"\nFound {len(results)} matching articles")
    
    if not results:
        return
    
    print(f"\nShowing first {min(limit, len(results))} results:\n")
    
    for i, result in enumerate(results[:limit], 1):
        article = result['article']
        category = result['category']
        
        print(f"{i}. [{category}] {article.get('title', 'No title')}")
        print(f"   URL: {article.get('url', 'No URL')}")
        print(f"   Date: {article.get('scraped_at', 'Unknown')}")
        print(f"   Preview: {article.get('text', '')[:150]}...")
        print()
    
    if len(results) > limit:
        print(f"... and {len(results) - limit} more results")


def export_results(results, output_file):
    """Export search results to a JSON file."""
    articles_only = [r['article'] for r in results]
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(articles_only, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ Exported {len(results)} articles to '{output_file}'")


def main():
    parser = argparse.ArgumentParser(
        description='Query and search articles across category files'
    )
    parser.add_argument(
        '--data-dir',
        default='data',
        help='Directory containing category JSON files (default: data)'
    )
    parser.add_argument(
        '--stats',
        action='store_true',
        help='Show statistics about the data'
    )
    parser.add_argument(
        '--search',
        help='Search keyword (searches in title and text)'
    )
    parser.add_argument(
        '--category',
        help='Filter by specific category'
    )
    parser.add_argument(
        '--export',
        help='Export results to JSON file'
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=10,
        help='Limit number of results to display (default: 10)'
    )
    
    args = parser.parse_args()
    
    # Load all category data
    category_data = load_all_categories(args.data_dir)
    
    if not category_data:
        return 1
    
    # Show statistics
    if args.stats:
        stats = get_statistics(category_data)
        print_statistics(stats)
        return 0
    
    # Search
    if args.search:
        results = search_articles(category_data, args.search, args.category)
        print_search_results(results, args.limit)
        
        if args.export:
            export_results(results, args.export)
        
        return 0
    
    # If no action specified, show stats
    if not args.stats and not args.search:
        stats = get_statistics(category_data)
        print_statistics(stats)
    
    return 0


if __name__ == '__main__':
    exit(main())
