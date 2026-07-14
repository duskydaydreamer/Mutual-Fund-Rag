import logging
from langchain_groq import ChatGroq
from langchain_core.documents import Document
from langchain_core.messages import SystemMessage, HumanMessage
from src.config.prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE

logger = logging.getLogger(__name__)

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
        return "I encountered a temporary issue while generating the answer. Please try again later."
