"""
Generate content quality and size analytics for both datasets.
"""

import json
from pathlib import Path
from datetime import datetime

def load_dataset(filepath):
    """Load JSON dataset."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading dataset: {e}")
        return []

def count_words(text):
    """Count words in text."""
    if not text:
        return 0
    return len(text.split())

def analyze_content_quality(records, dataset_name):
    """Analyze content quality metrics."""
    total_records = len(records)
    records_with_content = 0
    total_chars = 0
    total_words = 0
    content_lengths = []
    
    for record in records:
        content = None
        if isinstance(record, dict):
            if 'content' in record:
                content = record.get('content', '')
            elif 'text' in record:
                content = record.get('text', '')
        
        if content and content.strip():
            records_with_content += 1
            char_count = len(content)
            word_count = count_words(content)
            total_chars += char_count
            total_words += word_count
            content_lengths.append(len(content.split()))
    
    avg_words = total_words / records_with_content if records_with_content > 0 else 0
    avg_chars = total_chars / records_with_content if records_with_content > 0 else 0
    
    stats = {
        "dataset_name": dataset_name,
        "total_records": total_records,
        "records_with_content": records_with_content,
        "empty_records": total_records - records_with_content,
        "total_characters": total_chars,
        "total_words": total_words,
        "avg_words_per_record": round(avg_words, 2),
        "avg_chars_per_record": round(avg_chars, 2),
    }
    
    return stats

def generate_report(femina_path, sloboden_path, output_dir="scripts/output"):
    """Generate comprehensive content quality report."""
    Path(output_dir).mkdir(exist_ok=True, parents=True)
    
    print("Loading and analyzing Femina Forum dataset...")
    femina_records = load_dataset(femina_path)
    femina_stats = analyze_content_quality(femina_records, "Femina Forum")
    
    print("Loading and analyzing Sloboden Pechat dataset...")
    sloboden_records = load_dataset(sloboden_path)
    sloboden_stats = analyze_content_quality(sloboden_records, "Sloboden Pechat")
    
    # Generate report
    report_file = f"{output_dir}/content_quality_analysis.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("DATASET CONTENT QUALITY ANALYSIS\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*70 + "\n\n")
        
        for stats in [femina_stats, sloboden_stats]:
            f.write(f"{stats['dataset_name'].upper()}\n")
            f.write("-"*70 + "\n")
            f.write(f"Total Records:           {stats['total_records']:,}\n")
            f.write(f"Records with Content:    {stats['records_with_content']:,}\n")
            f.write(f"Empty Records:           {stats['empty_records']:,}\n")
            f.write(f"Content Fill Rate:       {(stats['records_with_content']/stats['total_records']*100):.1f}%\n\n")
            f.write(f"Total Characters:        {stats['total_characters']:,}\n")
            f.write(f"Total Words:             {stats['total_words']:,}\n")
            f.write(f"Avg Words per Record:    {stats['avg_words_per_record']}\n")
            f.write(f"Avg Characters/Record:   {stats['avg_chars_per_record']}\n")
            f.write("\n")
        
        # Combined summary
        combined_records = femina_stats['total_records'] + sloboden_stats['total_records']
        combined_words = femina_stats['total_words'] + sloboden_stats['total_words']
        combined_chars = femina_stats['total_characters'] + sloboden_stats['total_characters']
        
        f.write("COMBINED DATASET SUMMARY\n")
        f.write("-"*70 + "\n")
        f.write(f"Total Records:           {combined_records:,}\n")
        f.write(f"Total Words:             {combined_words:,}\n")
        f.write(f"Total Characters:        {combined_chars:,}\n")
        f.write(f"Average Words/Record:    {round(combined_words/combined_records, 2)}\n\n")
        
        f.write("DATA COMPOSITION\n")
        f.write("-"*70 + "\n")
        f.write(f"Femina Forum:   {femina_stats['total_records']:,} records ({femina_stats['total_records']/combined_records*100:.1f}%)\n")
        f.write(f"Sloboden Pechat: {sloboden_stats['total_records']:,} records ({sloboden_stats['total_records']/combined_records*100:.1f}%)\n")
    
    print(f"Saved: {report_file}")
    
    # Print summary to console
    print("\n" + "="*70)
    print("CONTENT QUALITY SUMMARY")
    print("="*70)
    print(f"\nFEMINA FORUM:")
    print(f"  Records: {femina_stats['total_records']:,}")
    print(f"  Words: {femina_stats['total_words']:,}")
    print(f"  Avg words/record: {femina_stats['avg_words_per_record']}")
    
    print(f"\nSLOBODEN PECHAT:")
    print(f"  Records: {sloboden_stats['total_records']:,}")
    print(f"  Words: {sloboden_stats['total_words']:,}")
    print(f"  Avg words/record: {sloboden_stats['avg_words_per_record']}")
    
    print(f"\nCOMBINED:")
    print(f"  Total Records: {combined_records:,}")
    print(f"  Total Words: {combined_words:,}")
    print("="*70)

if __name__ == "__main__":
    # For Sloboden Pechat directory
    femina_path = "../femina-forum scraper/data/femina_forum_dataset_cleaned.json"
    sloboden_path = "data/sloboden_pechat_dataset.json"
    
    generate_report(femina_path, sloboden_path)
