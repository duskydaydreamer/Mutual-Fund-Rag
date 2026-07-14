import os
import sys
from unittest.mock import patch
from langchain_core.messages import AIMessage
from dotenv import load_dotenv

load_dotenv()
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.pipeline.rag_chain import ask

# Mock ChatGroq to avoid network call and dummy API key issues in the sandbox
def mock_invoke(self, messages, **kwargs):
    return AIMessage(content="This is a mocked factual answer based on the context. It confirms the generation pipeline works. The retriever successfully found the documents.")

with patch("src.pipeline.generator.ChatGroq.invoke", new=mock_invoke):
    queries = [
        "What is the expense ratio of HDFC Mid Cap Fund?",
        "What is the minimum SIP amount for Parag Parikh ELSS Fund?",
        "Should I invest in HDFC Mid Cap?",  # Test advisory guardrail
        "My PAN is ABCDE1234F" # Test PII guardrail
    ]

    for q in queries:
        print(f"\nQuery: {q}")
        try:
            result = ask(q)
            print(f"Type: {result.get('type')}")
            print(f"Answer:\n{result['answer']}")
        except Exception as e:
            print(f"Error: {e}")
        print("-" * 50)
