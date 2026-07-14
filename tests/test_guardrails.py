from src.pipeline.guardrails import detect_pii, is_advisory_query, classify_query

def test_detect_pii():
    # True positives
    assert detect_pii("My PAN is ABCDE1234F") == True
    assert detect_pii("Here is my Aadhaar 1234-5678-9012") == True
    assert detect_pii("Call me at 9876543210") == True
    assert detect_pii("Email me at test@example.com") == True

    # True negatives
    assert detect_pii("What is the PAN requirement for mutual funds?") == False
    assert detect_pii("What is the exit load?") == False

def test_is_advisory_query():
    # True positives
    assert is_advisory_query("Should I invest in HDFC Mid Cap?") == True
    assert is_advisory_query("Which is better: HDFC or ICICI?") == True
    assert is_advisory_query("Can you recommend a good fund?") == True
    
    # True negatives
    assert is_advisory_query("What is the NAV of HDFC Mid Cap?") == False
    assert is_advisory_query("Who is the fund manager?") == False

def test_classify_query():
    assert classify_query("My phone is 9876543210") == "PII_DETECTED"
    assert classify_query("Which fund should I buy?") == "ADVISORY"
    assert classify_query("What's the weather today?") == "OUT_OF_SCOPE"
    assert classify_query("What is the exit load?") == "FACTUAL"

if __name__ == "__main__":
    test_detect_pii()
    test_is_advisory_query()
    test_classify_query()
    print("All guardrail tests passed!")
