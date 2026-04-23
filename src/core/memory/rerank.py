"""
Reranking Pipeline - Hybrid Search + Temporal + KG Boost

Implements a multi-stage reranking pipeline for memory retrieval:
1. Hybrid Search: BM25 + Vector → Top K
2. Temporal Rerank: Prefer recently updated + KG connectivity
3. Diversity Filter: MMR-style deduplication

Design inspired by MemPalace hybrid v4 temporal-proximity.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .palace import PalaceIndex, SearchResult
    from .kg import KnowledgeGraph, Entity

# Runtime imports for KG booster
from .kg import RelationQuery

# ============================================================================
# Configuration
# ============================================================================


@dataclass
class RerankConfig:
    """Configuration for reranking pipeline."""

    # Stage 1: Hybrid Search
    hybrid_k: int = 20  # Initial retrieval count
    bm25_weight: float = 0.3  # BM25 contribution
    vector_weight: float = 0.7  # Vector similarity contribution

    # Stage 2: Temporal Rerank
    temporal_decay_days: float = 30.0  # Half-life for temporal decay
    temporal_weight: float = 0.3  # Temporal score contribution
    kg_boost_weight: float = 0.2  # KG connectivity boost

    # Stage 3: Diversity
    mmr_lambda: float = 0.7  # MMR balance (relevance vs diversity)
    diversity_threshold: float = 0.85  # Similarity threshold for dedup

    # Final output
    final_k: int = 10  # Final result count


@dataclass
class RerankResult:
    """A single reranked search result."""

    # Original result
    drawer_id: str
    content: str
    wing_id: str
    room_id: str
    metadata: dict[str, Any] = field(default_factory=dict)

    # Scores
    bm25_score: float = 0.0
    vector_score: float = 0.0
    hybrid_score: float = 0.0
    temporal_score: float = 0.0
    kg_boost: float = 0.0
    final_score: float = 0.0

    # Context
    updated_at: datetime | None = None
    entity_id: str | None = None  # Linked KG entity if any


# ============================================================================
# BM25 Implementation
# ============================================================================


class BM25:
    """BM25 ranking function for text search."""

    def __init__(
        self,
        k1: float = 1.5,
        b: float = 0.75,
    ):
        self.k1 = k1
        self.b = b
        self.doc_freqs: dict[str, int] = {}
        self.doc_lens: list[int] = []
        self.avgdl: float = 0.0
        self.n_docs: int = 0

    def tokenize(self, text: str) -> list[str]:
        """Simple tokenizer - lowercase alphanumeric + CJK characters."""
        # Match word characters or CJK unified ideographs
        tokens = re.findall(r"[\w\u4e00-\u9fff]+", text.lower())
        return tokens

    def fit(self, documents: list[str]) -> None:
        """Build document frequency index."""
        self.n_docs = len(documents)
        self.doc_freqs = {}
        self.doc_lens = []

        for doc in documents:
            tokens = self.tokenize(doc)
            self.doc_lens.append(len(tokens))
            seen = set()
            for token in tokens:
                if token not in seen:
                    seen.add(token)
                    self.doc_freqs[token] = self.doc_freqs.get(token, 0) + 1

        self.avgdl = sum(self.doc_lens) / max(self.n_docs, 1)

    def _idf(self, term: str) -> float:
        """Compute IDF for a term."""
        n = self.doc_freqs.get(term, 0)
        return math.log((self.n_docs - n + 0.5) / (n + 0.5) + 1)

    def score(self, query: str, doc_idx: int, doc: str) -> float:
        """Score a document against a query."""
        query_tokens = self.tokenize(query)
        doc_tokens = self.tokenize(doc)
        doc_len = len(doc_tokens)

        if doc_len == 0:
            return 0.0

        score = 0.0
        doc_term_freqs: dict[str, int] = {}
        for token in doc_tokens:
            doc_term_freqs[token] = doc_term_freqs.get(token, 0) + 1

        for term in query_tokens:
            if term not in doc_term_freqs:
                continue
            tf = doc_term_freqs[term]
            idf = self._idf(term)
            numerator = tf * (self.k1 + 1)
            denominator = tf + self.k1 * (
                1 - self.b + self.b * doc_len / max(self.avgdl, 1)
            )
            score += idf * numerator / denominator

        return score

    def search(self, query: str, documents: list[str]) -> list[tuple[int, float]]:
        """Search and return (doc_idx, score) pairs."""
        results = []
        for idx, doc in enumerate(documents):
            score = self.score(query, idx, doc)
            if score > 0:
                results.append((idx, score))
        results.sort(key=lambda x: x[1], reverse=True)
        return results


# ============================================================================
# Temporal Scorer
# ============================================================================


class TemporalScorer:
    """Score documents based on recency and freshness."""

    def __init__(self, half_life_days: float = 30.0):
        self.half_life = timedelta(days=half_life_days)

    def score(self, updated_at: datetime | None, now: datetime | None = None) -> float:
        """Compute temporal score with exponential decay."""
        if updated_at is None:
            return 0.5  # Default for unknown dates

        if now is None:
            now = datetime.now()

        age = now - updated_at
        half_life_seconds = self.half_life.total_seconds()

        # Exponential decay: score = 2^(-age / half_life)
        # At age=0: score=1.0, at half_life: score=0.5
        decay_factor = age.total_seconds() / half_life_seconds
        return math.pow(0.5, decay_factor)


# ============================================================================
# KG Boost Calculator
# ============================================================================


class KGBooster:
    """Boost scores based on Knowledge Graph connectivity."""

    def __init__(self, kg: KnowledgeGraph | None = None):
        self.kg = kg

    def set_kg(self, kg: KnowledgeGraph) -> None:
        """Set the knowledge graph reference."""
        self.kg = kg

    def boost(self, entity_id: str | None) -> float:
        """Calculate boost based on entity connectivity."""
        if self.kg is None or entity_id is None:
            return 0.0

        try:
            # Get entity and count connections
            entity = self.kg.get_entity(entity_id)
            if entity is None:
                return 0.0

            # Count outgoing and incoming relations
            outgoing = self.kg.query_relations(RelationQuery(source_id=entity_id))
            incoming = self.kg.query_relations(RelationQuery(target_id=entity_id))

            # More connections = higher boost (capped at 1.0)
            # Use log scale to prevent outliers
            n_connections = len(outgoing) + len(incoming)
            return min(1.0, math.log10(max(n_connections, 1) + 1))

        except Exception:
            return 0.0


# ============================================================================
# Reranking Pipeline
# ============================================================================


class Reranker:
    """Multi-stage reranking pipeline for memory retrieval."""

    def __init__(self, config: RerankConfig | None = None):
        self.config = config or RerankConfig()
        self.bm25 = BM25()
        self.temporal = TemporalScorer(self.config.temporal_decay_days)
        self.kg_booster = KGBooster()

    def set_kg(self, kg: KnowledgeGraph) -> None:
        """Set knowledge graph for boost calculations."""
        self.kg_booster.set_kg(kg)

    def rerank(
        self,
        query: str,
        results: list[SearchResult],
        now: datetime | None = None,
    ) -> list[RerankResult]:
        """
        Rerank search results through the full pipeline.

        Args:
            query: The search query
            results: Initial search results from Palace Index
            now: Current time for temporal scoring

        Returns:
            Reranked results sorted by final_score
        """
        if not results:
            return []

        if now is None:
            now = datetime.now()

        # Stage 1: Build BM25 index and compute hybrid scores
        reranked = self._compute_hybrid_scores(query, results)

        # Stage 2: Apply temporal and KG boosts
        reranked = self._apply_boosts(reranked, now)

        # Stage 3: Diversity filtering (MMR)
        reranked = self._diversity_filter(reranked)

        # Sort by final score and limit
        reranked.sort(key=lambda x: x.final_score, reverse=True)
        return reranked[: self.config.final_k]

    def _compute_hybrid_scores(
        self,
        query: str,
        results: list[SearchResult],
    ) -> list[RerankResult]:
        """Stage 1: Compute BM25 + Vector hybrid scores."""
        # Extract documents for BM25
        documents = [r.drawer.content for r in results]

        # Fit BM25 on documents
        self.bm25.fit(documents)

        # Get BM25 scores
        bm25_scores = {idx: score for idx, score in self.bm25.search(query, documents)}

        # Normalize scores to [0, 1] range
        max_bm25 = max(bm25_scores.values()) if bm25_scores else 1.0
        max_vector = max(r.score for r in results) if results else 1.0

        reranked = []
        for idx, result in enumerate(results):
            # Normalize scores
            bm25_norm = bm25_scores.get(idx, 0.0) / max(max_bm25, 1e-6)
            vector_norm = result.score / max(max_vector, 1e-6)

            # Weighted combination
            hybrid = (
                self.config.bm25_weight * bm25_norm
                + self.config.vector_weight * vector_norm
            )

            # Extract metadata from drawer
            drawer_metadata = result.drawer.metadata or {}

            reranked.append(
                RerankResult(
                    drawer_id=result.drawer.id,
                    content=result.drawer.content,
                    wing_id=result.wing.id,
                    room_id=result.room.id,
                    metadata=drawer_metadata,
                    bm25_score=bm25_norm,
                    vector_score=vector_norm,
                    hybrid_score=hybrid,
                    updated_at=drawer_metadata.get("updated_at"),
                    entity_id=drawer_metadata.get("entity_id"),
                )
            )

        return reranked

    def _apply_boosts(
        self,
        results: list[RerankResult],
        now: datetime,
    ) -> list[RerankResult]:
        """Stage 2: Apply temporal and KG boosts."""
        for result in results:
            # Temporal boost
            temporal = self.temporal.score(result.updated_at, now)
            result.temporal_score = temporal

            # KG connectivity boost
            kg_boost = self.kg_booster.boost(result.entity_id)
            result.kg_boost = kg_boost

            # Combine: hybrid + temporal + kg_boost
            result.final_score = (
                result.hybrid_score
                + self.config.temporal_weight * temporal
                + self.config.kg_boost_weight * kg_boost
            )

        return results

    def _diversity_filter(
        self,
        results: list[RerankResult],
    ) -> list[RerankResult]:
        """Stage 3: MMR-style diversity filtering."""
        if len(results) <= 1:
            return results

        selected: list[RerankResult] = []
        remaining = list(results)

        # Always include top result
        selected.append(remaining.pop(0))

        while remaining and len(selected) < self.config.final_k:
            best_idx = 0
            best_score = -1.0

            for idx, candidate in enumerate(remaining):
                # Relevance score
                relevance = candidate.final_score

                # Diversity penalty: max similarity to selected
                max_sim = 0.0
                for s in selected:
                    sim = self._similarity(candidate.content, s.content)
                    max_sim = max(max_sim, sim)

                # MMR score
                mmr_score = (
                    self.config.mmr_lambda * relevance
                    - (1 - self.config.mmr_lambda) * max_sim
                )

                if mmr_score > best_score:
                    best_score = mmr_score
                    best_idx = idx

            if best_score > 0:
                selected.append(remaining.pop(best_idx))
            else:
                break

        return selected

    def _similarity(self, text1: str, text2: str) -> float:
        """Compute simple text similarity using token overlap (Jaccard)."""
        tokens1 = set(self.bm25.tokenize(text1))
        tokens2 = set(self.bm25.tokenize(text2))

        if not tokens1 or not tokens2:
            return 0.0

        intersection = len(tokens1 & tokens2)
        union = len(tokens1 | tokens2)
        return intersection / max(union, 1)


# ============================================================================
# Convenience Functions
# ============================================================================


def rerank_search_results(
    query: str,
    results: list[SearchResult],
    kg: KnowledgeGraph | None = None,
    config: RerankConfig | None = None,
) -> list[RerankResult]:
    """
    Convenience function to rerank search results.

    Args:
        query: The search query
        results: Initial search results
        kg: Optional knowledge graph for boost
        config: Optional reranking configuration

    Returns:
        Reranked results
    """
    reranker = Reranker(config)
    if kg is not None:
        reranker.set_kg(kg)
    return reranker.rerank(query, results)
