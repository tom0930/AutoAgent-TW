import time
import logging
import math

logger = logging.getLogger("Orchestration.CircuitBreaker")

class CircuitBreaker:
    """
    Advanced Circuit Breaker with Exponential Backoff (Phase 171 v2.1).
    Prevents runaway API calls and runaway loops.
    """
    def __init__(self, max_failures: int = 3, initial_cooldown: int = 60):
        self.max_failures = max_failures
        self.initial_cooldown = initial_cooldown
        
        self.failure_count = 0
        self.last_failure_time = 0
        self.state = "CLOSED" # CLOSED, OPEN, HALF_OPEN
        self.total_failures = 0

    def record_success(self):
        """Resets failure count on success."""
        if self.state != "CLOSED":
            logger.info("Circuit Breaker: Resetting to CLOSED.")
        self.failure_count = 0
        self.state = "CLOSED"

    def record_failure(self):
        """Records a failure and calculates backoff."""
        self.failure_count += 1
        self.total_failures += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.max_failures:
            self.state = "OPEN"
            cooldown = self._get_backoff_time()
            logger.warning(f"Circuit Breaker: OPEN. Tripped after {self.failure_count} failures. Cooldown: {cooldown}s")

    def can_execute(self) -> bool:
        """Checks if execution is permitted."""
        if self.state == "CLOSED":
            return True
            
        elapsed = time.time() - self.last_failure_time
        cooldown = self._get_backoff_time()
        
        if self.state == "OPEN":
            if elapsed >= cooldown:
                self.state = "HALF_OPEN"
                logger.info("Circuit Breaker: Moving to HALF_OPEN (Testing recovery).")
                return True
            return False
            
        return True # HALF_OPEN allows one try

    def _get_backoff_time(self) -> int:
        """
        Calculates exponential backoff.
        Base: 60s, 120s, 240s...
        """
        multiplier = 2 ** (max(0, self.failure_count - self.max_failures))
        return min(3600, self.initial_cooldown * multiplier) # Max 1 hour
