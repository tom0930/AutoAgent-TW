"""
Tests for Reranking Pipeline (rerank.py)
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

from src.core.memory.rerank import (
    RerankConfig,
    RerankResult,
    Reranker,
    BM25,
    TemporalScorer,
    KGBooster,
    rerank_search_results,
)


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def rerank_config():
    """Standard rerank config for testing."""
    return RerankConfig(
        hybrid_k=10,
        final_k=5,
        bm25_weight=0.3,
        vector_weight=0.7,
        temporal_decay_days=30.0,
    )


@pytest.fixture
def sample_search_results():
    """Sample search results for testing."""
    now = datetime.now()
    return [
        MagicMock(
            drawer=MagicMock(
                id="d1",
                content="Python 是一種流行的程式語言，廣泛用於 Web 開發。",
                metadata={"updated_at": now - timedelta(days=1)},
            ),
            room=MagicMock(id="r1"),
            wing=MagicMock(id="w1"),
            score=0.9,
        ),
        MagicMock(
            drawer=MagicMock(
                id="d2",
                content="JavaScript 用於前端開發，React 是熱門框架。",
                metadata={"updated_at": now - timedelta(days=10)},
            ),
            room=MagicMock(id="r1"),
            wing=MagicMock(id="w1"),
            score=0.8,
        ),
        MagicMock(
            drawer=MagicMock(
                id="d3",
                content="Python 資料科學生態系統包含 NumPy, Pandas, Scikit-learn。",
                metadata={"updated_at": now - timedelta(days=5)},
            ),
            room=MagicMock(id="r2"),
            wing=MagicMock(id="w1"),
            score=0.7,
        ),
        MagicMock(
            drawer=MagicMock(
                id="d4",
                content="TypeScript 是 JavaScript 的超集，提供靜態型別檢查。",
                metadata={"updated_at": now - timedelta(days=60)},
            ),
            room=MagicMock(id="r1"),
            wing=MagicMock(id="w2"),
            score=0.6,
        ),
    ]


# ============================================================================
# BM25 Tests
# ============================================================================


class TestBM25:
    """Tests for BM25 ranking function."""

    def test_tokenize_english(self):
        """Test tokenization of English text."""
        bm25 = BM25()
        tokens = bm25.tokenize("Hello World Test 123")
        assert tokens == ["hello", "world", "test", "123"]

    def test_tokenize_chinese(self):
        """Test tokenization of Chinese text."""
        bm25 = BM25()
        tokens = bm25.tokenize("你好世界測試")
        assert tokens == ["你好世界測試"]

    def test_tokenize_mixed(self):
        """Test tokenization of mixed Chinese/English."""
        bm25 = BM25()
        tokens = bm25.tokenize("Python 程式語言")
        assert "python" in tokens
        assert "程式語言" in tokens

    def test_fit_and_search(self):
        """Test BM25 fit and search."""
        bm25 = BM25()
        docs = [
            "Python is a programming language",
            "JavaScript for web development",
            "Python data science libraries",
        ]
        bm25.fit(docs)
        results = bm25.search("Python programming", docs)

        # Should find Python docs
        assert len(results) >= 1
        # First doc should mention Python
        assert results[0][0] in [0, 2]

    def test_empty_query(self):
        """Test search with empty query."""
        bm25 = BM25()
        docs = ["Hello world"]
        bm25.fit(docs)
        results = bm25.search("", docs)
        # Empty query returns no matches
        assert len(results) == 0

    def test_empty_documents(self):
        """Test search with empty documents."""
        bm25 = BM25()
        bm25.fit([])
        results = bm25.search("test", [])
        assert len(results) == 0


# ============================================================================
# TemporalScorer Tests
# ============================================================================


class TestTemporalScorer:
    """Tests for temporal scoring."""

    def test_score_now(self):
        """Test score for current timestamp."""
        scorer = TemporalScorer(half_life_days=30.0)
        now = datetime.now()
        score = scorer.score(now, now)
        assert score == pytest.approx(1.0, abs=0.01)

    def test_score_half_life(self):
        """Test score at half-life."""
        scorer = TemporalScorer(half_life_days=30.0)
        now = datetime.now()
        half_life_ago = now - timedelta(days=30)
        score = scorer.score(half_life_ago, now)
        assert score == pytest.approx(0.5, abs=0.05)

    def test_score_old(self):
        """Test score for old content."""
        scorer = TemporalScorer(half_life_days=30.0)
        now = datetime.now()
        old = now - timedelta(days=90)  # 3 half-lives
        score = scorer.score(old, now)
        # Should be ~0.125 (0.5^3)
        assert 0.1 < score < 0.2

    def test_score_none(self):
        """Test score for unknown timestamp."""
        scorer = TemporalScorer()
        score = scorer.score(None)
        # Default score for unknown
        assert score == 0.5


# ============================================================================
# KGBooster Tests
# ============================================================================


class TestKGBooster:
    """Tests for Knowledge Graph boost."""

    def test_boost_no_kg(self):
        """Test boost without knowledge graph."""
        booster = KGBooster()
        assert booster.boost("entity1") == 0.0

    def test_boost_no_entity(self):
        """Test boost without entity ID."""
        booster = KGBooster()
        assert booster.boost(None) == 0.0

    def test_boost_with_kg(self):
        """Test boost with mock KG."""
        from src.core.memory.kg import RelationQuery
        
        booster = KGBooster()
        mock_kg = MagicMock()
        mock_entity = MagicMock()
        mock_kg.get_entity.return_value = mock_entity
        # Mock returns lists for query_relations
        mock_kg.query_relations.return_value = [MagicMock()] * 3  # 3 connections each way
        booster.set_kg(mock_kg)

        boost = booster.boost("entity1")
        # Should have positive boost (6 connections total)
        assert boost > 0

    def test_boost_many_connections(self):
        """Test boost with many connections."""
        booster = KGBooster()
        mock_kg = MagicMock()
        mock_entity = MagicMock()
        mock_kg.get_entity.return_value = mock_entity
        # 100 connections each way
        mock_kg.query_relations.return_value = [MagicMock()] * 100
        booster.set_kg(mock_kg)

        boost = booster.boost("entity1")
        # Should cap at 1.0
        assert boost <= 1.0


# ============================================================================
# Reranker Tests
# ============================================================================


class TestReranker:
    """Tests for full reranking pipeline."""

    def test_rerank_empty_results(self, rerank_config):
        """Test reranking with no results."""
        reranker = Reranker(rerank_config)
        results = reranker.rerank("test", [])
        assert results == []

    def test_rerank_basic(self, rerank_config, sample_search_results):
        """Test basic reranking."""
        reranker = Reranker(rerank_config)
        results = reranker.rerank("Python", sample_search_results)

        # Should return up to final_k results
        assert len(results) <= rerank_config.final_k

        # Results should have scores
        for r in results:
            assert r.hybrid_score >= 0
            assert r.temporal_score >= 0
            assert r.final_score >= 0

    def test_rerank_temporal_boost(self, rerank_config, sample_search_results):
        """Test that newer content gets temporal boost."""
        reranker = Reranker(rerank_config)
        results = reranker.rerank("Python", sample_search_results)

        # Find Python results
        python_results = [r for r in results if "Python" in r.content]

        # Most recent Python result should have highest temporal score
        if len(python_results) >= 2:
            sorted_by_temporal = sorted(
                python_results, key=lambda x: x.temporal_score, reverse=True
            )
            # d1 was updated 1 day ago, d3 was 5 days ago
            assert sorted_by_temporal[0].drawer_id == "d1"

    def test_rerank_respects_final_k(self, rerank_config, sample_search_results):
        """Test that final_k limit is respected."""
        config = RerankConfig(hybrid_k=20, final_k=2)
        reranker = Reranker(config)
        results = reranker.rerank("Python", sample_search_results)
        assert len(results) <= 2

    def test_rerank_diversity(self, rerank_config):
        """Test diversity filtering reduces duplicates."""
        # Create similar results
        similar_results = [
            MagicMock(
                drawer=MagicMock(
                    id=f"d{i}",
                    content="Python is great for programming",
                    metadata={"updated_at": datetime.now()},
                ),
                room=MagicMock(id="r1"),
                wing=MagicMock(id="w1"),
                score=0.9 - i * 0.1,
            )
            for i in range(10)
        ]

        reranker = Reranker(rerank_config)
        results = reranker.rerank("Python programming", similar_results)

        # Should return fewer due to dedup
        assert len(results) <= rerank_config.final_k


# ============================================================================
# Convenience Function Tests
# ============================================================================


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_rerank_search_results(self, sample_search_results):
        """Test convenience rerank function."""
        results = rerank_search_results("Python", sample_search_results)
        assert isinstance(results, list)
        for r in results:
            assert isinstance(r, RerankResult)

    def test_rerank_with_config(self, sample_search_results):
        """Test convenience function with custom config."""
        config = RerankConfig(final_k=2)
        results = rerank_search_results("Python", sample_search_results, config=config)
        assert len(results) <= 2
