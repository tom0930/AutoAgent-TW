import subprocess
import logging
from typing import List

logger = logging.getLogger(__name__)

class DiffScanner:
    """
    Scans for changed files to enable incremental processing in CI.
    Filters out irrelevant files based on the project structure.
    """
    @classmethod
    def get_changed_files(cls, base_ref: str = "HEAD~1") -> List[str]:
        """
        Returns a list of files changed since the base_ref.
        """
        try:
            cmd = ["git", "diff", "--name-only", base_ref]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            files = result.stdout.strip().split("\n")
            return [f for f in files if f]
        except Exception as e:
            logger.error(f"[DiffScanner] Failed to get changed files: {e}")
            return []

    @classmethod
    def filter_relevant_files(cls, files: List[str]) -> List[str]:
        """
        Filters out non-source files (e.g., .md, .png, .json).
        """
        source_extensions = (".py", ".ts", ".js", ".html", ".css", ".cpp", ".h")
        return [f for f in files if f.endswith(source_extensions)]
