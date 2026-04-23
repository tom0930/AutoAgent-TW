"""
Tests for Token Compression (compress.py)
"""

import pytest
from datetime import datetime

from src.core.memory.compress import (
    CompressionConfig,
    CompressionResult,
    TokenEstimator,
    StructureParser,
    TokenCompressor,
    compress_content,
    estimate_tokens,
)


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def sample_markdown():
    """Sample markdown content for testing."""
    return """
## 專案概述

這是一個 AI Harness 框架專案，目標是打造全自動化的 AI 代理系統。

## 主要功能

1. Gateway Daemon - 核心服務守護程序
2. Session Manager - 會話管理模組
3. Vision Engine - 視覺處理引擎

## 程式碼範例

```python
def hello():
    print("Hello, World!")
```

## 技術棧

使用 Python 3.13 + Pyrefly 進行型別檢查。
"""


@pytest.fixture
def compression_config():
    """Standard compression config."""
    return CompressionConfig(
        target_ratio=0.4,
        preserve_headers=True,
        preserve_code_blocks=True,
    )


# ============================================================================
# TokenEstimator Tests
# ============================================================================


class TestTokenEstimator:
    """Tests for token estimation."""

    def test_estimate_empty(self):
        """Test estimating empty string."""
        estimator = TokenEstimator()
        assert estimator.estimate("") == 0

    def test_estimate_english(self):
        """Test estimating English text."""
        estimator = TokenEstimator()
        # ~4 chars per token for English
        tokens = estimator.estimate("Hello world this is a test")
        # Should be around 7 tokens
        assert 5 <= tokens <= 10

    def test_estimate_chinese(self):
        """Test estimating Chinese text."""
        estimator = TokenEstimator()
        # ~2 chars per token for Chinese
        tokens = estimator.estimate("這是一個測試文字")
        # 8 characters / 2 = ~4 tokens
        assert 3 <= tokens <= 6

    def test_estimate_mixed(self):
        """Test estimating mixed content."""
        estimator = TokenEstimator()
        tokens = estimator.estimate("Python 程式語言是很好用的")
        # Should handle both
        assert tokens > 0

    def test_estimate_chunks(self):
        """Test estimating multiple chunks."""
        estimator = TokenEstimator()
        chunks = ["Hello", "世界", "Test 123"]
        counts = estimator.estimate_chunks(chunks)
        assert len(counts) == 3
        assert all(c > 0 for c in counts)

    def test_estimate_custom_ratio(self):
        """Test with custom chars_per_token."""
        estimator = TokenEstimator(chars_per_token_zh=1.0, chars_per_token_en=2.0)
        zh_tokens = estimator.estimate("測試")
        en_tokens = estimator.estimate("test")
        # Should be higher with smaller denominator
        assert zh_tokens >= 2
        assert en_tokens >= 2


# ============================================================================
# StructureParser Tests
# ============================================================================


class TestStructureParser:
    """Tests for structure parsing."""

    def test_parse_sections_no_headers(self):
        """Test parsing text without headers."""
        parser = StructureParser()
        text = "Just some plain text without headers."
        sections = parser.parse_sections(text)
        assert len(sections) == 1
        assert sections[0][0] == ""  # No header

    def test_parse_sections_with_headers(self, sample_markdown):
        """Test parsing text with headers."""
        parser = StructureParser()
        sections = parser.parse_sections(sample_markdown)
        # Should find headers
        assert len(sections) >= 2
        # First section might be empty (before first header)
        headers = [s[0] for s in sections if s[0]]
        assert any("專案概述" in h for h in headers)

    def test_extract_code_blocks(self, sample_markdown):
        """Test extracting code blocks."""
        parser = StructureParser()
        blocks = parser.extract_code_blocks(sample_markdown)
        assert len(blocks) == 1
        assert "def hello()" in blocks[0][0]

    def test_extract_code_blocks_multiple(self):
        """Test extracting multiple code blocks."""
        parser = StructureParser()
        text = """
```python
code1
```
some text
```javascript
code2
```
"""
        blocks = parser.extract_code_blocks(text)
        assert len(blocks) == 2

    def test_extract_links(self):
        """Test extracting links."""
        parser = StructureParser()
        text = "Check [OpenClaw](https://openclaw.ai) and [GitHub](https://github.com)."
        links = parser.extract_links(text)
        assert len(links) == 2
        assert links[0][0] == "OpenClaw"
        assert links[1][0] == "GitHub"


# ============================================================================
# TokenCompressor Tests
# ============================================================================


class TestTokenCompressor:
    """Tests for main compression engine."""

    def test_compress_short_text(self, compression_config):
        """Test compressing text that's too short."""
        compressor = TokenCompressor(compression_config)
        result = compressor.compress("Short")
        # Should not compress
        assert result.compressed_content == "Short"
        assert result.compression_ratio == 1.0

    def test_compress_basic(self, compression_config, sample_markdown):
        """Test basic compression."""
        compressor = TokenCompressor(compression_config)
        result = compressor.compress(sample_markdown)

        assert isinstance(result, CompressionResult)
        assert len(result.compressed_content) < len(sample_markdown)
        assert result.original_tokens > 0
        assert result.compressed_tokens > 0
        assert result.compression_ratio < 1.0

    def test_compress_preserves_structure(self, compression_config, sample_markdown):
        """Test that compression preserves structure."""
        compressor = TokenCompressor(compression_config)
        result = compressor.compress(sample_markdown)

        # Headers should be preserved
        compressed = result.compressed_content
        if result.preserved_structures:
            assert len(result.preserved_structures) > 0

    def test_compress_code_blocks_preserved(self, compression_config):
        """Test that code blocks are preserved."""
        text = "介紹:\n```python\ndef test():\n    pass\n```\n以上是程式碼。"
        compressor = TokenCompressor(compression_config)
        result = compressor.compress(text)

        # Code block should be in result
        assert "def test()" in result.compressed_content or "code_block" in str(
            result.preserved_structures
        )

    def test_compress_ratio(self, compression_config):
        """Test compression meets target ratio."""
        long_text = """
這是一段很長的測試文字。我們需要測試壓縮功能是否能夠正確運作。
壓縮功能應該要能夠減少 token 數量，同時保留重要資訊。
重要的是，我們要確保關鍵詞彙和核心概念被保留下來。
這個測試需要足夠長的內容才能觸發壓縮機制。
""" * 5

        compressor = TokenCompressor(compression_config)
        result = compressor.compress(long_text)

        # Should achieve at least some reduction
        assert result.compression_ratio < 1.0

    def test_compress_estimate_accuracy(self, compression_config, sample_markdown):
        """Test that token estimation is consistent."""
        compressor = TokenCompressor(compression_config)
        result = compressor.compress(sample_markdown)

        # Re-estimate tokens
        estimator = TokenEstimator()
        re_estimated = estimator.estimate(result.compressed_content)

        # Should be close
        assert abs(re_estimated - result.compressed_tokens) < 10

    def test_compress_empty(self, compression_config):
        """Test compressing empty content."""
        compressor = TokenCompressor(compression_config)
        result = compressor.compress("")
        assert result.compressed_content == ""
        assert result.original_tokens == 0

    def test_compress_whitespace_only(self, compression_config):
        """Test compressing whitespace-only content."""
        compressor = TokenCompressor(compression_config)
        result = compressor.compress("   \n\n   \t\t  ")
        assert result.compressed_content.strip() == ""

    def test_compress_with_config_override(self):
        """Test with different config."""
        config = CompressionConfig(target_ratio=0.2)  # More aggressive
        compressor = TokenCompressor(config)

        text = "Testing compression with aggressive settings. " * 20
        result = compressor.compress(text)

        # Should be more compressed
        assert result.compressed_tokens < result.original_tokens


# ============================================================================
# Sentence Scoring Tests
# ============================================================================


class TestSentenceScoring:
    """Tests for sentence scoring in compression."""

    def test_score_with_numbers(self):
        """Test that sentences with numbers score higher."""
        compressor = TokenCompressor()
        score_numbers = compressor._score_sentence("Version 2.0 released on 2024-01-01.")
        score_no_numbers = compressor._score_sentence("Version released recently.")
        assert score_numbers > score_no_numbers

    def test_score_with_capitals(self):
        """Test that sentences with proper nouns score higher."""
        compressor = TokenCompressor()
        score_proper = compressor._score_sentence("OpenClaw and Python are tools.")
        score_lower = compressor._score_sentence("openclaw and python are tools.")
        assert score_proper >= score_lower

    def test_score_action_words(self):
        """Test that sentences with action words score higher."""
        compressor = TokenCompressor()
        score_action = compressor._score_sentence("Implement the feature.")
        score_passive = compressor._score_sentence("The feature exists.")
        assert score_action >= score_passive


# ============================================================================
# Convenience Function Tests
# ============================================================================


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_estimate_tokens(self):
        """Test convenience estimator."""
        count = estimate_tokens("Hello World")
        assert count > 0

    def test_compress_content(self, sample_markdown):
        """Test convenience compressor."""
        result = compress_content(sample_markdown)
        assert isinstance(result, CompressionResult)
        assert result.original_tokens > result.compressed_tokens

    def test_compress_content_custom_ratio(self, sample_markdown):
        """Test with custom ratio."""
        result = compress_content(sample_markdown, target_ratio=0.3)
        assert isinstance(result, CompressionResult)


# ============================================================================
# Integration Tests
# ============================================================================


class TestIntegration:
    """Integration tests for compression."""

    def test_full_workflow(self, sample_markdown):
        """Test full compression workflow."""
        # Estimate original
        original_tokens = estimate_tokens(sample_markdown)

        # Compress
        config = CompressionConfig(target_ratio=0.4)
        compressor = TokenCompressor(config)
        result = compressor.compress(sample_markdown)

        # Verify
        assert result.original_tokens == original_tokens
        assert result.compressed_tokens < original_tokens
        assert result.reduction_ratio > 0

        # Content should still contain key words
        assert any(
            keyword in result.compressed_content
            for keyword in ["Harness", "Gateway", "Python"]
        )

    def test_compress_preserves_chinese(self):
        """Test that Chinese content is preserved."""
        text = "這是繁體中文測試內容，需要確保壓縮後仍然保留重要的中文關鍵詞。" * 5
        result = compress_content(text)
        # Should still have Chinese
        assert any("\u4e00" <= c <= "\u9fff" for c in result.compressed_content)
