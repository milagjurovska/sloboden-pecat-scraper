import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path to import vezilka_schemas
sys.path.append(os.getcwd())

try:
    from vezilka_schemas import Record, RecordMeta, RecordType
except ImportError:
    print("Error: vezilka_schemas not found. Please install requirements first.")
    sys.path.append(r"c:\Users\milam\OneDrive - ALS Bobi\Desktop\femina-forum scraper")
    from vezilka_schemas import Record, RecordMeta, RecordType

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def migrate_data(input_file: str, output_file: str):
    input_path = Path(input_file)
    output_path = Path(output_file)

    if not input_path.exists():
        logger.error(f"Input file {input_file} does not exist.")
        return

    logger.info(f"Loading legacy data from {input_file}...")
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            legacy_data = json.load(f)
    except Exception as e:
        logger.error(f"Failed to load legacy data: {e}")
        return

    logger.info(f"Loaded {len(legacy_data)} records. Starting transformation...")

    standardized_records = []
    seen_ids = set()

    for i, item in enumerate(legacy_data):
        try:
            # Map legacy fields to Record
            post_id = str(item.get('page_id') or item.get('id') or i)
            
            # Skip duplicates if any
            if post_id in seen_ids:
                continue
            seen_ids.add(post_id)

            content = item.get('text') or item.get('content', {}).get('rendered', '')
            url = item.get('url') or item.get('link', '')
            title = item.get('title', '')
            if isinstance(title, dict):
                title = title.get('rendered', '')
            
            categories = item.get('categories', [])
            if not isinstance(categories, list):
                categories = [categories]
            
            scraped_at_str = item.get('scraped_at')
            scraped_at = datetime.now()
            if scraped_at_str:
                try:
                    scraped_at = datetime.fromisoformat(scraped_at_str)
                except:
                    pass

            published_at_str = item.get('date')
            published_at = None
            if published_at_str:
                try:
                    published_at = datetime.fromisoformat(published_at_str)
                except:
                    pass

            record_meta = RecordMeta(
                source="https://www.slobodenpecat.mk/",
                url=url,
                tags=categories,
                labels=[],
                scraped_at=scraped_at,
                published_at=published_at
            )
            
            record = Record(
                id=post_id,
                text=content,
                type=RecordType.NARRATIVE,
                last_modified_at=datetime.now(),
                meta=record_meta
            )
            
            standardized_records.append(record.model_dump(mode="json"))

            if (i + 1) % 5000 == 0:
                logger.info(f"Processed {i+1}/{len(legacy_data)} records...")

        except Exception as e:
            logger.warning(f"Error processing record at index {i}: {e}")

    logger.info(f"Transformation complete. Saving {len(standardized_records)} records to {output_file}...")
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(standardized_records, f, indent=2, ensure_ascii=False)

    # Save seen IDs as well
    seen_ids_file = output_path.parent / "sloboden_pechat_seen_ids.json"
    logger.info(f"Saving {len(seen_ids)} seen IDs to {seen_ids_file}...")
    with open(seen_ids_file, 'w', encoding='utf-8') as f:
        json.dump(sorted(list(seen_ids)), f, indent=2, ensure_ascii=False)

    logger.info("Migration successful!")

if __name__ == "__main__":
    input_file = "slobodenpecat_data.json"
    output_file = "data/sloboden_pechat_dataset.json"
    migrate_data(input_file, output_file)
