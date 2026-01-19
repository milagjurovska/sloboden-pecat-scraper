"""
Quick script to count total articles across all category files.
"""

import json
import os
from pathlib import Path

DATA_DIR = "data"

def count_articles():
    total = 0
    category_counts = {}
    
    data_path = Path(DATA_DIR)
    if not data_path.exists():
        print(f"Error: {DATA_DIR} directory not found!")
        return
    
    json_files = sorted(data_path.glob("*.json"))
    
    if not json_files:
        print(f"No JSON files found in {DATA_DIR}/")
        return
    
    print(f"Counting articles in {len(json_files)} files...\n")
    
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                articles = json.load(f)
                count = len(articles)
                category_counts[json_file.stem] = count
                total += count
                print(f"  {json_file.name:30s}: {count:,} articles")
        except Exception as e:
            print(f"  {json_file.name:30s}: ERROR - {e}")
    
    print("\n" + "="*60)
    print(f"TOTAL ARTICLES: {total:,}")
    print("="*60)
    
    print("\nTop 5 categories by size:")
    sorted_cats = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    for category, count in sorted_cats:
        percentage = (count / total) * 100
        print(f"  {category:25s}: {count:,} ({percentage:.1f}%)")

if __name__ == "__main__":
    count_articles()
