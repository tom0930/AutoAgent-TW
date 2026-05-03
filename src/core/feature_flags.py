import os
import json
import logging
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger("Core.FeatureFlags")

# Default flags
DEFAULT_FLAGS = {
    "AA_CC_STATE_V2": False,
    "AA_ASYNC_COMPRESSION": False,
    "AA_EVIDENCE_MEMORY": False,
    "AA_INTERRUPTIBLE_STREAM": False,
}

class FeatureFlags:
    """
    Simple Feature Flag management system.
    Supports JSON config file with environment variable overrides.
    """
    _instance = None

    def __init__(self):
        self.flags = DEFAULT_FLAGS.copy()
        # Project-level state directory
        self.state_dir = Path(".agent-state")
        self.config_path = self.state_dir / "feature_flags.json"
        self._load_flags()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _load_flags(self):
        # 1. Load from file if exists
        if self.config_path.exists():
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    file_flags = json.load(f)
                    self.flags.update(file_flags)
            except Exception as e:
                logger.warning(f"Failed to load feature flags from {self.config_path}: {e}")

        # 2. Environment variable overrides (AA_FF_XXX)
        for key in self.flags:
            env_val = os.getenv(f"AA_FF_{key}")
            if env_val is not None:
                # Convert string to bool/int if possible
                if env_val.lower() in ("true", "1", "yes"):
                    self.flags[key] = True
                elif env_val.lower() in ("false", "0", "no"):
                    self.flags[key] = False
                else:
                    self.flags[key] = env_val

    def is_enabled(self, flag_name: str) -> bool:
        """Returns True if the flag is enabled."""
        return self.flags.get(flag_name, False)

    def get_value(self, flag_name: str, default: Any = None) -> Any:
        """Returns the value of the flag."""
        return self.flags.get(flag_name, default)

    def set_flag(self, flag_name: str, value: Any, persist: bool = True):
        """Sets a flag value and optionally persists it to JSON."""
        self.flags[flag_name] = value
        if persist:
            if not self.state_dir.exists():
                self.state_dir.mkdir(parents=True, exist_ok=True)
            try:
                with open(self.config_path, "w", encoding="utf-8") as f:
                    json.dump(self.flags, f, indent=4)
            except Exception as e:
                logger.error(f"Failed to persist feature flags: {e}")

# Global access
feature_flags = FeatureFlags.get_instance()
