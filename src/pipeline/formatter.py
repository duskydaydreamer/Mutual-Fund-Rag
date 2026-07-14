from typing import Optional
import re

def clean_answer_text(raw_answer: str) -> str:
    """
    Keep the answer body separate from citation metadata.
    The API sends source_url and scrape_date as structured fields for the UI.
    """
    answer_text = raw_answer.strip()
    answer_text = re.sub(r"\s*\(Source:\s*https?://[^)]+\)", "", answer_text, flags=re.IGNORECASE)
    answer_text = re.sub(r"\n*\s*Source:\s*https?://\S+\s*", "\n", answer_text, flags=re.IGNORECASE)
    answer_text = re.sub(r"\n*\s*Last updated from sources:\s*[^\n]+\s*", "\n", answer_text, flags=re.IGNORECASE)
    return answer_text.strip()

def format_response(raw_answer: str, source_url: Optional[str], scrape_date: Optional[str]) -> str:
    """
    Format the final output response.
    """
    answer_text = clean_answer_text(raw_answer)
    
    # Ensure source_url and scrape_date have defaults if None
    url = source_url if source_url else "No source available"
    date = scrape_date if scrape_date else "Unknown"
    
    formatted = f"{answer_text}\n\nSource: {url}\nLast updated from sources: {date}"
    return formatted
