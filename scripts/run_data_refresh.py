import logging
import sys

# Configure logging at the root level so all modules use it
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from src.ingestion.scraper import scrape_all_schemes
from src.ingestion.cleaner import clean_all_documents

def main():
    logger.info("==========================================")
    logger.info("   STARTING SCHEDULED DATA REFRESH")
    logger.info("==========================================")
    
    try:
        print("\nStep 1/2: Scraping 20 Groww URLs...")
        scrape_all_schemes(force_refresh=True)

        print("\nStep 2/2: Cleaning documents...")
        clean_all_documents()

        print("\n✅ Data refresh complete! Raw and processed JSONs updated.")
        logger.info("Pipeline execution finished successfully.")

    except Exception as e:
        logger.exception(f"Pipeline failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
