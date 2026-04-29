# scripts/planning/engine.py
import asyncio
import json
import os
import time
from typing import List, Dict, Any, Tuple
from pydantic import ValidationError
from schemas import AgentPlan

CACHE_DIR = ".agent-state/parallel_planning_cache"

class APIError(Exception):
    pass

class RateLimitError(APIError):
    pass

class ParallelPlanner:
    def __init__(self, context: Dict[str, Any], resource_monitor: Any):
        self.context = context
        self.monitor = resource_monitor
        os.makedirs(CACHE_DIR, exist_ok=True)

    def _get_cache_path(self, agent_id: str) -> str:
        return os.path.join(CACHE_DIR, f"{agent_id}.json")

    def _read_cache(self, agent_id: str) -> Dict[str, Any]:
        cache_path = self._get_cache_path(agent_id)
        if os.path.exists(cache_path):
            with open(cache_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None

    def _write_cache(self, agent_id: str, data: Dict[str, Any]):
        cache_path = self._get_cache_path(agent_id)
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    async def _mock_api_call(self, agent_cfg: Dict[str, Any]) -> Dict[str, Any]:
        """Mock LLM API call for execution testing."""
        await asyncio.sleep(2) # Simulate network delay
        return {
            "role": agent_cfg.get("role", "Unknown"),
            "confidence": 0.9,
            "plan_section": f"Plan from {agent_cfg.get('role')}",
            "dependencies": [],
            "risks": ["Mocked risk"],
            "conflicts_with": []
        }

    async def _call_subagent(self, agent_cfg: Dict[str, Any], timeout: int = 60, max_retries: int = 3) -> AgentPlan:
        agent_id = agent_cfg.get("id", "default")
        
        # Check cache
        cached = self._read_cache(agent_id)
        if cached:
            try:
                return AgentPlan(**cached)
            except ValidationError:
                pass # Cache invalid, re-run

        # Exponential Backoff and Circuit Breaker
        delay = 1
        for attempt in range(max_retries):
            try:
                # In a real scenario, this would be `harness_gateway.dispatch(agent_cfg)`
                # with security filters applied via `filter_read_only_tools`.
                # Here we mock the API response.
                response_data = await asyncio.wait_for(self._mock_api_call(agent_cfg), timeout=timeout)
                
                # Schema validation
                plan = AgentPlan(**response_data)
                
                # Cache on success
                self._write_cache(agent_id, plan.model_dump())
                return plan
                
            except asyncio.TimeoutError:
                if attempt == max_retries - 1:
                    raise APIError(f"Agent {agent_id} timed out.")
            except RateLimitError:
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(delay)
                delay *= 2
            except ValidationError as e:
                # Retry on schema failure
                if attempt == max_retries - 1:
                    raise APIError(f"Agent {agent_id} failed schema validation: {str(e)}")
            except Exception as e:
                raise APIError(f"Agent {agent_id} encountered unexpected error: {str(e)}")

    async def run(self, agents: List[Dict[str, Any]], timeout: int = 60) -> Tuple[List[AgentPlan], List[str]]:
        tasks = [self._call_subagent(agent, timeout) for agent in agents]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        valid_plans = []
        failed = []
        
        for agent, res in zip(agents, results):
            if isinstance(res, Exception):
                failed.append(agent.get("id", "unknown"))
            else:
                valid_plans.append(res)
                
        return valid_plans, failed
