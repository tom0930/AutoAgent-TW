"""
Token Compression - Q4_K_M Style Local Model Compression

Implements token-aware compression for memory content:
1. Structure-aware summarization
2. Key phrase extraction
3. Quantization-style compression (Q4_K_M inspired)
4. Loss preservation for critical content

Design philosophy: Preserve maximum information in minimum tokens.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass  # No external dependencies needed

# ============================================================================
# Configuration
# ============================================================================


@dataclass
class CompressionConfig:
    """Configuration for token compression."""

    # Target compression ratio
    target_ratio: float = 0.4  # 60% reduction

    # Token estimation
    chars_per_token_zh: float = 2.0  # Chinese: ~2 chars/token
    chars_per_token_en: float = 4.0  # English: ~4 chars/token

    # Structure preservation
    preserve_headers: bool = True  # Keep section headers
    preserve_code_blocks: bool = True  # Keep code blocks intact
    preserve_links: bool = True  # Keep links visible

    # Compression levels
    min_chunk_tokens: int = 20  # Minimum chunk to compress
    max_summary_ratio: float = 0.3  # Summary <= 30% of original


@dataclass
class CompressionResult:
    """Result of compression operation."""

    original_content: str
    compressed_content: str
    original_tokens: int
    compressed_tokens: int
    compression_ratio: float  # compressed / original
    reduction_ratio: float  # 1 - compression_ratio

    # Metadata
    preserved_structures: list[str] = field(default_factory=list)
    compressed_sections: list[str] = field(default_factory=list)


# ============================================================================
# Token Estimator
# ============================================================================


class TokenEstimator:
    """Estimate token count for mixed Chinese/English text."""

    def __init__(
        self,
        chars_per_token_zh: float = 2.0,
        chars_per_token_en: float = 4.0,
    ):
        self.chars_zh = chars_per_token_zh
        self.chars_en = chars_per_token_en

    def estimate(self, text: str) -> int:
        """Estimate token count for text."""
        if not text:
            return 0

        # Split into Chinese and non-Chinese segments
        zh_chars = len(re.findall(r"[\u4e00-\u9fff]", text))
        en_chars = len(re.findall(r"[a-zA-Z0-9\s.,!?;:'\"()\[\]{}]", text))
        other_chars = len(text) - zh_chars - en_chars

        zh_tokens = zh_chars / self.chars_zh
        en_tokens = en_chars / self.chars_en
        other_tokens = other_chars / max((self.chars_zh + self.chars_en) / 2, 1)

        return int(math.ceil(zh_tokens + en_tokens + other_tokens))

    def estimate_chunks(self, chunks: list[str]) -> list[int]:
        """Estimate token counts for multiple chunks."""
        return [self.estimate(chunk) for chunk in chunks]


# ============================================================================
# Structure Parser
# ============================================================================


class StructureParser:
    """Parse markdown structure for structure-aware compression."""

    # Patterns
    HEADER_PATTERN = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)
    CODE_BLOCK_PATTERN = re.compile(r"```[\s\S]*?```", re.MULTILINE)
    LINK_PATTERN = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
    LIST_PATTERN = re.compile(r"^[\s]*[-*+]\s+(.+)$", re.MULTILINE)

    def parse_sections(self, text: str) -> list[tuple[str, str, int, int]]:
        """
        Parse text into sections.

        Returns list of (header, content, start, end) tuples.
        """
        sections = []

        # Find all headers
        headers = list(self.HEADER_PATTERN.finditer(text))

        if not headers:
            # No headers, single section
            return [("", text, 0, len(text))]

        # Add content before first header
        if headers[0].start() > 0:
            sections.append(("", text[: headers[0].start()], 0, headers[0].start()))

        # Add each section
        for i, match in enumerate(headers):
            header = match.group(0)
            start = match.start()

            # Find end (next header or EOF)
            if i + 1 < len(headers):
                end = headers[i + 1].start()
            else:
                end = len(text)

            content = text[start:end]
            sections.append((header, content, start, end))

        return sections

    def extract_code_blocks(self, text: str) -> list[tuple[str, int, int]]:
        """Extract code blocks with positions."""
        blocks = []
        for match in self.CODE_BLOCK_PATTERN.finditer(text):
            blocks.append((match.group(0), match.start(), match.end()))
        return blocks

    def extract_links(self, text: str) -> list[tuple[str, str, int, int]]:
        """Extract links with positions."""
        links = []
        for match in self.LINK_PATTERN.finditer(text):
            links.append((match.group(1), match.group(2), match.start(), match.end()))
        return links


# ============================================================================
# Compressor
# ============================================================================


class TokenCompressor:
    """Main compression engine."""

    def __init__(self, config: CompressionConfig | None = None):
        self.config = config or CompressionConfig()
        self.estimator = TokenEstimator(
            self.config.chars_per_token_zh,
            self.config.chars_per_token_en,
        )
        self.parser = StructureParser()

    def compress(self, content: str) -> CompressionResult:
        """
        Compress content using structure-aware compression.

        Args:
            content: Original content to compress

        Returns:
            CompressionResult with compressed content and metadata
        """
        original_tokens = self.estimator.estimate(content)
        target_tokens = int(original_tokens * self.config.target_ratio)

        if original_tokens < self.config.min_chunk_tokens:
            # Too short to compress
            return CompressionResult(
                original_content=content,
                compressed_content=content,
                original_tokens=original_tokens,
                compressed_tokens=original_tokens,
                compression_ratio=1.0,
                reduction_ratio=0.0,
            )

        # Parse structure
        sections = self.parser.parse_sections(content)
        code_blocks = self.parser.extract_code_blocks(content)

        # Protect code blocks
        protected = self._create_protection_map(code_blocks)

        # Compress each section
        compressed_sections = []
        preserved = []
        total_compressed = 0

        for header, section_content, start, end in sections:
            # Check if section overlaps with protected regions
            if self._is_protected(start, end, protected):
                compressed_sections.append(section_content)
                preserved.append(f"code_block:{start}-{end}")
                continue

            # Compress section
            compressed = self._compress_section(header, section_content)
            compressed_sections.append(compressed)

            if compressed != section_content:
                preserved.append(header if header else f"section:{start}-{end}")

        # Combine
        result_content = "\n".join(compressed_sections)
        result_tokens = self.estimator.estimate(result_content)

        # Check if we met target
        if result_tokens > target_tokens:
            # Apply more aggressive compression
            result_content = self._aggressive_compress(result_content, target_tokens)
            result_tokens = self.estimator.estimate(result_content)

        ratio = result_tokens / max(original_tokens, 1)

        return CompressionResult(
            original_content=content,
            compressed_content=result_content,
            original_tokens=original_tokens,
            compressed_tokens=result_tokens,
            compression_ratio=ratio,
            reduction_ratio=1 - ratio,
            preserved_structures=preserved,
            compressed_sections=[s[0] for s in sections if s[0]],
        )

    def _compress_section(self, header: str, content: str) -> str:
        """Compress a single section."""
        if not content.strip():
            return content

        # Preserve header
        lines = content.split("\n")
        if header:
            # First line is header
            body = "\n".join(lines[1:])
        else:
            body = content

        if not body.strip():
            return content

        # Extract key sentences
        sentences = self._split_sentences(body)

        if len(sentences) <= 2:
            # Already minimal
            return content

        # Score sentences by information density
        scored = [(s, self._score_sentence(s)) for s in sentences]
        scored.sort(key=lambda x: x[1], reverse=True)

        # Keep top sentences (target ratio)
        n_keep = max(2, int(len(sentences) * self.config.max_summary_ratio))
        kept = sorted(
            [s for s, _ in scored[:n_keep]],
            key=lambda s: sentences.index(s),
        )

        # Reconstruct
        compressed_body = ". ".join(kept)
        if not compressed_body.endswith((".", "。", "!", "?", "！", "？")):
            compressed_body += "."

        if header:
            return f"{header}\n{compressed_body}"
        return compressed_body

    def _aggressive_compress(self, content: str, target_tokens: int) -> str:
        """Apply more aggressive compression to meet target."""
        current_tokens = self.estimator.estimate(content)

        if current_tokens <= target_tokens:
            return content

        # Strategy 1: Remove filler words
        filler_removed = self._remove_fillers(content)
        if self.estimator.estimate(filler_removed) <= target_tokens:
            return filler_removed

        # Strategy 2: Extract key phrases only
        key_phrases = self._extract_key_phrases(filler_removed)
        return key_phrases

    def _remove_fillers(self, text: str) -> str:
        """Remove filler words and phrases."""
        # English fillers
        fillers = [
            r"\bplease\b",
            r"\bkindly\b",
            r"\bbasically\b",
            r"\bactually\b",
            r"\bsimply\b",
            r"\bjust\b",
            r"\bquite\b",
            r"\brather\b",
            r"\bsomewhat\b",
            r"\bin order to\b",
            r"\bdue to the fact that\b",
            r"\bat this point in time\b",
        ]

        result = text
        for filler in fillers:
            result = re.sub(filler, "", result, flags=re.IGNORECASE)

        # Clean up extra whitespace
        result = re.sub(r"\s+", " ", result)
        return result.strip()

    def _extract_key_phrases(self, text: str) -> str:
        """Extract key phrases using TF-IDF style scoring."""
        sentences = self._split_sentences(text)
        if not sentences:
            return text

        # Score each sentence
        scored = [(s, self._score_sentence(s)) for s in sentences]

        # Keep top 30% by score
        n_keep = max(1, int(len(sentences) * 0.3))
        top = sorted(scored, key=lambda x: x[1], reverse=True)[:n_keep]

        # Sort by original position
        kept = sorted(top, key=lambda x: sentences.index(x[0]))

        return ". ".join(s for s, _ in kept)

    def _split_sentences(self, text: str) -> list[str]:
        """Split text into sentences."""
        # Handle both English and Chinese punctuation
        pattern = r"(?<=[.。!！?？\n])\s*"
        sentences = re.split(pattern, text)
        return [s.strip() for s in sentences if s.strip()]

    def _score_sentence(self, sentence: str) -> float:
        """Score sentence by information density."""
        tokens = self.estimator.estimate(sentence)
        if tokens == 0:
            return 0.0

        # Factors that increase score
        score = 0.0

        # Has numbers (data/facts)
        if re.search(r"\d+", sentence):
            score += 0.2

        # Has proper nouns (capitalized words in English)
        if re.search(r"\b[A-Z][a-z]+", sentence):
            score += 0.1

        # Has Chinese technical terms
        if re.search(r"[參數設定規格協議協定配置狀態結果輸出入]", sentence):
            score += 0.15

        # Has code-like patterns
        if re.search(r"[a-z_]+\(", sentence):
            score += 0.1

        # Not too short or too long
        if 5 <= tokens <= 30:
            score += 0.1

        # Contains key action words
        if re.search(r"(實作|建立|完成|修復|設定|執行|create|implement|fix|config|run)", sentence, re.I):
            score += 0.15

        # Normalize by token count (density)
        return score / max(tokens / 10, 1)

    def _create_protection_map(
        self,
        code_blocks: list[tuple[str, int, int]],
    ) -> list[tuple[int, int]]:
        """Create map of protected regions."""
        return [(start, end) for _, start, end in code_blocks]

    def _is_protected(
        self,
        start: int,
        end: int,
        protected: list[tuple[int, int]],
    ) -> bool:
        """Check if region overlaps with protected areas."""
        for p_start, p_end in protected:
            if start < p_end and end > p_start:
                return True
        return False


# ============================================================================
# Convenience Functions
# ============================================================================


def compress_content(
    content: str,
    target_ratio: float = 0.4,
) -> CompressionResult:
    """
    Convenience function to compress content.

    Args:
        content: Content to compress
        target_ratio: Target compression ratio (compressed/original)

    Returns:
        CompressionResult
    """
    config = CompressionConfig(target_ratio=target_ratio)
    compressor = TokenCompressor(config)
    return compressor.compress(content)


def estimate_tokens(content: str) -> int:
    """Convenience function to estimate token count."""
    return TokenEstimator().estimate(content)
