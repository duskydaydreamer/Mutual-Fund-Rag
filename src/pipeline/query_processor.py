import re

def preprocess_query(query: str) -> str:
    """
    Preprocess the user query by:
    - Stripping leading/trailing whitespace
    - Normalizing to lowercase
    - Normalizing whitespace (replacing multiple spaces with a single space)
    """
    if not query:
        return ""
        
    # 1. Normalize to lowercase
    query = query.lower()
    
    # 2. Strip leading/trailing whitespace
    query = query.strip()
    
    # 3. Normalize multiple whitespace characters into a single space
    query = re.sub(r'\s+', ' ', query)
    
    # Note: Basic spell correction for scheme names can be integrated here later
    # (e.g., using rapidfuzz against a list of known scheme names).
    
    return query
