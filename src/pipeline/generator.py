import logging
import re
from typing import Optional
from langchain_groq import ChatGroq
from langchain_core.documents import Document
from langchain_core.messages import SystemMessage, HumanMessage
from src.config.prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE

logger = logging.getLogger(__name__)

def _extract_source_answer(query: str, retrieved_chunks: list[Document]) -> Optional[str]:
    """
    Return a concise source-only answer for common factual questions if the LLM is unavailable.
    """
    if not retrieved_chunks:
        return None

    query_lower = query.lower()
    scheme_name = retrieved_chunks[0].metadata.get("scheme_name", "The scheme")
    context = " ".join(chunk.page_content for chunk in retrieved_chunks)
    context = " ".join(context.split())

    def find(pattern: str) -> Optional[str]:
        match = re.search(pattern, context, flags=re.IGNORECASE)
        return match.group(1).strip(" .;") if match else None

    if "expense ratio" in query_lower:
        value = find(r"Expense ratio\s+([0-9.]+%)")
        if value:
            return f"{scheme_name}'s expense ratio is {value}."

    if "sip" in query_lower:
        value = find(r"Min\. for SIP\s+(\S+)")
        if value:
            return f"{scheme_name}'s minimum SIP amount is {value}."

    if "nav" in query_lower:
        value = find(r"NAV:\s+[^ ]+\s+[^ ]+\s+(\S+)")
        if value:
            return f"{scheme_name}'s latest NAV is {value}."

    if "aum" in query_lower or "fund size" in query_lower:
        value = find(r"Fund size \(AUM\)\s+(.+? Cr)")
        if value:
            return f"{scheme_name}'s fund size (AUM) is {value}."

    if "exit load" in query_lower:
        value = find(r"Exit load\s+(Exit load[^.]+[.])")
        if value:
            return f"{scheme_name}'s {value}"

    if "benchmark" in query_lower:
        value = find(r"Fund benchmark\s+(.+?)\s+Scheme Information")
        if value:
            return f"{scheme_name}'s benchmark is {value}."

    if "fund manager" in query_lower or "manager" in query_lower:
        value = find(r"([A-Z][A-Za-z .]+?)\s+is the Current Fund Manager")
        if value:
            return f"{scheme_name}'s current fund manager is {value}."

    if "lock-in" in query_lower or "lock in" in query_lower or "lockin" in query_lower:
        value = find(r"(?:Lock-in|Lock in|Lockin)\s+(.*?)(?:\.|;)")
        if value:
            return f"{scheme_name}'s lock-in information is: {value}."

    return None

def generate_answer(query: str, retrieved_chunks: list[Document]) -> str:
    """
    Generates an answer using the retrieved chunks and the Groq LLM.
    """
    if not retrieved_chunks:
        return "I don't have this information in my current sources."

    # Build context string
    context_parts = []
    source_urls = set()
    scrape_dates = set()
    
    for chunk in retrieved_chunks:
        context_parts.append(chunk.page_content)
        if "source_url" in chunk.metadata:
            source_urls.add(chunk.metadata["source_url"])
        if "scrape_date" in chunk.metadata:
            scrape_dates.add(chunk.metadata["scrape_date"])
            
    context_str = "\n\n---\n\n".join(context_parts)
    urls_str = "\n".join(list(source_urls))
    
    # Use the most recent scrape date or a fallback
    scrape_date = list(scrape_dates)[0] if scrape_dates else "Unknown"

    system_prompt = SYSTEM_PROMPT.format(scrape_date=scrape_date)
    user_prompt = USER_PROMPT_TEMPLATE.format(
        context=context_str,
        source_urls=urls_str,
        query=query
    )
    
    try:
        import time
        # Enforce rate limit: 30 requests per minute = 1 request every 2 seconds
        time.sleep(2.1)
        
        import os
        model_name = os.environ.get("LLM_MODEL", "llama-3.3-70b-versatile")
        groq_api_key = os.environ.get("GROQ_API_KEY", "").strip()
        if groq_api_key:
            os.environ["GROQ_API_KEY"] = groq_api_key

        llm = ChatGroq(
            model=model_name,
            groq_api_key=groq_api_key or None,
            temperature=0.0,
            max_tokens=200,
            max_retries=3, # Built-in exponential backoff for 429 errors
        )
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        response = llm.invoke(messages)
        return response.content
        
    except Exception as e:
        logger.error(f"Error generating answer: {e}")
        import traceback
        traceback.print_exc()
        source_answer = _extract_source_answer(query, retrieved_chunks)
        if source_answer:
            return source_answer
        return "I found relevant source information, but the answer generator is temporarily unavailable. Please try a more specific factual question."
