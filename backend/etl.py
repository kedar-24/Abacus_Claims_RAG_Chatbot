import logging
from pathlib import Path
from typing import List, Dict, Any

import pandas as pd

from backend.vector_store import SimpleVectorStore

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

BACKEND_DIR = Path(__file__).parent


def format_claim(row: pd.Series) -> str:
    """Format a claim row as a readable text document."""
    return (
        f"Claim ID: {row['claim_id']}\n"
        f"Patient: {row['patient_name']} (ID: {row['patient_id']})\n"
        f"Provider: {row['provider_name']} ({row['specialty']})\n"
        f"Date: {row['date']}\n"
        f"Diagnosis: {row['diagnosis']}\n"
        f"Treatment: {row['treatment_description']}\n"
        f"Amount: ${row['claim_amount']}\n"
        f"Status: {row['status']}\n"
        f"Denial Reason: {row['denial_reason']}"
    )


def run_etl() -> None:
    """Run the ETL pipeline to create the vector index."""
    logger.info("Starting ETL Process...")

    data_path = BACKEND_DIR / "claims_data.csv"
    index_path = BACKEND_DIR / "index.pkl"

    df = pd.read_csv(data_path)
    logger.info(f"Loaded {len(df)} claims from {data_path}")

    documents: List[str] = []
    metadatas: List[Dict[str, Any]] = []

    for _, row in df.iterrows():
        text = format_claim(row)
        documents.append(text)
        metadatas.append(row.to_dict())

    store = SimpleVectorStore()
    store.add_documents(documents, metadatas)
    store.save(str(index_path))

    logger.info(f"ETL Complete. Created index with {len(documents)} documents.")


if __name__ == "__main__":
    run_etl()
