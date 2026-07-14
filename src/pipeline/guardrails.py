import re

PII_PATTERNS = {
    "PAN": r"[A-Z]{5}[0-9]{4}[A-Z]",
    "Aadhaar": r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}\b",
    "Phone": r"\b[6-9]\d{9}\b",
    "Email": r"[\w.-]+@[\w.-]+\.\w+",
}

ADVISORY_KEYWORDS = [
    "should i", "which is better", "recommend", "suggest",
    "good fund", "best fund", "invest in", "compare",
    "worth investing", "better option", "which one",
    "good investment", "which fund is better", "returns will i get",
    "guarantee", "right time to buy", "should i buy", "time to invest",
    "buy or sell"
]

def detect_pii(query: str) -> bool:
    for name, pattern in PII_PATTERNS.items():
        if re.search(pattern, query, re.IGNORECASE):
            return True
    return False

def is_advisory_query(query: str) -> bool:
    query_lower = query.lower()
    for keyword in ADVISORY_KEYWORDS:
        if keyword in query_lower:
            return True
    return False

def classify_query(query: str) -> str:
    """
    Returns: "FACTUAL", "ADVISORY", "PII_DETECTED", or "OUT_OF_SCOPE"
    """
    if detect_pii(query):
        return "PII_DETECTED"
    
    if is_advisory_query(query):
        return "ADVISORY"
    
    out_of_scope_keywords = ["weather", "sports", "movie", "recipe"]
    if any(kw in query.lower() for kw in out_of_scope_keywords):
        return "OUT_OF_SCOPE"
        
    return "FACTUAL"
