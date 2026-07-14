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

    print(f"\n--- Total chunks stored in Chroma: {collection.count()} ---")
    
    queries = [
        "expense ratio of HDFC Mid Cap Fund",
        "exit load for Parag Parikh ELSS Fund",
        "minimum SIP for ICICI Prudential Large Cap Fund",
        "fund manager of Motilal Oswal Midcap Fund",
        "what is the exit load"
    ]
    
    for query in queries:
        print(f"\n=============================================")
        print(f"QUERY: {query}")
        print(f"=============================================")
        query_embedding = embeddings.embed_query(query)
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=5,
            include=['documents', 'metadatas', 'distances']
        )
        
        for i in range(len(results['documents'][0])):
            doc = results['documents'][0][i]
            meta = results['metadatas'][0][i]
            dist = results['distances'][0][i]
            print(f"Result {i+1} (Distance: {dist:.4f}):")
            print(f"Metadata: {meta}")
            print(f"Snippet: {doc[:150]}...")
            print("-" * 30)

    # Now get 3 representative chunks
    print("\n=============================================")
    print("3 REPRESENTATIVE CHUNKS")
    print("=============================================")
    chunk_types = ['overview', 'exit_load_tax', 'holdings']
    for ct in chunk_types:
        res = collection.get(where={"chunk_type": ct}, limit=1)
        if res and res['documents']:
            print(f"\n--- Chunk Type: {ct} ---")
            print(f"Metadata: {res['metadatas'][0]}")
            print(f"Content:\n{res['documents'][0]}")
            
if __name__ == "__main__":
    main()
