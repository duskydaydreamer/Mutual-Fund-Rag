import logging
from pathlib import Path
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# Import the chunker function we just built
from src.ingestion.chunker import chunk_all_documents

logger = logging.getLogger(__name__)

if not logger.hasHandlers():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

VECTORSTORE_PATH = "./data/vectorstore"
COLLECTION_NAME = "mutual_fund_faq"

def enrich_chunks_with_context(chunks: list) -> list:
    """
    Prepends the scheme name and chunk type to the text of each chunk.
    This ensures the embedding model (and later the LLM) knows exactly
    which fund and topic this chunk belongs to.
    """
    enriched_chunks = []
    for chunk in chunks:
        scheme_name = chunk.metadata.get("scheme_name", "Unknown Fund")
        chunk_type = chunk.metadata.get("chunk_type", "general")
        
        # Prepend context
        context_header = f"Fund: {scheme_name} | Topic: {chunk_type}\n\n"
        chunk.page_content = context_header + chunk.page_content
        
        enriched_chunks.append(chunk)
        
    return enriched_chunks

def embed_and_store_all(chunks: list):
    """
    Generates embeddings for all chunks and stores them in ChromaDB.
    """
    if not chunks:
        logger.warning("No chunks provided to embedder.")
        return

    logger.info("Enriching chunks with contextual headers...")
    enriched_chunks = enrich_chunks_with_context(chunks)

    logger.info("Loading HuggingFace embedding model (BAAI/bge-small-en-v1.5)...")
    # This will download the model weights on the first run
    embeddings = HuggingFaceEmbeddings(
        model_name="BAAI/bge-small-en-v1.5",
        model_kwargs={'device': 'cpu'}, # Force CPU to avoid sandbox/MPS issues
        encode_kwargs={'normalize_embeddings': True} # BGE models perform best with normalized embeddings
    )

    logger.info(f"Initializing ChromaDB at {VECTORSTORE_PATH}...")
    Path(VECTORSTORE_PATH).mkdir(parents=True, exist_ok=True)
    
    # Create or update the vectorstore
    vectorstore = Chroma.from_documents(
        documents=enriched_chunks,
        embedding=embeddings,
        persist_directory=VECTORSTORE_PATH,
        collection_name=COLLECTION_NAME,
        collection_metadata={"hnsw:space": "cosine"} # BGE uses cosine similarity
    )
    
    # Langchain Chroma automatically persists when using from_documents with persist_directory
    vectorstore.persist()
    
    logger.info(f"✅ Successfully embedded and stored {len(enriched_chunks)} chunks in ChromaDB!")

if __name__ == "__main__":
    logger.info("Starting Phase 3.3: Embedding")
    # 1. Get all chunks
    all_chunks = chunk_all_documents()
    
    # 2. Embed and store
    embed_and_store_all(all_chunks)
