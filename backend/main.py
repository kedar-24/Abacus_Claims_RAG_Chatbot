import os
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .rag import ClaimsAssistant

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global RAG system instance
rag_system: ClaimsAssistant | None = None


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager for startup/shutdown events."""
    global rag_system
    logger.info("Starting Claims Query Assistant...")

    # Check for index file
    index_path = "backend/index.pkl"
    if not os.path.exists(index_path):
        logger.warning(f"Index not found at {index_path}. Run etl.py first.")

    # Initialize RAG system
    rag_system = ClaimsAssistant()
    logger.info("RAG system initialized successfully.")

    yield  # Application runs here

    # Cleanup on shutdown
    logger.info("Shutting down Claims Query Assistant...")


app = FastAPI(
    title="Claims Query Assistant",
    description="RAG-powered insurance claims query system",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration
origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    """Request model for query endpoint."""
    query: str


class QueryResponse(BaseModel):
    """Response model for query endpoint."""
    answer: str
    context: list


@app.post("/query", response_model=QueryResponse)
async def query_claims(request: QueryRequest) -> QueryResponse:
    """Query the claims database using RAG."""
    if not rag_system:
        raise HTTPException(
            status_code=503,
            detail="RAG system not initialized. Please try again later."
        )

    if not request.query.strip():
        raise HTTPException(
            status_code=400,
            detail="Query cannot be empty."
        )

    try:
        response = rag_system.query(request.query)
        return QueryResponse(**response)
    except Exception as e:
        logger.error(f"Query processing error: {e}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing your query."
        )


@app.get("/health")
async def health_check() -> dict:
    """Health check endpoint."""
    return {
        "status": "ok",
        "rag_ready": rag_system is not None
    }
