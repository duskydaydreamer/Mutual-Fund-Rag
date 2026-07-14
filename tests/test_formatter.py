from src.pipeline.formatter import format_response

def test_format_response():
    raw = "The expense ratio is 0.5%."
    url = "https://example.com/fund"
    date = "2023-10-01"
    
    formatted = format_response(raw, url, date)
    assert raw in formatted
    assert f"Source: {url}" in formatted
    assert f"Last updated from sources: {date}" in formatted

def test_format_response_missing_meta():
    raw = "The expense ratio is 0.5%."
    
    formatted = format_response(raw, None, None)
    assert raw in formatted
    assert "Source: No source available" in formatted
    assert "Last updated from sources: Unknown" in formatted

if __name__ == "__main__":
    test_format_response()
    test_format_response_missing_meta()
    print("All formatter tests passed!")
