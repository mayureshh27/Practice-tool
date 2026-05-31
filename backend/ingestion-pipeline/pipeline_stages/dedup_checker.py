from __future__ import annotations

import logging

import numpy as np
from sentence_transformers import SentenceTransformer

from ..generator import GeneratedProblem
from .config import DEDUP_THRESHOLD, EMBED_MODEL

logger = logging.getLogger(__name__)


class DedupChecker:
    def __init__(self, catalog: dict):
        try:
            self._embedder = SentenceTransformer(EMBED_MODEL)
        except Exception as exc:
            logger.error("Failed to load SentenceTransformer model '%s': %s", EMBED_MODEL, exc)
            raise RuntimeError(f"SentenceTransformer init failed: {exc}") from exc
        self._ids = {p["id"] for p in catalog.get("problems", [])}
        statements = [p.get("statement", "")
                      for p in catalog.get("problems", [])]
        self._embeddings: np.ndarray | None = None
        if statements:
            self._embeddings = self._embedder.encode(
                statements, normalize_embeddings=True, show_progress_bar=False
            )

    def is_duplicate(self, p: GeneratedProblem) -> tuple[bool, str]:
        if p.id in self._ids:
            return True, f"slug collision: '{p.id}' already exists"

        if self._embeddings is not None and len(self._embeddings) > 0:
            new_emb = self._embedder.encode(
                [p.statement], normalize_embeddings=True,
                show_progress_bar=False
            )
            sims    = (self._embeddings @ new_emb.T).squeeze()
            max_sim = float(np.max(sims))
            if max_sim >= DEDUP_THRESHOLD:
                idx = int(np.argmax(sims))
                return (
                    True,
                    f"cosine={max_sim:.3f} ≥ {DEDUP_THRESHOLD} "
                    f"vs existing problem at index {idx}"
                )
        return False, ""

    def register(self, p: GeneratedProblem):
        self._ids.add(p.id)
        new_emb = self._embedder.encode(
            [p.statement], normalize_embeddings=True, show_progress_bar=False
        )
        self._embeddings = (
            new_emb if self._embeddings is None
            else np.vstack([self._embeddings, new_emb])
        )
