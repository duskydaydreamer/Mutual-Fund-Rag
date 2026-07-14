"""
Inspect the actual ChromaDB collection: chunk count, metadata, scheme names,
chunk type distribution, and a live query test.
"""
import sys
import chromadb
from collections import Counter

client = chromadb.PersistentClient(path="./data/vectorstore")
collection = client.get_collection("mutual_fund_faq")

print(f"=== ChromaDB Collection: mutual_fund_faq ===")
print(f"Total chunks stored: {collection.count()}")
print()

# ---- Sample documents ----
results = collection.get(limit=15, include=["documents", "metadatas"])
print("=== Sample Documents (first 15) ===")
for i, (doc, meta) in enumerate(zip(results["documents"], results["metadatas"])):
    print(f"\n--- Chunk {i+1} ---")
    print(f"  chunk_id:    {meta.get('chunk_id')}")
    print(f"  scheme_name: {meta.get('scheme_name')}")
    print(f"  chunk_type:  {meta.get('chunk_type')}")
    print(f"  amc:         {meta.get('amc')}")
    print(f"  doc preview: {doc[:150]}")

# ---- All scheme names ----
all_metas = collection.get(include=["metadatas"])["metadatas"]
scheme_names = sorted(set(m["scheme_name"] for m in all_metas))
print(f"\n=== All Unique scheme_name values ({len(scheme_names)}) ===")
for s in scheme_names:
    print(f"  {repr(s)}")

# ---- chunk_type distribution ----
type_counts = Counter(m["chunk_type"] for m in all_metas)
print(f"\n=== chunk_type distribution ===")
for ct, n in sorted(type_counts.items(), key=lambda x: -x[1]):
    print(f"  {ct:25s}: {n}")

# ---- AMC distribution ----
amc_counts = Counter(m["amc"] for m in all_metas)
print(f"\n=== AMC distribution ===")
for amc, n in sorted(amc_counts.items()):
    print(f"  {amc:35s}: {n}")

# ---- Live query test with manual embeddings ----
print("\n=== Live Query Test: 'expense ratio of HDFC Mid Cap Fund' ===")
from langchain_community.embeddings import HuggingFaceEmbeddings
embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-small-en-v1.5",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True},
)

query = "expense ratio of HDFC Mid Cap Fund"
context_q = "Fund: HDFC Mid Cap Fund Direct Growth | Topic: overview\n\nexpense ratio of HDFC Mid Cap Fund"
qe = embeddings.embed_query(context_q)

res = collection.query(
    query_embeddings=[qe],
    n_results=8,
    include=["documents", "metadatas", "distances"],
)
print(f"Top 8 results (cosine distance, lower=better):")
for doc, meta, dist in zip(res["documents"][0], res["metadatas"][0], res["distances"][0]):
    print(f"  dist={dist:.4f}  [{meta['chunk_type']:20s}]  {meta['scheme_name']}  |  {doc[:80]}")
