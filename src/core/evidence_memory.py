import time
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class EvidenceFact(BaseModel):
    """
    A single fact extracted from the conversation with supporting evidence.
    Industrial grade memory structure.
    """
    fact: str
    evidence: List[str] = Field(description="List of msg_ids or turn indices supporting this fact")
    provenance: Dict[str, Any] = Field(default_factory=lambda: {"source": "llm_summarizer", "confidence": 1.0})
    timestamp: float = Field(default_factory=time.time)
    version: int = 1
    supersedes: List[str] = Field(default_factory=list, description="IDs of previously contradicted facts")

class CompressionSummary(BaseModel):
    """
    The structured output of a compression turn.
    """
    executive_summary: str
    key_facts: List[EvidenceFact]
    decisions_made: List[str]
    open_questions: List[str]
    token_reduction: Optional[float] = None
    quality_score: Optional[float] = None

class EvidenceMemory:
    """
    Manages structured evidence facts in MemPalace L3.
    """
    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = storage_path
        self.facts: Dict[str, EvidenceFact] = {}

    def add_fact(self, fact: EvidenceFact):
        # Conflict resolution logic: Latest + High Confidence wins
        fact_id = self._generate_id(fact.fact)
        if fact_id in self.facts:
            existing = self.facts[fact_id]
            if fact.timestamp > existing.timestamp:
                self.facts[fact_id] = fact
        else:
            self.facts[fact_id] = fact

    def _generate_id(self, text: str) -> str:
        # Simple normalization for deduplication
        return "".join(e for e in text.lower() if e.isalnum())[:32]

    def to_json(self) -> str:
        return json.dumps([f.dict() for f in self.facts.values()], indent=2)
