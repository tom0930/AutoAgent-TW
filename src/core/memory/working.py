"""
Working Memory Module - Layer 1 of Hybrid Palace Architecture

Manages short-term/working memory using Markdown files:
- MEMORY.md (long-term curated memory)
- memory/YYYY-MM-DD.md (daily notes)

Features:
- Auto Flush: Triggered when context approaches token limit
- Compression: Summarize and compress before writing to long-term index
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Callable, Any
import json
import re


# Constants
TRIGGER_THRESHOLD = 0.75  # 75% of max_tokens
FLUSH_TARGET = 0.4        # Compress to 40%


@dataclass
class FlushEvent:
    """Represents a flush event"""
    timestamp: datetime
    tokens_before: int
    tokens_after: int
    compression_ratio: float
    target_file: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "tokens_before": self.tokens_before,
            "tokens_after": self.tokens_after,
            "compression_ratio": self.compression_ratio,
            "target_file": self.target_file,
        }


@dataclass
class WorkingMemoryConfig:
    """Configuration for Working Memory"""
    workspace_root: Path
    max_tokens: int = 128000  # Default for modern LLMs
    trigger_threshold: float = TRIGGER_THRESHOLD
    flush_target: float = FLUSH_TARGET
    auto_flush_enabled: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "workspace_root": str(self.workspace_root),
            "max_tokens": self.max_tokens,
            "trigger_threshold": self.trigger_threshold,
            "flush_target": self.flush_target,
            "auto_flush_enabled": self.auto_flush_enabled,
        }


class WorkingMemory:
    """
    Working Memory Manager - OpenClaw-style Layer 1
    
    Manages:
    - MEMORY.md: Long-term curated memory
    - memory/YYYY-MM-DD.md: Daily notes
    
    Architecture:
    - Layer 1: Working Memory (this module) - Markdown + Auto Flush
    - Layer 2: Long-term Palace - Wings/Rooms/Drawers + Knowledge Graph
    - Layer 3: Reranking Pipeline - Hybrid Search + Temporal + KG Boost
    """
    
    def __init__(self, config: WorkingMemoryConfig):
        self.config = config
        self.memory_dir = config.workspace_root / "memory"
        self.memory_file = config.workspace_root / "MEMORY.md"
        self._flush_history: list[FlushEvent] = []
        
        # Ensure memory directory exists
        self.memory_dir.mkdir(parents=True, exist_ok=True)
    
    def get_daily_file(self, date: Optional[datetime] = None) -> Path:
        """Get the daily memory file path"""
        if date is None:
            date = datetime.now()
        return self.memory_dir / f"{date.strftime('%Y-%m-%d')}.md"
    
    def should_flush(self, current_tokens: int) -> bool:
        """Check if flush should be triggered"""
        if not self.config.auto_flush_enabled:
            return False
        return current_tokens / self.config.max_tokens >= self.config.trigger_threshold
    
    def flush(
        self, 
        content: str, 
        current_tokens: int,
        summary_func: Optional[Callable[[str, int], str]] = None,
    ) -> tuple[str, int, FlushEvent]:
        """
        Flush working memory content to long-term storage.
        
        Args:
            content: Content to flush
            current_tokens: Current token count (use actual if available, or estimate)
            summary_func: Optional custom summarization function (content, target_tokens) -> summary
            
        Returns:
            tuple: (compressed_content, new_tokens, flush_event)
        """
        # Use actual content tokens if not provided
        actual_tokens = self._estimate_tokens(content)
        if current_tokens <= 0:
            current_tokens = actual_tokens
        
        # Calculate target tokens
        target_tokens = int(self.config.max_tokens * self.config.flush_target)
        
        # Compress content
        if summary_func:
            compressed = summary_func(content, target_tokens)
        else:
            compressed = self._compress(content, target_tokens)
        
        new_tokens = self._estimate_tokens(compressed)
        
        # Write to daily file
        daily_file = self.get_daily_file()
        self._append_to_file(daily_file, compressed)
        
        # Record flush event (use actual tokens for ratio)
        compression_ratio = new_tokens / actual_tokens if actual_tokens > 0 else 0
        event = FlushEvent(
            timestamp=datetime.now(),
            tokens_before=current_tokens,
            tokens_after=new_tokens,
            compression_ratio=compression_ratio,
            target_file=str(daily_file)
        )
        self._flush_history.append(event)
        
        return compressed, new_tokens, event
    
    def _compress(self, content: str, target_tokens: int) -> str:
        """
        Compress content to target token count.
        
        Phase 1: Structure-aware truncation
        Phase 2: Will use Q4_K_M local model for intelligent summarization
        """
        current_tokens = self._estimate_tokens(content)
        
        # If already within target, return as-is
        if current_tokens <= target_tokens:
            return content
        
        # Phase 1: Structure-aware compression
        # 1. Split into sections (by ### headers)
        sections = re.split(r'\n(?=### )', content)
        
        # 2. Keep important markers
        header = f"### Auto Flush ({datetime.now().strftime('%H:%M')})\n> Compressed to {target_tokens/current_tokens:.0%}\n\n"
        
        # 3. Truncate each section proportionally
        # Leave room for header (estimate ~50 tokens)
        adjusted_target = target_tokens - 50
        ratio = adjusted_target / current_tokens
        
        compressed_sections = []
        
        for section in sections:
            if not section.strip():
                continue
            # Keep section header intact
            lines = section.split('\n', 1)
            if len(lines) > 1:
                section_header = lines[0]
                section_body = lines[1]
                target_chars = int(len(section_body) * ratio)
                truncated_body = section_body[:max(target_chars, 100)]  # Keep at least 100 chars
                compressed_sections.append(f"{section_header}\n{truncated_body}\n[...]\n")
            else:
                compressed_sections.append(section)
        
        return header + "\n".join(compressed_sections)
    
    def _estimate_tokens(self, text: str) -> int:
        """
        Estimate token count.
        
        Rough approximation:
        - English: 1 token ≈ 4 characters
        - Chinese: 1 token ≈ 2 characters
        - Using weighted average based on character detection
        """
        if not text:
            return 0
            
        # Count Chinese characters
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        total_chars = len(text)
        other_chars = total_chars - chinese_chars
        
        # Weighted estimate
        tokens = (chinese_chars // 2) + (other_chars // 4)
        return max(1, tokens)
    
    def _append_to_file(self, file_path: Path, content: str) -> None:
        """Append content to file, creating if needed"""
        if not file_path.exists():
            file_path.write_text(content, encoding='utf-8')
        else:
            existing = file_path.read_text(encoding='utf-8')
            # Avoid duplicate content
            if content.strip() not in existing:
                with open(file_path, 'a', encoding='utf-8') as f:
                    f.write("\n\n" + content)
    
    # === Memory Loading Methods ===
    
    def load_memory(self) -> str:
        """Load MEMORY.md content (long-term curated memory)"""
        if self.memory_file.exists():
            return self.memory_file.read_text(encoding='utf-8')
        return ""
    
    def load_daily(self, date: Optional[datetime] = None) -> str:
        """Load daily memory file content"""
        daily_file = self.get_daily_file(date)
        if daily_file.exists():
            return daily_file.read_text(encoding='utf-8')
        return ""
    
    def load_recent(self, days: int = 2) -> str:
        """
        Load recent daily files.
        
        Default: today + yesterday (OpenClaw pattern)
        """
        contents = []
        for i in range(days):
            date = datetime.now() - timedelta(days=i)
            content = self.load_daily(date)
            if content:
                contents.append(f"## {date.strftime('%Y-%m-%d')}\n\n{content}")
        
        return "\n\n---\n\n".join(reversed(contents))
    
    def load_context(self, include_memory: bool = True, days: int = 2) -> str:
        """
        Load full context for LLM.
        
        Combines:
        - MEMORY.md (if include_memory=True)
        - Recent daily files
        """
        parts = []
        
        if include_memory:
            memory_content = self.load_memory()
            if memory_content:
                parts.append(f"# Long-term Memory\n\n{memory_content}")
        
        recent = self.load_recent(days)
        if recent:
            parts.append(f"# Recent Context\n\n{recent}")
        
        return "\n\n---\n\n".join(parts)
    
    # === Memory Writing Methods ===
    
    def write_memory(self, content: str, mode: str = "append") -> None:
        """
        Write to MEMORY.md.
        
        Args:
            content: Content to write
            mode: "append" or "replace"
        """
        if mode == "replace" or not self.memory_file.exists():
            self.memory_file.write_text(content, encoding='utf-8')
        else:
            with open(self.memory_file, 'a', encoding='utf-8') as f:
                f.write("\n\n" + content)
    
    def write_daily(self, content: str, date: Optional[datetime] = None, mode: str = "append") -> None:
        """
        Write to daily memory file.
        
        Args:
            content: Content to write
            date: Target date (default: today)
            mode: "append" or "replace"
        """
        daily_file = self.get_daily_file(date)
        
        if mode == "replace" or not daily_file.exists():
            daily_file.write_text(content, encoding='utf-8')
        else:
            with open(daily_file, 'a', encoding='utf-8') as f:
                f.write("\n\n" + content)
    
    # === Utility Methods ===
    
    def get_flush_history(self) -> list[FlushEvent]:
        """Get flush history"""
        return self._flush_history.copy()
    
    def get_stats(self) -> dict[str, Any]:
        """Get memory statistics"""
        memory_content = self.load_memory()
        recent_content = self.load_recent(2)
        
        return {
            "memory_file_exists": self.memory_file.exists(),
            "memory_tokens": self._estimate_tokens(memory_content),
            "recent_tokens": self._estimate_tokens(recent_content),
            "flush_count": len(self._flush_history),
            "config": self.config.to_dict(),
        }
    
    def list_daily_files(self) -> list[Path]:
        """List all daily memory files"""
        if not self.memory_dir.exists():
            return []
        return sorted(
            self.memory_dir.glob("*.md"),
            key=lambda p: p.stem,
            reverse=True
        )
