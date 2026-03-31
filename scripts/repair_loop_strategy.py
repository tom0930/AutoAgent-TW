import json
from pathlib import Path
from datetime import datetime

class RepairStrategy:
    def __init__(self, max_rounds=6, min_rounds=3):
        self.max_rounds = max_rounds
        self.min_rounds = min_rounds

    def calculate_diversity(self, history):
        # Calculate how many different sets of files were modified
        if len(history) < 2:
            return 1.0 # Default High
        
        modified_sets = [set(h.get("modified_files", [])) for h in history]
        unique_sets = []
        for s in modified_sets:
            if s not in unique_sets:
                unique_sets.append(s)
        
        return len(unique_sets) / len(history)

    def calculate_trend(self, history):
        # Calculate trend of error/failure counts
        # Positive (>0) means counts are decreasing (GOOD)
        # Negative (<0) means counts are increasing (BAD)
        if len(history) < 2:
            return 0
        
        counts = [h.get("failure_count", 0) for h in history]
        # Compare last two
        return counts[-2] - counts[-1]

    def is_repeating(self, history):
        if len(history) < 2:
            return False
        
        # Check if same files were changed in the last two attempts
        last = history[-1].get("modified_files", [])
        second_last = history[-2].get("modified_files", [])
        return set(last) == set(second_last) and len(last) > 0

    def should_continue(self, history_data):
        history = history_data.get("history", [])
        rounds = len(history)
        
        if rounds == 0:
            return True, "Initial round. Starting repair..."
            
        if rounds >= self.max_rounds:
            return False, f"Reached absolute maximum rounds ({self.max_rounds})."

        # Rule 1: Always allow up to min_rounds unless repeating
        if rounds < self.min_rounds:
            if self.is_repeating(history):
                return False, "Detected repeating repair strategy (same files modified)."
            return True, "Under minimum rounds, continuing..."

        # Rule 2: If we are improving, continue
        trend = self.calculate_trend(history)
        if trend > 0:
            return True, f"Positive trend detected (improved by {trend} tests). Continuing..."

        # Rule 3: If diversity is good, maybe try one more strategy
        diversity = self.calculate_diversity(history)
        if diversity > 0.7 and rounds < (self.max_rounds - 1):
            return True, f"High strategy diversity ({diversity:.2f}). Giving one more attempt."

        return False, "No significant improvement and low strategy diversity."

if __name__ == "__main__":
    # Test script with dummy history
    test_history = {
        "history": [
            {"id": 1, "failure_count": 10, "modified_files": ["a.py"]},
            {"id": 2, "failure_count": 8, "modified_files": ["b.py"]},
            {"id": 3, "failure_count": 8, "modified_files": ["c.py"]}
        ]
    }
    strategy = RepairStrategy()
    cont, reason = strategy.should_continue(test_history)
    print(f"Should Continue: {cont} :: Reason: {reason}")
