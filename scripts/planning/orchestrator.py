# scripts/planning/orchestrator.py
from typing import List, Dict, Any, Tuple
import asyncio
from engine import ParallelPlanner
from schemas import AgentPlan, ConflictReport, DecisionMatrix

class ComplexityScorer:
    def __init__(self, threshold: int = 1000):
        self.threshold = threshold

    def score(self, context_length: int, files_changed: int) -> int:
        """Simple heuristic for task complexity."""
        return context_length + (files_changed * 500)

    def should_parallelize(self, context_length: int, files_changed: int) -> bool:
        return self.score(context_length, files_changed) > self.threshold


class MapReflectReduceOrchestrator:
    def __init__(self, context: Dict[str, Any], planner: ParallelPlanner):
        self.context = context
        self.planner = planner

    async def _extract_conflicts(self, plans: List[AgentPlan]) -> ConflictReport:
        """
        In reality, this would prompt the Synthesizer Agent.
        Mock implementation for the scope of the framework.
        """
        all_conflicts = []
        for plan in plans:
            all_conflicts.extend(plan.conflicts_with)
        
        has_conflict = len(all_conflicts) > 0
        return ConflictReport(
            has_conflict=has_conflict,
            conflict_dimensions=list(set(all_conflicts)),
            description="Identified conflicts across agent boundaries." if has_conflict else "No conflicts detected."
        )

    async def _cross_reflect(self, conflicts: ConflictReport, plans: List[AgentPlan]) -> List[AgentPlan]:
        """
        Simulate cross-reflection by sending specific prompt back to agents to reconsider.
        For now, we just return the plans as they are.
        """
        return plans

    async def synthesize(self, plans: List[AgentPlan], conflicts: ConflictReport) -> DecisionMatrix:
        """
        In reality, Synthesizer Agent writes the DecisionMatrix.
        """
        options = []
        if conflicts.has_conflict:
            options.append({
                "option_id": 1,
                "title": "Architect's Preference",
                "pros": ["High Scalability"],
                "cons": ["Complex setup"],
                "risk_level": "Medium"
            })
            options.append({
                "option_id": 2,
                "title": "Security's Preference",
                "pros": ["Highly secure"],
                "cons": ["Performance overhead"],
                "risk_level": "Low"
            })
        
        return DecisionMatrix(
            conflict_summary=conflicts.description,
            options=options
        )

    async def run(self, agents: List[Dict[str, Any]]) -> Tuple[List[AgentPlan], DecisionMatrix]:
        # 1. Map Phase
        valid_plans, failed = await self.planner.run(agents)
        
        # 2. Reflect Phase
        conflicts = await self._extract_conflicts(valid_plans)
        if conflicts.has_conflict:
            valid_plans = await self._cross_reflect(conflicts, valid_plans)

        # 3. Reduce Phase
        decision_matrix = await self.synthesize(valid_plans, conflicts)
        return valid_plans, decision_matrix
