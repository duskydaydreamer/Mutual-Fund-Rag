import hashlib
import difflib
import chromadb
from typing import Optional
from langchain_core.documents import Document
from langchain_community.embeddings import HuggingFaceEmbeddings

# Initialize embeddings and ChromaDB client at module level
embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-small-en-v1.5",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True}
)

client = chromadb.PersistentClient(path="./data/vectorstore")
collection = client.get_or_create_collection(
    name="mutual_fund_faq",
    metadata={"hnsw:space": "cosine"}
)

CANONICAL_SCHEMES = [
    "HDFC Defence Fund Direct Growth",
    "HDFC Flexi Cap Direct Plan Growth",
    "HDFC Gold ETF Fund of Fund Direct Plan Growth",
    "HDFC Mid Cap Fund Direct Growth",
    "HDFC NIFTY 50 Index Fund Direct Growth",
    "HDFC Silver ETF FoF Direct Growth",
    "HDFC Small Cap Fund Direct Growth",
    "ICICI Prudential Large Cap Fund Direct Growth",
    "ICICI Prudential Multi Asset Fund Direct Growth",
    "ICICI Prudential Silver ETF FoF Direct Growth",
    "ICICI Prudential Technology Direct Plan Growth",
    "Motilal Oswal Flexi Cap Fund Direct Growth",
    "Motilal Oswal Large and Midcap Fund Direct Growth",
    "Motilal Oswal Midcap Fund Direct Growth",
    "Motilal Oswal Small Cap Fund Direct Growth",
    "Parag Parikh Conservative Hybrid Fund Direct Growth",
    "Parag Parikh ELSS Tax Saver Fund Direct Growth",
    "Parag Parikh Flexi Cap Fund Direct Growth",
    "Parag Parikh Large Cap Fund Direct Growth",
    "Parag Parikh Liquid Fund Direct Growth"
]

SCHEMES_WITHOUT_OVERVIEW = {
    "HDFC Defence Fund Direct Growth",
    "HDFC Gold ETF Fund of Fund Direct Plan Growth",
    "HDFC Silver ETF FoF Direct Growth",
    "ICICI Prudential Silver ETF FoF Direct Growth",
    "ICICI Prudential Technology Direct Plan Growth",
    "Motilal Oswal Large and Midcap Fund Direct Growth",
}

def clean_for_matching(text: str) -> str:
    text = text.lower()
    for word in ['direct', 'growth', 'plan', 'fund']:
        text = text.replace(word, '')
    return " ".join(text.split())

def detect_scheme(query: str) -> Optional[str]:
    """
    Match query against known 20 schemes.
    Clean query first: remove 'direct', 'growth', 'plan', 'fund'.
    Return the exact canonical `scheme_name` if match confidence > 85%, else None.
    """
    cleaned_query = clean_for_matching(query)
    
    # Direct substring match first
    for scheme in CANONICAL_SCHEMES:
        cleaned_scheme = clean_for_matching(scheme)
        if cleaned_scheme and cleaned_scheme in cleaned_query:
            return scheme
            
    # If no exact substring match, try fuzzy matching using difflib
    best_match = None
    best_ratio = 0.0
    
    for scheme in CANONICAL_SCHEMES:
        cleaned_scheme = clean_for_matching(scheme)
        words_query = cleaned_query.split()
        words_scheme = cleaned_scheme.split()
        n = len(words_scheme)
        
        if n == 0 or len(words_query) == 0:
            continue
            
        # Sliding window to match sub-phrases
        for i in range(len(words_query) - n + 1):
            window = " ".join(words_query[i:i+n])
            ratio = difflib.SequenceMatcher(None, cleaned_scheme, window).ratio()
            if ratio > best_ratio:
                best_ratio = ratio
                best_match = scheme
                
        # Also check against the whole query just in case
        ratio = difflib.SequenceMatcher(None, cleaned_scheme, cleaned_query).ratio()
        if ratio > best_ratio:
            best_ratio = ratio
            best_match = scheme
            
    if best_ratio > 0.85:
        return best_match
    return None

def detect_topics(query: str) -> list[str]:
    """
    Map keywords in query to preferred chunk_types.
    """
    query_lower = query.lower()
    topics = []
    
    if any(k in query_lower for k in ["expense ratio", "nav", "aum", "rating", "risk"]):
        topics.extend(["overview"])
    if any(k in query_lower for k in ["sip", "lumpsum", "minimum investment", "min investment"]):
        topics.extend(["investments", "overview"])
    if any(k in query_lower for k in ["exit load", "stamp duty", "tax"]):
        topics.extend(["exit_load_tax"])
    if any(k in query_lower for k in ["fund manager", "manager"]):
        topics.extend(["fund_manager"])
    if any(k in query_lower for k in ["holdings", "portfolio", "sector"]):
        topics.extend(["holdings"])
    if any(k in query_lower for k in ["fund house", "launch", "inception", "amc"]):
        topics.extend(["scheme_info", "about"])
    if any(k in query_lower for k in ["general description", "about", "what is"]):
        topics.extend(["about", "overview"])
        
    # Remove duplicates while preserving order
    seen = set()
    result = []
    for t in topics:
        if t not in seen:
            seen.add(t)
            result.append(t)
    return result

def build_contextualized_query(query: str, scheme: Optional[str], topics: list[str]) -> str:
    """
    Format query to match the embedding structure of stored chunks.
    """
    if scheme and topics:
        return f"Fund: {scheme} | Topic: {topics[0]}\n\n{query}"
    if scheme:
        return f"Fund: {scheme}\n\n{query}"
    if topics:
        return f"Topic: {topics[0]}\n\n{query}"
    return query

def build_chroma_filter(scheme: Optional[str], base_filters: Optional[dict]) -> Optional[dict]:
    """
    Safely build Chroma where clause.
    """
    if scheme and base_filters:
        return {"$and": [{"scheme_name": scheme}, base_filters]}
    if scheme:
        return {"scheme_name": scheme}
    return base_filters

def retrieve(query: str, top_k: int = 5, filters: Optional[dict] = None) -> list[Document]:
    # 1. Guardrail: Block performance/returns queries before any retrieval
    performance_keywords = [
        "returns", "performance", "cagr", "annualised return", "annualized return",
        "1y return", "3y return", "5y return", "historical return"
    ]
    if any(kw in query.lower() for kw in performance_keywords):
        raise ValueError("performance_query_guardrail")

    # 2. Parse Intent
    scheme = detect_scheme(query)    # e.g. "HDFC Mid Cap Fund Direct Growth"
    topics = detect_topics(query)    # e.g. ["overview"] or ["investments", "overview"]

    # 3. Overview fallback for the 6 schemes that have no overview chunk
    if scheme in SCHEMES_WITHOUT_OVERVIEW and "overview" in topics:
        topics = [t for t in topics if t != "overview"] + ["about", "scheme_info"]

    # 4. Build contextualized query and Chroma filter
    context_query = build_contextualized_query(query, scheme, topics)
    chroma_filter = build_chroma_filter(scheme, filters)

    # 5. Fetch Candidates
    # Use a wider pool first to allow post-filtering
    candidate_k = max(top_k * 4, 20)

    # IMPORTANT: use HuggingFaceEmbeddings manually
    query_embedding = embeddings.embed_query(context_query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=candidate_k,
        where=chroma_filter,
        include=["documents", "metadatas", "distances"]
    )

    if not results["documents"] or not results["documents"][0]:
        return []

    candidates = []
    # Chroma returns parallel lists: unpack them together
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0]
    ):
        candidates.append({"doc": doc, "meta": meta, "dist": dist})

    # 6. Post-Process: cutoff → scheme filter → topic boost → dedup → sort
    final_results = []
    seen_keys = set()

    for c in candidates:
        # 6a. Distance cutoff (cosine distance, lower = more similar)
        # Good matches: ~0.12–0.24. Reject anything above 0.35.
        if c["dist"] > 0.35:
            continue

        # 6b. Hard-filter: discard wrong-scheme results
        # (Chroma filter should already handle this, but be defensive)
        if scheme and c["meta"]["scheme_name"] != scheme:
            continue

        # 6c. Topic boost: preferred chunk_type gets a small distance reduction
        adjusted_dist = c["dist"]
        if topics and c["meta"]["chunk_type"] in topics:
            adjusted_dist -= 0.05  # pulls preferred types to the top

        # 6d. Stable deduplication — prefer chunk_id, fall back to content hash
        dedup_key = c["meta"].get("chunk_id") or hashlib.md5(
            " ".join(c["doc"].lower().split()).encode("utf-8")
        ).hexdigest()
        
        if dedup_key in seen_keys:
            continue
        seen_keys.add(dedup_key)

        c["adjusted_dist"] = adjusted_dist
        final_results.append(c)

    # Sort by adjusted distance ascending (best match first)
    final_results.sort(key=lambda x: x["adjusted_dist"])
    top_results = final_results[:top_k]

    # 7. Ambiguity check: no scheme detected + results span ≥3 different schemes
    # This means the query is too vague — ask the user to name the fund.
    if not scheme and top_results:
        unique_schemes = set(r["meta"]["scheme_name"] for r in top_results)
        if len(unique_schemes) >= 3:
            raise ValueError("ambiguous_scheme_query")

    # Convert back to Langchain Document objects
    return [Document(page_content=r["doc"], metadata=r["meta"]) for r in top_results]
