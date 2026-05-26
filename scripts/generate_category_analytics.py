"""
Generate category distribution analytics and visualizations for Sloboden Pechat dataset.
"""

import json
import matplotlib.pyplot as plt
from pathlib import Path
from collections import Counter
from datetime import datetime

def load_dataset(filepath):
    """Load JSON dataset."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading dataset: {e}")
        return []

def analyze_categories(records):
    """Analyze category distribution in records."""
    categories = []
    for record in records:
        # Handle both old format (post_categories) and new format (meta.tags)
        if isinstance(record, dict):
            # New format
            if 'meta' in record and 'tags' in record['meta']:
                cat = record['meta']['tags']
            # Old format
            elif 'post_categories' in record:
                cat = record['post_categories']
            else:
                cat = "Unknown"
            
            if isinstance(cat, list) and cat:
                categories.extend(cat)
            elif isinstance(cat, str):
                categories.append(cat)
    
    return Counter(categories)

def create_visualizations(category_counts, output_dir="scripts/output"):
    """Create visualization charts."""
    Path(output_dir).mkdir(exist_ok=True)
    
    if not category_counts:
        print("No category data to visualize")
        return
    
    # Sort by count
    sorted_cats = dict(sorted(category_counts.items(), key=lambda x: x[1], reverse=True))
    
    # Top 15 categories
    top_n = 15
    top_cats = dict(list(sorted_cats.items())[:top_n])
    
    # 1. Bar chart - Top 15 categories
    plt.figure(figsize=(14, 8))
    categories = list(top_cats.keys())
    counts = list(top_cats.values())
    plt.barh(categories, counts, color='steelblue')
    plt.xlabel('Number of Posts', fontsize=12)
    plt.ylabel('Category', fontsize=12)
    plt.title('Sloboden Pechat - Top 15 Categories by Post Count', fontsize=14, fontweight='bold')
    plt.tight_layout()
    output_file = f"{output_dir}/sloboden_pechat_top_categories.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Saved: {output_file}")
    plt.close()
    
    # 2. Pie chart - Top 10 categories
    top_10 = dict(list(sorted_cats.items())[:10])
    plt.figure(figsize=(12, 8))
    plt.pie(top_10.values(), labels=top_10.keys(), autopct='%1.1f%%', startangle=90)
    plt.title('Sloboden Pechat - Top 10 Categories (Percentage Distribution)', 
              fontsize=14, fontweight='bold')
    plt.tight_layout()
    output_file = f"{output_dir}/sloboden_pechat_category_distribution.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Saved: {output_file}")
    plt.close()
    
    # 3. Statistics table
    total_posts = sum(category_counts.values())
    unique_categories = len(category_counts)
    
    stats = {
        "Total Posts": total_posts,
        "Unique Categories": unique_categories,
        "Average Posts per Category": round(total_posts / unique_categories, 2),
        "Top Category": list(sorted_cats.keys())[0],
        "Top Category Count": list(sorted_cats.values())[0]
    }
    
    print("\n" + "="*50)
    print("SLOBODEN PECHAT - CATEGORY STATISTICS")
    print("="*50)
    for key, value in stats.items():
        print(f"{key}: {value}")
    print("="*50)
    
    # Save stats to file
    stats_file = f"{output_dir}/sloboden_pechat_stats.txt"
    with open(stats_file, 'w', encoding='utf-8') as f:
        f.write(f"Sloboden Pechat Category Analytics\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*50 + "\n")
        for key, value in stats.items():
            f.write(f"{key}: {value}\n")
        f.write("="*50 + "\n\n")
        f.write("TOP 20 CATEGORIES:\n")
        for i, (cat, count) in enumerate(list(sorted_cats.items())[:20], 1):
            percentage = (count / total_posts) * 100
            f.write(f"{i:2d}. {cat:30s} {count:6d} posts ({percentage:5.2f}%)\n")
    
    print(f"Saved: {stats_file}")
    
    return stats

if __name__ == "__main__":
    # Load dataset
    dataset_path = "data/sloboden_pechat_dataset.json"
    print(f"Loading dataset from {dataset_path}...")
    records = load_dataset(dataset_path)
    
    if records:
        print(f"Loaded {len(records)} records")
        
        # Analyze categories
        category_counts = analyze_categories(records)
        print(f"Found {len(category_counts)} unique categories")
        
        # Create visualizations
        create_visualizations(category_counts)
    else:
        print("No records to analyze")
