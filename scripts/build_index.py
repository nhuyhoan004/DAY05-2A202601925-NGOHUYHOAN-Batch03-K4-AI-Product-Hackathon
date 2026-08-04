"""Rebuild the FAISS index using the configured embedding API."""

import sys
from pathlib import Path

# Cho phép chạy trực tiếp bằng `python scripts/build_index.py` từ repository.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.ingest import run_ingestion


if __name__ == "__main__":
    run_ingestion()
