import time
import unittest
from unittest.mock import MagicMock
from src.core.auto_compressor import AutoCompressor
from src.core.compression_quality_gate import CompressionQualityGate, QualityGateResult
from src.core.evidence_memory import CompressionSummary, EvidenceFact

class TestCompressionQuality(unittest.TestCase):
    def test_quality_gate_token_ratio(self):
        """Verify quality gate fails if token reduction is insufficient."""
        gate = CompressionQualityGate(min_token_reduction=0.5)
        
        summary = CompressionSummary(
            executive_summary="Short", key_facts=[], decisions_made=[], open_questions=[]
        )
        
        # Original 100, Compressed 80 (Reduction 0.2 < 0.5)
        result = gate.validate("original", summary, 100, 80)
        self.assertFalse(result.passed)
        self.assertIn("Insufficient token reduction", result.reason)

    def test_quality_gate_success(self):
        """Verify quality gate passes when all metrics are met."""
        gate = CompressionQualityGate(min_token_reduction=0.5, min_fact_recall=0.7)
        
        summary = CompressionSummary(
            executive_summary="Compressed summary", 
            key_facts=[EvidenceFact(fact="fact1", evidence=["1"])], 
            decisions_made=[], open_questions=[]
        )
        
        # Mock recall and similarity to pass
        gate._calculate_recall = MagicMock(return_value=0.9)
        gate._calculate_similarity = MagicMock(return_value=0.9)
        
        # Original 1000, Compressed 300 (Reduction 0.7 > 0.5)
        result = gate.validate("original context", summary, 1000, 300)
        self.assertTrue(result.passed)

    def test_auto_compressor_pipeline(self):
        """Verify the full pipeline flow with mock summarizer."""
        success_called = False
        def on_success(new_msgs):
            nonlocal success_called
            success_called = True

        def mock_summarizer(messages):
            return CompressionSummary(
                executive_summary="Summary", 
                key_facts=[], decisions_made=[], open_questions=[]
            )

        # Force gate to pass
        gate = CompressionQualityGate()
        gate.validate = MagicMock(return_value=QualityGateResult(True, 1.0, "Pass", {"reduction_ratio": 0.8}))
        
        compressor = AutoCompressor(quality_gate=gate, summarizer_fn=mock_summarizer)
        
        messages = [{"role": "user", "content": "hello " * 1000}] # Large content
        compressor.compress_async("session1", messages, on_success)
        
        # Wait for async thread
        time.sleep(1)
        self.assertTrue(success_called)

if __name__ == '__main__':
    unittest.main()
