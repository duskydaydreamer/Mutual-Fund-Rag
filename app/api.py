from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
from dotenv import load_dotenv
from typing import Optional

# Load environment variables from .env
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from src.pipeline.rag_chain import ask

app = FastAPI(
    title="Mutual Fund FAQ Assistant API",
    description="API for fetching factual information about mutual fund schemes",
    version="1.0.0"
)

# Configure CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow frontend from Vercel to access backend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    answer: str
    text: str
    source_url: Optional[str] = None
    type: str
    refusal: bool = False

@app.post("/api/chat", response_model=QueryResponse)
def chat_endpoint(request: QueryRequest):
    logger.info(f"Received query: {request.query}")
    try:
        response = ask(request.query)
        # response should have:
        # answer (formatted string), text (raw text), source_url (str), type (str), refusal (bool)
        
        # Determine refusal boolean for the frontend
        is_refusal = response.get("type") in ["refusal", "pii_refusal"]

        return QueryResponse(
            answer=response.get("answer", ""),
            text=response.get("text", response.get("answer", "")),
            source_url=response.get("source_url"),
            type=response.get("type", "factual"),
            refusal=is_refusal
        )
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.api:app", host="0.0.0.0", port=8000, reload=True)
