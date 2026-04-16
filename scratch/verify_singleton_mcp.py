import asyncio
import os
import sys
import psutil
import logging
from pathlib import Path

# Add src to sys.path
sys.path.append(str(Path("z:/autoagent-TW").absolute()))

from src.core.mcp.mcp_client import MCPClientManager
from src.core.reaper import AgentReaper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("QA_Verification")

async def test_singleton_startup():
    """
    Test Case 1: Sequential Startup
    Verify that multiple calls to startup() do not create duplicate processes.
    """
    manager = MCPClientManager()
    
    logger.info("--- Wave 1: Initial Startup ---")
    await manager.startup()
    
    # Check processes
    procs_v1 = [p.info for p in psutil.process_iter(['pid', 'name', 'cmdline']) if "mcp" in " ".join(p.info['cmdline'] or "").lower()]
    logger.info(f"Processes after Wave 1: {len(procs_v1)}")
    for p in procs_v1:
        logger.info(f"  - PID {p['pid']}: {p['name']}")

    logger.info("--- Wave 2: Redundant Startup ---")
    await manager.startup()
    
    # Check processes again
    procs_v2 = [p.info for p in psutil.process_iter(['pid', 'name', 'cmdline']) if "mcp" in " ".join(p.info['cmdline'] or "").lower()]
    logger.info(f"Processes after Wave 2: {len(procs_v2)}")
    
    # Logic: Should be approximately the same count (ignoring transient shell procs)
    # The key is that we don't have TWO of the same server.
    
    # Group by fingerprint (cmdline)
    by_cmd = {}
    for p in procs_v2:
        cmd = " ".join(p['cmdline'] or "").lower()
        if cmd not in by_cmd:
            by_cmd[cmd] = []
        by_cmd[cmd].append(p['pid'])
    
    duplicates = {cmd: pids for cmd, pids in by_cmd.items() if len(pids) > 1}
    if duplicates:
        logger.error(f"FAIL: Duplicates detected! {duplicates}")
        return False
    else:
        logger.info("PASS: No duplicates detected across redundant startups.")
        return True

async def test_fingerprint_mismatch():
    """
    Test Case 2: Config Change (Fingerprint Mismatch)
    Verify that if the fingerprint changes, the GLOBAL reaper still cleans up the old one.
    """
    # This is harder to test without mocking the config file.
    # But we can verify that _get_server_fingerprint is sensitive to args.
    manager = MCPClientManager()
    cfg1 = {"command": "python", "args": ["script.py", "--opt1"]}
    cfg2 = {"command": "python", "args": ["script.py", "--opt2"]}
    
    f1 = manager._get_server_fingerprint(cfg1)
    f2 = manager._get_server_fingerprint(cfg2)
    
    if f1 != f2:
        logger.info(f"PASS: Fingerprints differ with different args: {f1} vs {f2}")
        return True
    else:
        logger.error("FAIL: Fingerprints identical for different configs!")
        return False

async def main():
    success = True
    success &= await test_singleton_startup()
    success &= await test_fingerprint_mismatch()
    
    if success:
        logger.info("=== ALL QA TESTS PASSED ===")
        sys.exit(0)
    else:
        logger.error("=== QA TESTS FAILED ===")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
