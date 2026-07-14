import chromadb
from langchain_community.embeddings import HuggingFaceEmbeddings

def main():
    print("Loading HuggingFace embedding model (BAAI/bge-small-en-v1.5)...")
    embeddings = HuggingFaceEmbeddings(
        model_name="BAAI/bge-small-en-v1.5",
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )

    print("Connecting to local ChromaDB vectorstore...")
    client = chromadb.PersistentClient(path="./data/vectorstore")
    collection = client.get_collection(name="mutual_fund_faq")

    query = "What is the exit load for HDFC Mid Cap fund?"
    print(f"\n=============================================")
    print(f"QUERY: {query}")
    print(f"=============================================")

    # Embed the user query using the same model
    query_embedding = embeddings.embed_query(query)

    # Perform similarity search
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=1,
    )

    print("\n--- TOP MATCHING CHUNK ---")
    if results['documents'] and len(results['documents'][0]) > 0:
        print(results['documents'][0][0])
        print("\n--- METADATA ---")
        print(results['metadatas'][0][0])
    else:
        print("No results found.")

if __name__ == "__main__":
    main()
