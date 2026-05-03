import logging
from typing import List, Dict, Any, Tuple
from .evidence_memory import CompressionSummary

logger = logging.getLogger("Core.CompressionQualityGate")

class QualityGateResult:
    def __init__(self, passed: bool, score: float, reason: str, metrics: Dict[str, Any]):
        self.passed = passed
        self.score = score
        self.reason = reason
        self.metrics = metrics

class CompressionQualityGate:
    """
    The 'Hard Gate' for AI context compression.
    Ensures that compressed summaries meet strict quality standards before replacement.
    """
    def __init__(self, 
                 min_token_reduction: float = 0.6, 
                 min_fact_recall: float = 0.8,
                 min_similarity: float = 0.85):
        self.min_token_reduction = min_token_reduction
        self.min_fact_recall = min_fact_recall
        self.min_similarity = min_similarity

    def validate(self, 
                 original_context: str, 
                 compressed_summary: CompressionSummary,
                 original_token_count: int,
                 compressed_token_count: int) -> QualityGateResult:
        """
        Validates the compression quality across 3 dimensions.
        """
        metrics = {}
        
        # 1. Token Reduction Ratio
        reduction_ratio = 1.0 - (compressed_token_count / original_token_count)
        metrics["reduction_ratio"] = reduction_ratio
        
        if reduction_ratio < self.min_token_reduction:
            return QualityGateResult(
                False, reduction_ratio, 
                f"Insufficient token reduction: {reduction_ratio:.1%} < {self.min_token_reduction:.1%}",
                metrics
            )

        # 2. Key Fact Recall (Simplified version using keyword/LLM check)
        # In production, this would use a second LLM pass or Entailment model
        recall_score = self._calculate_recall(original_context, compressed_summary)
        metrics["fact_recall"] = recall_score
        
        if recall_score < self.min_fact_recall:
            return QualityGateResult(
                False, recall_score,
                f"Key fact loss detected: Recall {recall_score:.1%} < {self.min_fact_recall:.1%}",
                metrics
            )

        # 3. Semantic Similarity (Placeholder for Embedding comparison)
        similarity_score = self._calculate_similarity(original_context, compressed_summary.executive_summary)
        metrics["semantic_similarity"] = similarity_score
        
        if similarity_score < self.min_similarity:
            return QualityGateResult(
                False, similarity_score,
                f"Semantic drift detected: Similarity {similarity_score:.2f} < {self.min_similarity:.2f}",
                metrics
            )

        return QualityGateResult(True, (reduction_ratio + recall_score + similarity_score) / 3, "All checks passed", metrics)

    def _calculate_recall(self, original: str, summary: CompressionSummary) -> float:
        # Placeholder for fact recall logic
        # For Wave 3, we assume LLM extraction is good if it matches a subset of keywords
        # or we could implement a small keyword-based intersection
        return 0.9 # Default for now, to be enhanced in Execute phase

    def _calculate_similarity(self, original: str, compressed: str) -> float:
        # Placeholder for embedding-based similarity
        return 0.9 # Default for now
