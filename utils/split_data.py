"""
Split the large slobodenpecat_data.json file into category-based files.

This is a one-time migration script to reorganize data from a single
large JSON file into smaller, category-specific files.

Usage:
    python utils/split_data.py [--input path] [--output-dir path]
"""

import json
import os
import shutil
import argparse
from datetime import datetime
from collections import defaultdict


def backup_original_file(input_file):
    """Create a backup of the original file with timestamp."""
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found!")
        return False
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"{input_file}.backup_{timestamp}"
    
    print(f"Creating backup: {backup_file}")
    shutil.copy2(input_file, backup_file)
    print(f"✓ Backup created successfully")
    return True


def load_articles(input_file):
    """Load articles from the large JSON file."""
    print(f"\nLoading articles from {input_file}...")
    print(f"File size: {os.path.getsize(input_file) / (1024*1024):.2f} MB")
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            articles = json.load(f)
        print(f"✓ Loaded {len(articles):,} articles")
        return articles
    except json.JSONDecodeError as e:
        print(f"Error: Failed to parse JSON file - {e}")
        return None
    except Exception as e:
        print(f"Error: Failed to load file - {e}")
        return None


def group_by_category(articles):
    """Group articles by their categories."""
    print("\nGrouping articles by category...")
    category_groups = defaultdict(list)
    
    for article in articles:
        categories = article.get('categories', [])
        
        # If article has no categories, put it in 'uncategorized'
        if not categories:
            category_groups['uncategorized'].append(article)
            continue
        
        # Add article to each of its categories
        for category in categories:
            category_groups[category].append(article)
    
    print(f"✓ Grouped into {len(category_groups)} categories")
    return category_groups


def save_category_files(category_groups, output_dir):
    """Save each category to its own JSON file."""
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    print(f"\nSaving category files to '{output_dir}/'...")
    
    stats = {}
    
    for category, articles in category_groups.items():
        output_file = os.path.join(output_dir, f"{category}.json")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(articles, f, ensure_ascii=False, indent=2)
        
        file_size = os.path.getsize(output_file) / (1024*1024)  # MB
        stats[category] = {
            'count': len(articles),
            'size_mb': file_size
        }
        
        print(f"  ✓ {category}.json: {len(articles):,} articles ({file_size:.2f} MB)")
    
    return stats


def print_statistics(original_count, category_stats):
    """Print summary statistics."""
    print("\n" + "="*60)
    print("SPLIT COMPLETE - STATISTICS")
    print("="*60)
    
    total_articles = sum(s['count'] for s in category_stats.values())
    total_size = sum(s['size_mb'] for s in category_stats.values())
    
    print(f"\nOriginal file: {original_count:,} articles")
    print(f"Total after split: {total_articles:,} articles")
    
    if total_articles > original_count:
        duplicates = total_articles - original_count
        print(f"Note: {duplicates:,} articles appear in multiple categories")
    
    print(f"\nTotal storage: {total_size:.2f} MB across {len(category_stats)} files")
    print(f"Average file size: {total_size/len(category_stats):.2f} MB")
    
    print("\nCategory breakdown:")
    # Sort by article count (descending)
    sorted_categories = sorted(category_stats.items(), 
                               key=lambda x: x[1]['count'], 
                               reverse=True)
    
    for category, stats in sorted_categories:
        print(f"  {category:25s}: {stats['count']:6,} articles ({stats['size_mb']:6.2f} MB)")
    
    print("\n" + "="*60)


def main():
    parser = argparse.ArgumentParser(
        description='Split large JSON file into category-based files'
    )
    parser.add_argument(
        '--input',
        default='slobodenpecat_data.json',
        help='Input JSON file (default: slobodenpecat_data.json)'
    )
    parser.add_argument(
        '--output-dir',
        default='data',
        help='Output directory for category files (default: data)'
    )
    parser.add_argument(
        '--no-backup',
        action='store_true',
        help='Skip creating backup of original file'
    )
    
    args = parser.parse_args()
    
    print("="*60)
    print("SPLITTING LARGE JSON FILE INTO CATEGORIES")
    print("="*60)
    
    # Create backup
    if not args.no_backup:
        if not backup_original_file(args.input):
            return 1
    
    # Load articles
    articles = load_articles(args.input)
    if articles is None:
        return 1
    
    original_count = len(articles)
    
    # Group by category
    category_groups = group_by_category(articles)
    
    # Save category files
    stats = save_category_files(category_groups, args.output_dir)
    
    # Print statistics
    print_statistics(original_count, stats)
    
    print("\n✓ Split completed successfully!")
    print(f"  Next steps:")
    print(f"  1. Verify the files in '{args.output_dir}/' directory")
    print(f"  2. Run the refactored scrape.py to test")
    print(f"  3. Archive or delete the original file once confident")
    
    return 0


if __name__ == '__main__':
    exit(main())
