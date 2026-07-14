from src.pipeline.retriever import detect_scheme, detect_topics, build_chroma_filter

def test_detect_scheme():
    # Exact/fuzzy matches
    assert detect_scheme("What is the NAV of HDFC Mid Cap?") == "HDFC Mid Cap Fund Direct Growth"
    assert detect_scheme("Tell me about Parag Parikh Flexi Cap Fund") == "Parag Parikh Flexi Cap Fund Direct Growth"
    assert detect_scheme("ICICI Tech fund exit load") == "ICICI Prudential Technology Direct Plan Growth"
    
    # No match
    assert detect_scheme("What is a mutual fund?") is None

def test_detect_topics():
    assert "overview" in detect_topics("What is the expense ratio?")
    assert "investments" in detect_topics("What is the minimum SIP?")
    assert "exit_load_tax" in detect_topics("What is the exit load?")
    assert "fund_manager" in detect_topics("Who is the fund manager?")
    assert "holdings" in detect_topics("What are the top sectors?")

def test_build_chroma_filter():
    # Only scheme
    assert build_chroma_filter("HDFC Mid Cap Fund Direct Growth", None) == {"scheme_name": "HDFC Mid Cap Fund Direct Growth"}
    
    # Scheme and base filters
    assert build_chroma_filter("HDFC Mid Cap Fund Direct Growth", {"chunk_type": "overview"}) == {
        "$and": [
            {"scheme_name": "HDFC Mid Cap Fund Direct Growth"},
            {"chunk_type": "overview"}
        ]
    }
    
    # Only base filters
    assert build_chroma_filter(None, {"chunk_type": "overview"}) == {"chunk_type": "overview"}
    
    # Neither
    assert build_chroma_filter(None, None) is None

if __name__ == "__main__":
    test_detect_scheme()
    test_detect_topics()
    test_build_chroma_filter()
    print("All retriever tests passed!")
