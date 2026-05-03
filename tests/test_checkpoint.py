import os
import json
import unittest
import shutil
import time
from pathlib import Path
from src.core.feature_flags import feature_flags
from src.core.workflow_checkpoint import CheckpointManager, WorkflowCheckpoint
from src.core.session_manager import SessionManager, SessionKind

class TestCheckpointV2(unittest.TestCase):
    def setUp(self):
        """Setup a temporary project environment."""
        self.test_dir = Path("tests/tmp_phase170")
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
        self.test_dir.mkdir(parents=True)
        
        # Mock .agent-state directory
        (self.test_dir / ".agent-state").mkdir()

    def tearDown(self):
        """Cleanup."""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_feature_flags(self):
        """Verify feature flag loading and override."""
        # Default is False (set in current session)
        self.assertFalse(feature_flags.is_enabled("AA_CC_STATE_V2"))
        
        # Set to True
        feature_flags.set_flag("AA_CC_STATE_V2", True, persist=False)
        self.assertTrue(feature_flags.is_enabled("AA_CC_STATE_V2"))
        
        # Restore
        feature_flags.set_flag("AA_CC_STATE_V2", False, persist=False)

    def test_checkpoint_v2_basic(self):
        """Verify Checkpoint V2 basic save/load."""
        manager = CheckpointManager(self.test_dir)
        
        cp = WorkflowCheckpoint(
            workflow_id="wf_test_001",
            step_id="1",
            action="initial_scan",
            status="completed",
            active_tools=["ls", "grep"],
            capability_mode="explore"
        )
        
        path = manager.save(cp)
        self.assertTrue(path.exists())
        
        # Load back
        loaded = manager.load("wf_test_001", "1")
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.workflow_id, "wf_test_001")
        self.assertEqual(loaded.active_tools, ["ls", "grep"])
        self.assertNotEqual(loaded.hmac, "")

    def test_checkpoint_integrity(self):
        """Verify HMAC integrity check."""
        manager = CheckpointManager(self.test_dir)
        cp = WorkflowCheckpoint(workflow_id="wf_bad", step_id="1", action="test", status="ok")
        path = manager.save(cp)
        
        # Tamper with the file
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        data["action"] = "malicious_action" # Modify data
        
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f)
            
        # Load should fail
        loaded = manager.load("wf_bad", "1")
        self.assertIsNone(loaded) # load() returns None on error/integrity fail

    def test_session_shadow_mode(self):
        """Verify SessionManager dual-writing in Shadow Mode."""
        # Enable Shadow Mode
        feature_flags.set_flag("AA_CC_STATE_V2", True, persist=False)
        
        manager = SessionManager(self.test_dir / "sessions")
        session = manager.create(kind=SessionKind.MAIN, label="ShadowTest")
        
        # Send a message (triggers _save_session -> _shadow_checkpoint_save)
        manager.send(session.key, "Hello Shadow", role="user")
        
        # Wait a bit for the daemon thread
        time.sleep(0.5)
        
        # Verify Checkpoint V2 exists
        cp_manager = CheckpointManager(self.test_dir)
        workflow_id = f"wf_{session.key.replace('session_', '')}"
        
        # step_id in Shadow Mode is str(session.message_count)
        # After send(), message_count should be 1
        cp = cp_manager.load(workflow_id, "1")
        self.assertIsNotNone(cp)
        self.assertEqual(cp.action, "session_update")
        
        # Cleanup
        feature_flags.set_flag("AA_CC_STATE_V2", False, persist=False)

if __name__ == '__main__':
    unittest.main()
