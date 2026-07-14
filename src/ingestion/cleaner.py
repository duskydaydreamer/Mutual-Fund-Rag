import json
import logging
import re
from pathlib import Path
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# Basic logging if not configured
if not logger.hasHandlers():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def remove_boilerplate(text: str) -> str:
    """Removes common ads, cookie notices, or prompts."""
    boilers = [
        r"(?i)download app",
        r"(?i)cookie notice",
        r"(?i)accept cookies",
        r"(?i)terms and conditions",
        r"(?i)privacy policy",
        r"(?i)all rights reserved",
    ]
    for pattern in boilers:
        text = re.sub(pattern, "", text)
    return text

def remove_duplicates(text: str) -> str:
    """Removes duplicate sentences or text blocks."""
    # Split by common sentence endings
    sentences = re.split(r'(?<=[.!?]) +', text)
    seen = set()
    unique_sentences = []
    for s in sentences:
        s_clean = s.strip()
        if s_clean and s_clean not in seen:
            seen.add(s_clean)
            unique_sentences.append(s_clean)
    return ' '.join(unique_sentences)

def clean_text(text: str) -> str:
    """Apply all text cleaning steps as per Phase 3.1 requirements."""
    if not text:
        return ""
    
    # 1. Strip residual HTML tags
    text = BeautifulSoup(text, "lxml").get_text(separator=" ")
    
    # 2. Fix encoding issues (e.g., standardizing ₹ symbol)
    text = text.replace("â‚¹", "₹").replace("Rs.", "₹")
    
    # 3. Standardize number formats (ensure no space after ₹)
    text = re.sub(r'₹\s+', '₹', text)
    
    # 4. Remove boilerplate
    text = remove_boilerplate(text)
    
    # 5. Remove duplicates
    text = remove_duplicates(text)
    
    # 6. Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def clean_document(raw_doc: dict) -> dict:
    """Cleans a single document dictionary."""
    cleaned = raw_doc.copy()
    
    # Clean structured data values
    if "structured_data" in cleaned:
        for k, v in cleaned["structured_data"].items():
            cleaned["structured_data"][k] = clean_text(str(v))
            
    # Clean full page text
    if "full_page_text" in cleaned:
        cleaned["full_page_text"] = clean_text(cleaned["full_page_text"])
        
    return cleaned

def clean_all_documents():
    """Reads all raw JSON files, cleans them, and saves to processed folder."""
    raw_dir = Path("data/raw")
    processed_dir = Path("data/processed")
    processed_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info("Starting data cleaning (Phase 3.1)...")
    
    raw_files = list(raw_dir.glob("*.json"))
    if not raw_files:
        logger.warning(f"No JSON files found in {raw_dir}. Please run scraping first.")
        return
        
    for raw_file in raw_files:
        try:
            with open(raw_file, 'r', encoding='utf-8') as f:
                raw_doc = json.load(f)
                
            cleaned_doc = clean_document(raw_doc)
            
            output_file = processed_dir / raw_file.name
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(cleaned_doc, f, indent=2, ensure_ascii=False)
                
            logger.info(f"Cleaned and saved {raw_file.name}")
                
        except Exception as e:
            logger.error(f"Failed to clean {raw_file.name}: {e}")
            
    logger.info("✅ Cleaning complete. Files saved to data/processed/")

if __name__ == "__main__":
    clean_all_documents()
