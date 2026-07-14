"""
Find which schemes are missing which chunk_types.
"""
import chromadb
from collections import defaultdict

client = chromadb.PersistentClient(path="./data/vectorstore")
collection = client.get_collection("mutual_fund_faq")

all_metas = collection.get(include=["metadatas"])["metadatas"]

scheme_types = defaultdict(set)
for m in all_metas:
    scheme_types[m["scheme_name"]].add(m["chunk_type"])

all_types = {"overview","returns","holdings","investments","returns_rankings",
             "exit_load_tax","comparison","fund_manager","about","scheme_info"}

print("=== Missing chunk_types per scheme ===")
for scheme in sorted(scheme_types):
    missing = all_types - scheme_types[scheme]
    present = scheme_types[scheme]
    if missing:
        print(f"\n  {scheme}")
        print(f"    present : {sorted(present)}")
        print(f"    MISSING : {sorted(missing)}")
    else:
        print(f"  {scheme}  ✓ all types present")
