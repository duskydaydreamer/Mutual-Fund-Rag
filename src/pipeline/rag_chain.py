from src.pipeline.query_processor import preprocess_query
from src.pipeline.retriever import retrieve
from src.pipeline.generator import generate_answer
from src.pipeline.guardrails import classify_query
from src.pipeline.formatter import format_response
from src.config.prompts import REFUSAL_TEMPLATE, PII_REFUSAL_TEMPLATE

def ask(query: str) -> dict:
    """Full RAG pipeline: query → preprocess → guardrails → retrieve → generate → format"""
    processed_query = preprocess_query(query)

    # Guardrails
    classification = classify_query(processed_query)

    if classification == "PII_DETECTED":
        return {"answer": PII_REFUSAL_TEMPLATE, "type": "pii_refusal"}
    if classification == "ADVISORY":
        return {"answer": REFUSAL_TEMPLATE, "type": "refusal"}
    if classification == "OUT_OF_SCOPE":
        return {"answer": REFUSAL_TEMPLATE, "type": "refusal"}

    # Retrieval + Generation
    try:
        chunks = retrieve(processed_query, top_k=5)
    except ValueError as e:
        if str(e) == "performance_query_guardrail":
            return {"answer": REFUSAL_TEMPLATE, "type": "refusal"}
        elif str(e) == "ambiguous_scheme_query":
            return {"answer": "Your query matches multiple mutual funds. Please specify the fund name more clearly.", "type": "refusal"}
        raise e

    raw_answer = generate_answer(processed_query, chunks)

    # Format
    source_url = chunks[0].metadata.get("source_url") if chunks else None
    scrape_date = chunks[0].metadata.get("scrape_date") if chunks else None
    
    formatted = format_response(
        raw_answer,
        source_url=source_url,
        scrape_date=scrape_date,
    )

    return {
        "answer": formatted,
        "text": raw_answer,
        "source_url": source_url,
        "type": "factual"
    }
