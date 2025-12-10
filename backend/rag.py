import os
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple

from dotenv import load_dotenv
from sentence_transformers import CrossEncoder
from huggingface_hub import InferenceClient

from .vector_store import SimpleVectorStore

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables
BACKEND_DIR = Path(__file__).parent
load_dotenv(BACKEND_DIR / ".env")


class ClaimsAssistant:
    """RAG-based Claims Query Assistant with reranking and LLM generation."""

    def __init__(self) -> None:
        self.vector_store = SimpleVectorStore()
        index_path = BACKEND_DIR / "index.pkl"
        self.vector_store.load(str(index_path))

        # Initialize Cross-Encoder for reranking
        self.reranker: Optional[CrossEncoder] = None
        try:
            logger.info("Loading Cross-Encoder model for reranking...")
            self.reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
            logger.info("Cross-Encoder loaded successfully.")
        except Exception as e:
            logger.warning(f"Failed to load Cross-Encoder: {e}. Reranking disabled.")

        # Initialize Inference Client
        self.hf_token: Optional[str] = os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_API_TOKEN")
        
        self.client: Optional[InferenceClient] = None
        if self.hf_token:
            try:
                self.client = InferenceClient(token=self.hf_token)
                logger.info("HuggingFace InferenceClient initialized successfully.")
            except Exception as e:
                logger.error(f"Error initializing InferenceClient: {e}")
        else:
            logger.warning("HF_TOKEN not found. LLM generation will be disabled.")

    def _detect_query_type(self, query: str) -> Tuple[str, int]:
        """
        Detect query intent and return (query_type, result_count).
        Types: 'data' (show table), 'analysis' (text only), 'chat' (conversational)
        """
        query_lower = query.lower().strip()
        
        # Conversational/chat queries - no data needed
        chat_patterns = [
            'hello', 'hi', 'hey', 'how are you', 'what can you do', 
            'help', 'thank', 'bye', 'who are you', 'your name'
        ]
        if any(p in query_lower for p in chat_patterns):
            return ('chat', 0)
        
        # Analytical questions - need context but return primarily text
        analysis_patterns = [
            'why', 'explain', 'analyze', 'insight', 'pattern', 'trend',
            'what do you think', 'your view', 'summarize', 'summary',
            'tell me about', 'describe', 'what are the', 'main reason',
            'most common', 'average', 'typical'
        ]
        if any(p in query_lower for p in analysis_patterns):
            return ('analysis', 20)
        
        # Data retrieval queries - show table
        data_patterns = [
            'show', 'list', 'find', 'get', 'display', 'search',
            'all', 'denied', 'approved', 'pending', 'claims for',
            'patient', 'provider', 'doctor'
        ]
        if any(p in query_lower for p in data_patterns):
            # Check for "all" keywords
            if any(kw in query_lower for kw in ['all', 'every', 'list all', 'show all']):
                return ('data', 50)
            return ('data', 15)
        
        # Default: treat as analysis
        return ('analysis', 10)

    def _retrieve(self, query: str, k: int = 10) -> List[Dict[str, Any]]:
        """Retrieve relevant documents from vector store."""
        total_docs = len(self.vector_store.documents)
        search_k = min(k * 4 if self.reranker else k, total_docs)
        return self.vector_store.query(query, k=search_k)

    def _rerank(self, query: str, results: List[Dict[str, Any]], top_k: int = 10) -> List[Dict[str, Any]]:
        """Rerank results using Cross-Encoder if available."""
        if not self.reranker or not results:
            return results[:top_k]

        try:
            pairs = [[query, r['document']] for r in results]
            scores = self.reranker.predict(pairs)
            for i, r in enumerate(results):
                r['rerank_score'] = float(scores[i])
            reranked = sorted(results, key=lambda x: x['rerank_score'], reverse=True)
            return reranked[:top_k]
        except Exception as e:
            logger.warning(f"Reranking failed: {e}. Using raw results.")
            return results[:top_k]

    def _generate_chat_response(self, query: str) -> str:
        """Generate conversational response without data."""
        if not self.client:
            return "Hello! I'm your Claims Intelligence Assistant. I can help you search and analyze claims data. Try asking things like 'Show all denied claims' or 'What are the main denial reasons?'"
        
        try:
            messages = [
                {
                    "role": "system",
                    "content": """You are a Claims Intelligence Assistant. Help users with insurance claims data.
Keep responses concise (3-5 bullet points max). Don't over-explain.
Example capabilities: search claims, analyze denial patterns, find patient/provider data."""
                },
                {"role": "user", "content": query}
            ]
            
            response = self.client.chat_completion(
                model="meta-llama/Llama-3.2-1B-Instruct",
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Chat generation error: {e}")
            return "Hello! I can help you analyze claims data. Try asking 'Show denied claims' or 'What are the top denial reasons?'"

    def _generate_analysis_response(self, query: str, context: str, num_results: int) -> str:
        """Generate analytical/insightful response."""
        if not self.client:
            return f"Based on {num_results} relevant claims, I can see patterns in the data. The table below shows the details."
        
        try:
            messages = [
                {
                    "role": "system",
                    "content": """You are a claims data analyst. Provide insightful analysis based on the data.
Focus on patterns, trends, and actionable insights.
Be conversational but informative. Give 2-3 sentences of analysis."""
                },
                {
                    "role": "user",
                    "content": f"Analyze this claims data and answer: {query}\n\nData summary:\n{context}"
                }
            ]
            
            response = self.client.chat_completion(
                model="meta-llama/Llama-3.2-1B-Instruct",
                messages=messages,
                max_tokens=200,
                temperature=0.5
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Analysis generation error: {e}")
            return f"Looking at {num_results} claims, I found relevant data for your query. See the breakdown below."

    def _generate_data_response(self, query: str, num_results: int) -> str:
        """Generate brief response for data queries."""
        return f"Found {num_results} claims matching your search."

    def query(self, user_query: str) -> Dict[str, Any]:
        """Main query method with intent detection."""
        logger.info(f"Processing query: {user_query}")

        # Detect query type
        query_type, result_count = self._detect_query_type(user_query)
        logger.info(f"Query type: {query_type}, target results: {result_count}")

        # Handle chat queries - no data retrieval
        if query_type == 'chat':
            answer = self._generate_chat_response(user_query)
            return {"answer": answer, "context": []}

        # Retrieve data for analysis and data queries
        initial_results = self._retrieve(user_query, k=result_count)
        if not initial_results:
            return {"answer": "No relevant claims found for your query.", "context": []}

        # Rerank
        final_results = self._rerank(user_query, initial_results, top_k=result_count)

        # Generate response based on query type
        if query_type == 'analysis':
            # Build context for analysis
            context_str = "\n".join([
                f"- {r['metadata'].get('status', 'Unknown')} claim: {r['metadata'].get('patient_name', 'N/A')}, "
                f"${r['metadata'].get('claim_amount', 0)}, {r['metadata'].get('denial_reason', 'N/A')}"
                for r in final_results[:10]
            ])
            answer = self._generate_analysis_response(user_query, context_str, len(final_results))
            # For analysis, show fewer results in table
            return {"answer": answer, "context": final_results[:5]}
        else:
            # Data query - brief response, full table
            answer = self._generate_data_response(user_query, len(final_results))
            return {"answer": answer, "context": final_results}
