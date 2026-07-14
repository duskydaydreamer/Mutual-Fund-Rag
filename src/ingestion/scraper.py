import json
import logging
import time
import random
from pathlib import Path
from datetime import datetime
from bs4 import BeautifulSoup
import requests
import re

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from src.config.constants import GROWW_URLS

logger = logging.getLogger(__name__)

# Basic logging if not configured globally yet
if not logger.hasHandlers():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_url_slug(url: str) -> str:
    """Extract slug from url."""
    return url.strip('/').split('/')[-1]

def extract_field(soup: BeautifulSoup, field_name: str) -> str:
    """Helper to extract structured data using heuristic text searches."""
    target = soup.find(text=re.compile(field_name, re.IGNORECASE))
    if target:
        parent = target.parent
        # Handle Table layouts (td/th)
        if parent.name in ['td', 'th']:
            next_td = parent.find_next_sibling(['td', 'th'])
            if next_td:
                return next_td.get_text(strip=True)
        # Handle Div/Span layouts
        elif parent.name in ['div', 'span']:
            next_sib = parent.find_next_sibling(['div', 'span'])
            if next_sib:
                return next_sib.get_text(strip=True)
            # Try parent's next sibling
            grand_next = parent.parent.find_next_sibling(['div', 'span', 'tr'])
            if grand_next:
                return grand_next.get_text(strip=True)
                
    return "N/A"

def get_html_with_selenium(url: str) -> str:
    """Fallback method to fetch HTML using headless Selenium."""
    logger.info(f"Falling back to Selenium for {url}")
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--window-size=1920x1080")
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
        # Wait until an h1 is present (indicates content loaded)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "h1"))
        )
        # Small delay to ensure dynamic data finishes rendering
        time.sleep(2)
        html = driver.page_source
        return html
    except Exception as e:
        logger.error(f"Selenium fallback failed for {url}: {e}")
        return ""
    finally:
        try:
            driver.quit()
        except:
            pass

def get_html(url: str) -> str:
    """Attempt requests first, fallback to selenium if content seems missing."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    
    html = response.text
    # Check for mutual fund data (h1 is a good indicator of loaded content)
    if "<h1" not in html.lower():
        selenium_html = get_html_with_selenium(url)
        if selenium_html:
            return selenium_html
            
    return html

def scrape_scheme_page(html: str, url: str) -> dict:
    """Scrapes structured details from a Groww scheme page HTML."""
    soup = BeautifulSoup(html, 'lxml')
    
    # Try to find scheme name from h1
    h1 = soup.find('h1')
    scheme_name = h1.get_text(strip=True) if h1 else get_url_slug(url).replace('-', ' ').title()
    
    # Try to determine AMC from scheme name
    amc = scheme_name.split()[0] + " Mutual Fund" if scheme_name else "Unknown AMC"
    
    # Category fallback
    category_elem = soup.find('a', text=re.compile(r'(Equity|Debt|Hybrid|Commodity)'))
    category = category_elem.get_text(strip=True) if category_elem else "Mutual Fund"
    
    structured_data = {
        "nav": extract_field(soup, "NAV"),
        "expense_ratio": extract_field(soup, "Expense Ratio"),
        "exit_load": extract_field(soup, "Exit Load"),
        "min_sip": extract_field(soup, "SIP"),
        "min_lumpsum": extract_field(soup, "Lumpsum"),
        "riskometer": extract_field(soup, "Risk"),
        "benchmark": extract_field(soup, "Benchmark"),
        "fund_manager": extract_field(soup, "Manager"),
        "lock_in": extract_field(soup, "Lock-in"),
        "aum": extract_field(soup, "Fund Size")
    }
    
    return {
        "source_url": url,
        "scheme_name": scheme_name,
        "amc": amc,
        "category": category,
        "scrape_date": datetime.now().strftime("%Y-%m-%d"),
        "structured_data": structured_data
    }

def scrape_full_page_text(html: str) -> str:
    """Extracts all readable text from the HTML body."""
    soup = BeautifulSoup(html, 'lxml')
    
    # Strip unnecessary boilerplate elements
    for element in soup(["script", "style", "nav", "footer", "aside"]):
        element.decompose()
        
    # Extract text with space separation
    text = soup.get_text(separator=' ')
    
    # Normalize whitespaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def scrape_all_schemes():
    """Iterates through all URLs and dumps scraped output into JSON files."""
    raw_dir = Path("data/raw")
    raw_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Starting to scrape {len(GROWW_URLS)} URLs.")
    
    for url in GROWW_URLS:
        slug = get_url_slug(url)
        output_file = raw_dir / f"{slug}.json"
        
        if output_file.exists():
            logger.info(f"Skipping {slug}, already scraped.")
            continue
            
        logger.info(f"Scraping {url}")
        
        try:
            html = get_html(url)
            
            # 1. Scrape structured data
            data = scrape_scheme_page(html, url)
            
            # 2. Scrape full body text
            data["full_page_text"] = scrape_full_page_text(html)
            
            # 3. Save to json file
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
            logger.info(f"Successfully saved {slug}.json")
            
        except Exception as e:
            logger.error(f"Failed to scrape {url}: {str(e)}")
            
        # Rate limit to avoid being blocked
        time.sleep(random.uniform(1.0, 3.0))

if __name__ == "__main__":
    scrape_all_schemes()
