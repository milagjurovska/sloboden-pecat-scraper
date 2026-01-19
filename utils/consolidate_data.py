"""
Consolidate category-based JSON files back into a single file.

This is an optional utility to merge all category files back into one
large JSON file if needed for backup, export, or other purposes.

Usage:
    python utils/consolidate_data.py [--output consolidated.json]
"""

import json
import os
import argparse
from datetime import datetime


def load_all_categories(data_dir):
    """Load all category files."""
    if not os.path.exists(data_dir):
        print(f"Error: Data directory '{data_dir}' not found!")
        return None
    
    all_articles = []
    seen_urls = set()
    category_counts = {}
    duplicate_count = 0
    
    json_files = sorted([f for f in os.listdir(data_dir) if f.endswith('.json')])
    
    print(f"Loading {len(json_files)} category files from '{data_dir}/'...")
    
    for filename in json_files:
        category_name = filename[:-5]  # Remove .json extension
        filepath = os.path.join(data_dir, filename)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                articles = json.load(f)
            
            # Count articles before deduplication
            original_count = len(articles)
            new_count = 0
            
            # Add articles, removing duplicates by URL
            for article in articles:
                url = article.get('url')
                if url and url not in seen_urls:
                    all_articles.append(article)
                    seen_urls.add(url)
                    new_count += 1
                elif url:
                    duplicate_count += 1
            
            category_counts[category_name] = {
                'original': original_count,
                'unique': new_count
            }
            
            print(f"  ✓ {category_name}: {original_count} articles ({new_count} unique)")
            
        except Exception as e:
            print(f"  ✗ Failed to load {filename}: {e}")
    
    return all_articles, category_counts, duplicate_count


def save_consolidated_file(articles, output_file):
    """Save consolidated articles to a single JSON file."""
    print(f"\nSaving {len(articles):,} articles to '{output_file}'...")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
    
    file_size = os.path.getsize(output_file) / (1024*1024)  # MB
    print(f"✓ Saved successfully ({file_size:.2f} MB)")


def print_statistics(category_counts, total_articles, duplicates):
    """Print consolidation statistics."""
    print("\n" + "="*60)
    print("CONSOLIDATION STATISTICS")
    print("="*60)
    
    total_original = sum(c['original'] for c in category_counts.values())
    total_unique = sum(c['unique'] for c in category_counts.values())
    
    print(f"\nTotal articles across all categories: {total_original:,}")
    print(f"Unique articles (after deduplication): {total_unique:,}")
    print(f"Duplicates removed: {duplicates:,}")
    
    print(f"\nCategory breakdown:")
    for category, counts in sorted(category_counts.items()):
        dup = counts['original'] - counts['unique']
        print(f"  {category:25s}: {counts['original']:6,} total, "
              f"{counts['unique']:6,} unique, {dup:4,} duplicates")
    
    print("\n" + "="*60)


def main():
    parser = argparse.ArgumentParser(
        description='Consolidate category files into a single JSON file'
    )
    parser.add_argument(
        '--data-dir',
        default='data',
        help='Directory containing category JSON files (default: data)'
    )
    parser.add_argument(
        '--output',
        default='consolidated_data.json',
        help='Output file for consolidated data (default: consolidated_data.json)'
    )
    
    args = parser.parse_args()
    
    print("="*60)
    print("CONSOLIDATING CATEGORY FILES")
    print("="*60)
    print()
    
    # Load all categories
    result = load_all_categories(args.data_dir)
    if result is None:
        return 1
    
    all_articles, category_counts, duplicate_count = result
    
    if not all_articles:
        print("\nError: No articles found!")
        return 1
    
    # Save consolidated file
    save_consolidated_file(all_articles, args.output)
    
    # Print statistics
    print_statistics(category_counts, len(all_articles), duplicate_count)
    
    print(f"\n✓ Consolidation completed successfully!")
    
    return 0


if __name__ == '__main__':
    exit(main())
