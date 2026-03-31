import asyncio
from error_classifier import ErrorClassifier, ErrorSeverity, ErrorCategory
from retry_engine import with_retry

# --- Mock Network Call that fails ---
call_count = 0

@with_retry(max_retries=3, base_delay=0.1, step_id="test_api_call")
async def unstable_api():
    global call_count
    call_count += 1
    if call_count < 3:
        raise ConnectionError("Connection reset by peer")
    return "SUCCESS"

async def test_error_classifier():
    print("[TEST 1] Error Classifier parsing...")
    e = Exception("HTTP 429 Too Many Requests: Rate limit exceeded")
    agent_error = ErrorClassifier.classify(e)
    assert agent_error.category == ErrorCategory.RATE_LIMIT
    assert agent_error.severity == ErrorSeverity.TRANSIENT
    
    e = Exception("Max context length exceeded 128000 tokens")
    agent_error = ErrorClassifier.classify(e)
    assert agent_error.category == ErrorCategory.CONTEXT_OVERFLOW
    assert agent_error.severity == ErrorSeverity.RECOVERABLE
    print("[OK] Error Classifier is accurate.")

async def test_retry_engine():
    print("[TEST 2] Retry Engine (Exponential backoff)...")
    result = await unstable_api()
    assert result == "SUCCESS"
    assert call_count == 3
    print("[OK] Retry Engine survived 2 connection errors and succeeded on the 3rd.")

if __name__ == "__main__":
    asyncio.run(test_error_classifier())
    asyncio.run(test_retry_engine())
    print("\n[SUCCESS] All Resilience Core Tests Passed!")
