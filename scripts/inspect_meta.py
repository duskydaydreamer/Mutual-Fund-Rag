"""
Metadata-only ChromaDB inspection — no embedding model needed.
"""
import chromadb
from collections import Counter

client = chromadb.PersistentClient(path="./data/vectorstore")
collection = client.get_collection("mutual_fund_faq")

print(f"=== ChromaDB: mutual_fund_faq ===")
print(f"Total chunks stored: {collection.count()}")

# ---- Sample 15 documents ----
results = collection.get(limit=15, include=["documents", "metadatas"])
print("\n=== Sample Documents (first 15) ===")
for i, (doc, meta) in enumerate(zip(results["documents"], results["metadatas"])):
    print(f"\n--- Chunk {i+1} ---")
    print(f"  chunk_id:    {meta.get('chunk_id')}")
    print(f"  scheme_name: {meta.get('scheme_name')}")
    print(f"  chunk_type:  {meta.get('chunk_type')}")
    print(f"  amc:         {meta.get('amc')}")
    print(f"  doc preview: {repr(doc[:160])}")

# ---- All unique scheme_name values ----
all_metas = collection.get(include=["metadatas"])["metadatas"]
scheme_names = sorted(set(m["scheme_name"] for m in all_metas))
print(f"\n=== All Unique scheme_name values ({len(scheme_names)}) ===")
for s in scheme_names:
    print(f"  {repr(s)}")

# ---- chunk_type distribution ----
type_counts = Counter(m["chunk_type"] for m in all_metas)
print(f"\n=== chunk_type distribution (total {sum(type_counts.values())}) ===")
for ct, n in sorted(type_counts.items(), key=lambda x: -x[1]):
    print(f"  {ct:25s}: {n}")

# ---- chunks per scheme ----
scheme_counts = Counter(m["scheme_name"] for m in all_metas)
print(f"\n=== Chunks per scheme ===")
for s, n in sorted(scheme_counts.items()):
    print(f"  {n:3d}  {s}")

# ---- All metadata keys present ----
all_keys = set()
for m in all_metas:
    all_keys.update(m.keys())
print(f"\n=== Metadata keys present: {sorted(all_keys)} ===")
