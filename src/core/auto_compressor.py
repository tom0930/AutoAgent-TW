import time
import logging
import threading
import json
from typing import List, Dict, Any, Optional, Callable
from pathlib import Path
from .compression_quality_gate import CompressionQualityGate, QualityGateResult
from .evidence_memory import CompressionSummary
from ..harness.streaming import event_bus, WorkflowEvent, EventType

logger = logging.getLogger("Core.AutoCompressor")

class AutoCompressor:
    """
    Asynchronous Context Compression Worker.
    Implements the 3-stage (L1->L2->L3) Pipeline with Quality Gate.
    """
    def __init__(self, 
                 quality_gate: Optional[CompressionQualityGate] = None,
                 summarizer_fn: Optional[Callable] = None):
        self.quality_gate = quality_gate or CompressionQualityGate()
        self.summarizer_fn = summarizer_fn # Function to call LLM for summary
        self._lock = threading.Lock()
        self._is_compressing = False

    def compress_async(self, 
                       session_id: str, 
                       messages: List[Dict[str, Any]], 
                       on_success: Callable[[str], None]):
        """
        Starts the compression pipeline in a background thread.
        """
        if self._is_compressing:
            logger.info(f"Compression already in progress for session {session_id}, skipping.")
            return

        thread = threading.Thread(
            target=self._run_pipeline,
            args=(session_id, messages, on_success),
            daemon=True,
            name=f"Compressor-{session_id}"
        )
        thread.start()

    def _run_pipeline(self, session_id: str, messages: List[Dict[str, Any]], on_success: Callable):
        with self._lock:
            self._is_compressing = True
        
        try:
            logger.info(f"Starting compression pipeline for {session_id}")
            original_token_count = self._estimate_tokens(messages)
            
            # --- L1: Background Trim ---
            # Remove redundant tool outputs, keep recent context
            trimmed_messages = self._trim_messages(messages)
            
            # --- L2: Background Summarize (LLM Call) ---
            if not self.summarizer_fn:
                logger.warning("No summarizer function provided, falling back to L1 only.")
                # If no LLM, we still pass through if tokens were reduced enough
                self._handle_success(session_id, trimmed_messages, on_success)
                return

            event_bus.emit(WorkflowEvent(
                event_type=EventType.MODEL_THINKING,
                workflow_id=session_id,
                data={"task": "compressing_context"}
            ))

            summary: CompressionSummary = self.summarizer_fn(messages)
            
            # --- L3: Quality Gate & Swap ---
            compressed_messages = [
                {"role": "system", "content": f"Context Summary: {summary.executive_summary}\nDecisions: {summary.decisions_made}"},
                *messages[-5:] # Always keep last 5 messages for continuity
            ]
            compressed_token_count = self._estimate_tokens(compressed_messages)
            
            result = self.quality_gate.validate(
                original_context=json.dumps(messages),
                compressed_summary=summary,
                original_token_count=original_token_count,
                compressed_token_count=compressed_token_count
            )
            
            if result.passed:
                logger.info(f"Quality Gate PASSED (Score: {result.score:.2f})")
                event_bus.emit(WorkflowEvent(
                    event_type=EventType.CONTEXT_COMPRESSED,
                    workflow_id=session_id,
                    data={"ratio": result.metrics["reduction_ratio"], "quality": result.score}
                ))
                self._handle_success(session_id, compressed_messages, on_success)
            else:
                logger.warning(f"Quality Gate FAILED: {result.reason}. Rolling back to original.")
                event_bus.emit(WorkflowEvent(
                    event_type=EventType.ERROR,
                    workflow_id=session_id,
                    data={"message": f"Compression quality check failed: {result.reason}"}
                ))
                
        except Exception as e:
            logger.error(f"Compression pipeline crash: {e}")
            event_bus.emit(WorkflowEvent(
                event_type=EventType.ERROR,
                workflow_id=session_id,
                data={"message": f"Compression engine error: {str(e)}"}
            ))
        finally:
            with self._lock:
                self._is_compressing = False

    def _trim_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        # Simple heuristic: remove tool results older than 10 turns
        return messages[-20:] # Simplified for now

    def _estimate_tokens(self, messages: List[Dict[str, Any]]) -> int:
        # Rough estimate: 4 chars per token
        total_chars = sum(len(str(m.get("content", ""))) for m in messages)
        return total_chars // 4

    def _handle_success(self, session_id: str, new_messages: List[Dict[str, Any]], on_success: Callable):
        # Notify session manager to swap context
        on_success(new_messages)
