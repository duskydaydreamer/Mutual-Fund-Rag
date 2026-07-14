from typing import Optional

def format_response(raw_answer: str, source_url: Optional[str], scrape_date: Optional[str]) -> str:
    """
    Format the final output response.
    """
    answer_text = raw_answer.strip()
    
    # Ensure source_url and scrape_date have defaults if None
    url = source_url if source_url else "No source available"
    date = scrape_date if scrape_date else "Unknown"
    
    formatted = f"{answer_text}\n\nSource: {url}\nLast updated from sources: {date}"
    return formatted
