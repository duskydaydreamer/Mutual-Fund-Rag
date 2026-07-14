from dotenv import load_dotenv
import logging
logging.basicConfig(level=logging.ERROR)

load_dotenv()
from src.pipeline.rag_chain import ask

try:
    print(ask("what is the NAV of hdfc small cap fund"))
except Exception as e:
    print("FAILED:", e)
