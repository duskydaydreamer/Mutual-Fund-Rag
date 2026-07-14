import os
import sys
from dotenv import load_dotenv
load_dotenv()

from src.pipeline.generator import generate_answer

print("LLM_MODEL:", os.environ.get("LLM_MODEL"))
print("GROQ_API_KEY:", "set" if os.environ.get("GROQ_API_KEY") else "not set")

try:
    from langchain_core.documents import Document
    doc = Document(page_content="test context", metadata={"source_url": "http://example.com"})
    ans = generate_answer("test query", [doc])
    print("Answer:", ans)
except Exception as e:
    print("Error:", e)
