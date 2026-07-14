import chromadb

def main():
    print("Connecting to local ChromaDB vectorstore...")
    client = chromadb.PersistentClient(path="./data/vectorstore")
    collection = client.get_collection(name="mutual_fund_faq")

    # Fetch exactly 1 document with its embedding
    # We include 'embeddings' explicitly because Chroma doesn't return them by default on get()
    results = collection.get(
        limit=1,
        include=["documents", "metadatas", "embeddings"]
    )

    if not results['documents']:
        print("No documents found in the vectorstore.")
        return

    doc_text = results['documents'][0]
    metadata = results['metadatas'][0]
    embedding = results['embeddings'][0]

    print("\n==========================================")
    print("   CHUNKS & EMBEDDINGS VIEWER")
    print("==========================================\n")
    
    print(f"--- CHUNK INFO ---")
    print(f"ID: {results['ids'][0]}")
    print(f"Scheme: {metadata.get('scheme_name')}")
    print(f"Type: {metadata.get('chunk_type')}")
    
    print(f"\n--- TEXT CONTENT ---")
    print(doc_text[:200] + "...\n(Text truncated for brevity)")
    
    print(f"\n--- EMBEDDING VECTOR ---")
    print(f"Vector Dimensions (Size): {len(embedding)}")
    print(f"First 10 values of the vector:")
    
    # Print just the first 10 floating point numbers nicely formatted
    for i, val in enumerate(embedding[:10]):
        print(f"  [{i}]: {val:.6f}")
    
    print("  ... (and so on)")

if __name__ == "__main__":
    main()
