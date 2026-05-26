"""
Generate comparative analytics between Femina Forum and Sloboden Pechat datasets.
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

def get_dataset_stats(records, name):
    """Get basic statistics about dataset."""
    return {
        "name": name,
        "total_records": len(records),
        "has_content": sum(1 for r in records if r.get('content') or r.get('text'))
    }

def create_comparative_visualizations(output_dir="scripts/output"):
    """Create comparative visualizations between both scrapers."""
    Path(output_dir).mkdir(exist_ok=True, parents=True)
    
    # Load both datasets
    print("Loading Femina Forum dataset...")
    femina_records = load_dataset("../femina-forum scraper/data/femina_forum_dataset_cleaned.json")
    
    print("Loading Sloboden Pechat dataset...")
    sloboden_records = load_dataset("data/sloboden_pechat_dataset.json")
    
    if not femina_records or not sloboden_records:
        print("Could not load one or both datasets")
        return
    
    # Get stats
    femina_stats = get_dataset_stats(femina_records, "Femina Forum")
    sloboden_stats = get_dataset_stats(sloboden_records, "Sloboden Pechat")
    
    print("\n" + "="*60)
    print("DATASET COMPARISON")
    print("="*60)
    print(f"Femina Forum:      {femina_stats['total_records']:,} records")
    print(f"Sloboden Pechat:   {sloboden_stats['total_records']:,} records")
    print(f"Total Combined:    {femina_stats['total_records'] + sloboden_stats['total_records']:,} records")
    print("="*60)
    
    # 1. Dataset size comparison
    plt.figure(figsize=(10, 6))
    names = [femina_stats['name'], sloboden_stats['name']]
    sizes = [femina_stats['total_records'], sloboden_stats['total_records']]
    colors = ['#FF69B4', '#4169E1']
    bars = plt.bar(names, sizes, color=colors, width=0.6)
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height):,}',
                ha='center', va='bottom', fontsize=12, fontweight='bold')
    
    plt.ylabel('Number of Records', fontsize=12)
    plt.title('Dataset Size Comparison: Femina Forum vs Sloboden Pechat', 
              fontsize=14, fontweight='bold')
    plt.ylim(0, max(sizes) * 1.15)
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    output_file = f"{output_dir}/dataset_comparison.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\nSaved: {output_file}")
    plt.close()
    
    # 2. Pie chart showing proportion
    plt.figure(figsize=(10, 8))
    plt.pie(sizes, labels=names, autopct='%1.1f%%', 
            colors=colors, startangle=90, textprops={'fontsize': 12})
    plt.title('Data Distribution: Combined Dataset Composition', 
              fontsize=14, fontweight='bold')
    plt.tight_layout()
    output_file = f"{output_dir}/dataset_composition.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Saved: {output_file}")
    plt.close()
    
    # 3. Save comprehensive comparison stats
    comparison_file = f"{output_dir}/dataset_comparison_stats.txt"
    with open(comparison_file, 'w', encoding='utf-8') as f:
        f.write("DATASET COMPARISON REPORT\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*70 + "\n\n")
        
        f.write("FEMINA FORUM\n")
        f.write("-"*70 + "\n")
        f.write(f"Source:          https://forum.femina.mk/\n")
        f.write(f"Type:            Forum Discussions\n")
        f.write(f"Total Records:   {femina_stats['total_records']:,}\n")
        f.write(f"Records with Content: {femina_stats['has_content']:,}\n")
        f.write(f"Percentage of Combined: {(femina_stats['total_records']/(femina_stats['total_records']+sloboden_stats['total_records'])*100):.1f}%\n\n")
        
        f.write("SLOBODEN PECHAT\n")
        f.write("-"*70 + "\n")
        f.write(f"Source:          https://www.slobodenpecat.mk/\n")
        f.write(f"Type:            News Articles (WordPress API)\n")
        f.write(f"Total Records:   {sloboden_stats['total_records']:,}\n")
        f.write(f"Records with Content: {sloboden_stats['has_content']:,}\n")
        f.write(f"Percentage of Combined: {(sloboden_stats['total_records']/(femina_stats['total_records']+sloboden_stats['total_records'])*100):.1f}%\n\n")
        
        f.write("COMBINED DATASET\n")
        f.write("-"*70 + "\n")
        f.write(f"Total Records:   {femina_stats['total_records'] + sloboden_stats['total_records']:,}\n")
        f.write(f"Total with Content: {femina_stats['has_content'] + sloboden_stats['has_content']:,}\n")
        f.write(f"Data Types:      Forum Discussions + News Articles\n")
        f.write(f"Coverage:        Macedonian Language Text\n")
    
    print(f"Saved: {comparison_file}")
    print("\n" + "="*60)
    print("Comparative analysis complete!")
    print("="*60)

if __name__ == "__main__":
    create_comparative_visualizations()
