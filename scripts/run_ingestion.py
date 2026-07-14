import logging
import sys

# Configure logging at the root level so all modules use it
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from src.ingestion.scraper import scrape_all_schemes
from src.ingestion.cleaner import clean_all_documents
from src.ingestion.chunker import chunk_all_documents
from src.ingestion.embedder import embed_and_store_all

def main():
    logger.info("==========================================")
    logger.info("   STARTING END-TO-END INGESTION PIPELINE")
    logger.info("==========================================")
    
    try:
        print("\nStep 1/4: Scraping 20 Groww URLs...")
        scrape_all_schemes()

        print("\nStep 2/4: Cleaning documents...")
        clean_all_documents()

        print("\nStep 3/4: Chunking documents...")
        chunks = chunk_all_documents()

        if not chunks:
            logger.error("No chunks generated. Aborting pipeline.")
            sys.exit(1)

        print(f"\nStep 4/4: Embedding & indexing {len(chunks)} chunks...")
        embed_and_store_all(chunks)

        print("\n✅ Ingestion pipeline complete!")
        logger.info("Pipeline execution finished successfully.")

    except Exception as e:
        logger.exception(f"Pipeline failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
