"""
AI Harness CLI 測試
"""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


class TestHarnessCLI:
    """CLI 測試"""

    def test_cli_help(self):
        """測試 --help"""
        from src.harness.cli.main import HarnessCLI

        cli = HarnessCLI(["--help"])
        # 不會拋出異常
        assert cli.parser is not None

    def test_cli_version(self):
        """測試 --version"""
        from src.harness.cli.main import HarnessCLI

        cli = HarnessCLI(["--version"])
        assert cli.parser is not None

    def test_gateway_status(self, tmp_path):
        """測試 status 命令"""
        from src.harness.cli.main import HarnessCLI

        cli = HarnessCLI(["status", "--workspace", str(tmp_path)])
        assert cli.parser is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
