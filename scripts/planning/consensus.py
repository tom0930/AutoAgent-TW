import json
import yaml
import asyncio
from pathlib import Path
from typing import List, Literal, Dict, Any, Optional
from datetime import datetime

from .schemas import AgentVote, ConsensusResult, ConflictReport

class ConflictClassifier:
    """Classifies conflicts into CRITICAL, MAJOR, or MINOR based on heuristics."""
    
    CRITICAL_KEYWORDS = ["security", "stride", "vulnerability", "auth", "veto", "leak", "injection"]
    MAJOR_KEYWORDS = ["architecture", "database", "api", "performance", "scalability", "dependency"]
    
    @classmethod
    def classify(cls, conflict: ConflictReport) -> Literal["CRITICAL", "MAJOR", "MINOR"]:
        dimensions_str = " ".join(conflict.conflict_dimensions).lower()
        desc_str = conflict.description.lower()
        full_text = dimensions_str + " " + desc_str
        
        for kw in cls.CRITICAL_KEYWORDS:
            if kw in full_text:
                return "CRITICAL"
                
        for kw in cls.MAJOR_KEYWORDS:
            if kw in full_text:
                return "MAJOR"
                
        return "MINOR"

class ConsensusEngine:
    def __init__(self, resource_monitor: Any = None):
        self.config_path = Path(__file__).parent / "config" / "role_weights.yaml"
        self.state_dir = Path(__file__).parent.parent.parent / ".agent-state"
        self.state_dir.mkdir(parents=True, exist_ok=True)
        
        self.config = self._load_config()
        self.monitor = resource_monitor
        self.max_rounds = self.config.get("thresholds", {}).get("max_negotiation_rounds", 2)
        self.threshold = self.config.get("thresholds", {}).get("consensus_score", 0.75)
        
    def _load_config(self) -> Dict[str, Any]:
        if self.config_path.exists():
            with open(self.config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        return {"roles": {}, "thresholds": {"consensus_score": 0.75, "max_negotiation_rounds": 2}}
        
    def _get_role_weight(self, role: str) -> float:
        roles = self.config.get("roles", {})
        if role in roles:
            return roles[role].get("base_weight", 1.0)
        return roles.get("General", {}).get("base_weight", 1.0)

    def _calculate_score(self, votes: List[AgentVote]) -> float:
        if not votes:
            return 0.0
            
        total_weighted_confidence = 0.0
        total_weight = 0.0
        
        for vote in votes:
            weight = self._get_role_weight(vote.agent_role) * vote.domain_relevance
            total_weighted_confidence += vote.confidence * weight
            total_weight += weight
            
        if total_weight == 0:
            return 0.0
            
        return total_weighted_confidence / total_weight
        
    def _write_audit_log(self, round_data: Dict[str, Any]) -> str:
        audit_file = self.state_dir / "consensus_audit.json"
        
        # Append-only list of JSON lines or a single JSON array
        # We will use JSON lines for easy appending
        round_data["timestamp"] = datetime.utcnow().isoformat()
        
        with open(audit_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(round_data) + "\n")
            
        return str(audit_file)

    async def _negotiate_round(self, votes: List[AgentVote], round_idx: int) -> List[AgentVote]:
        # In a real scenario, this would call LLM agents to rethink.
        # For phase 168 baseline, we simulate the negotiation by having them converge
        # towards the highest weighted decision.
        
        if not votes:
            return []
            
        # Find the dominant vote
        dominant_vote = max(
            votes, 
            key=lambda v: v.confidence * self._get_role_weight(v.agent_role) * v.domain_relevance
        )
        
        new_votes = []
        for vote in votes:
            if vote.decision != dominant_vote.decision:
                # Compromise: lower confidence slightly or switch decision
                new_confidence = min(1.0, vote.confidence + 0.1)
                new_vote = AgentVote(
                    agent_role=vote.agent_role,
                    confidence=new_confidence,
                    decision=dominant_vote.decision, # They agree to the dominant one after discussion
                    reasoning=f"Compromised to {dominant_vote.decision} in round {round_idx}",
                    domain_relevance=vote.domain_relevance
                )
                new_votes.append(new_vote)
            else:
                new_votes.append(vote)
                
        return new_votes

    def _budget_fallback(self, votes: List[AgentVote]) -> ConsensusResult:
        score = self._calculate_score(votes)
        best_vote = max(votes, key=lambda v: v.confidence * self._get_role_weight(v.agent_role)) if votes else None
        decision = best_vote.decision if best_vote else "UNKNOWN"
        
        audit_path = self._write_audit_log({
            "status": "FALLBACK_BUDGET",
            "score": score,
            "final_decision": decision,
            "votes": [v.model_dump() for v in votes]
        })
        
        return ConsensusResult(
            status="FALLBACK",
            score=score,
            adopted_decision=decision,
            audit_path=audit_path,
            notes=["[BUDGET_FALLBACK] Token budget low, forced resolution."]
        )

    def _timeout_fallback(self, votes: List[AgentVote]) -> ConsensusResult:
        score = self._calculate_score(votes)
        audit_path = self._write_audit_log({
            "status": "PENDING_REVIEW",
            "score": score,
            "votes": [v.model_dump() for v in votes]
        })
        
        return ConsensusResult(
            status="PENDING_REVIEW",
            score=score,
            adopted_decision="REQUIRES_HUMAN",
            audit_path=audit_path,
            notes=["[TIMEOUT_FALLBACK] Max rounds exceeded. Pending human review."]
        )

    async def resolve(self, votes: List[AgentVote], conflict: ConflictReport) -> ConsensusResult:
        conflict_type = ConflictClassifier.classify(conflict)
        
        if conflict_type == "CRITICAL":
            # Check if Security vetoes
            security_votes = [v for v in votes if v.agent_role.lower() == "security"]
            if security_votes:
                audit_path = self._write_audit_log({
                    "status": "VETO",
                    "conflict_type": conflict_type,
                    "votes": [v.model_dump() for v in votes]
                })
                return ConsensusResult(
                    status="VETO",
                    score=0.0,
                    adopted_decision="REJECTED_BY_SECURITY",
                    audit_path=audit_path,
                    notes=["[SECURITY_VETO] Critical conflict blocked by Security."]
                )
        
        if conflict_type == "MINOR":
            # Weighted vote, just return best
            score = self._calculate_score(votes)
            best_vote = max(votes, key=lambda v: v.confidence * self._get_role_weight(v.agent_role) * v.domain_relevance)
            audit_path = self._write_audit_log({
                "status": "CONSENSUS_MINOR",
                "score": score,
                "final_decision": best_vote.decision,
                "votes": [v.model_dump() for v in votes]
            })
            return ConsensusResult(
                status="CONSENSUS",
                score=score,
                adopted_decision=best_vote.decision,
                audit_path=audit_path,
                notes=["Resolved via MINOR weighted vote."]
            )
            
        # MAJOR - Negotiation Loop
        current_votes = votes
        for round_idx in range(self.max_rounds):
            if self.monitor and hasattr(self.monitor, 'can_spend_tokens'):
                if not self.monitor.can_spend_tokens(est_tokens=2000):
                    return self._budget_fallback(current_votes)
                    
            current_votes = await self._negotiate_round(current_votes, round_idx)
            score = self._calculate_score(current_votes)
            
            if score >= self.threshold:
                audit_path = self._write_audit_log({
                    "status": "CONSENSUS_MAJOR",
                    "score": score,
                    "round_reached": round_idx + 1,
                    "final_decision": current_votes[0].decision if current_votes else "UNKNOWN",
                    "votes": [v.model_dump() for v in current_votes]
                })
                return ConsensusResult(
                    status="CONSENSUS",
                    score=score,
                    adopted_decision=current_votes[0].decision if current_votes else "UNKNOWN",
                    audit_path=audit_path,
                    notes=[f"Resolved via MAJOR negotiation at round {round_idx + 1}."]
                )
                
        return self._timeout_fallback(current_votes)
