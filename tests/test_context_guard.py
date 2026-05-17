import os
import json
import pytest
from pathlib import Path
from src.core.context_guard import ContextGuard, CommandAnalysis

def test_token_estimation():
    guard = ContextGuard(context_limit=1000)
    
    # 1. 英文測試 (ASCII)：約 4 字元 = 1 token
    assert guard.estimate_tokens("Hello World") == len("Hello World") // 4
    
    # 2. 中文測試：1 中文字 ≈ 1.5 tokens
    chinese_text = "哈囉世界"
    assert guard.estimate_tokens(chinese_text) == int(len(chinese_text) * 1.5)
    
    # 3. 混合測試
    mixed = "Hello 哈囉"
    expected = int(6 * 0.25 + 2 * 1.5)
    assert guard.estimate_tokens(mixed) == expected

def test_guard_tracking_and_thresholds():
    guard = ContextGuard(context_limit=1000, warn_ratio=0.70, critical_ratio=0.85)
    
    # 追蹤常規工具
    guard.track("list_dir", 800) # 200 tokens
    assert guard.get_usage()["tokens"] == 200
    assert not guard.should_warn()
    assert not guard.should_force_stop()
    
    # 追蹤視覺工具 (乘數)
    guard.track("view_file", 20000) # 單次視覺文件最低 3000 tokens
    assert guard.get_usage()["tokens"] >= 3000
    assert guard.should_warn()
    assert guard.should_force_stop()
    
    # 重置
    guard.reset()
    assert guard.get_usage()["tokens"] == 0

def test_safe_shell_interceptor():
    guard = ContextGuard()
    
    # 1. 安全指令
    res = guard.analyze_command("python -m pytest tests/")
    assert res.safe
    assert res.risk_level == "safe"
    assert not res.requires_confirm
    
    # 2. blocked 指令 (格式化 / 刪根目錄)
    res = guard.analyze_command("rm -rf /")
    assert not res.safe
    assert res.risk_level == "blocked"
    assert "嘗試刪除根目錄" in res.suggestion
    
    # 3. dangerous / caution 指令
    res = guard.analyze_command("Remove-Item -Path C:\\Project\\*")
    assert not res.safe
    assert res.risk_level == "dangerous"
    assert res.requires_confirm
    
    # 4. PowerShell 連接字警告
    res = guard.analyze_command("cd src && pytest")
    assert not res.safe
    assert res.risk_level == "caution"
    assert "&&" in res.original_cmd

def test_signed_handoff_integrity(tmp_path):
    guard = ContextGuard(secret_key=b"test-secret-key-2026")
    
    state = {
        "task_id": "phase_179_test",
        "step": 4,
        "completed": ["discuss", "plan"],
        "variables": {"active_session": "sess_123"}
    }
    
    handoff_file = tmp_path / "handoff.json"
    
    # 1. 儲存與簽署
    saved_path = guard.save_handoff(state, handoff_file)
    assert saved_path.exists()
    
    # 2. 驗證與載入
    loaded_state = guard.load_handoff(saved_path)
    assert loaded_state == state
    
    # 3. 防篡改校驗：修改簽章
    with open(saved_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    data["signature"] = "tampered_signature_hash"
    with open(saved_path, "w", encoding="utf-8") as f:
        json.dump(data, f)
        
    # 載入應拒絕
    assert guard.load_handoff(saved_path) is None

def test_session_message_pruning(tmp_path):
    # 模擬修剪邏輯
    from src.core.session_manager import Session, SessionKind, SessionMessage
    import time
    
    session = Session(
        key="test_session_wipe",
        kind=SessionKind.MAIN,
        label="TestPrune",
        messages=[
            SessionMessage("1", "system", "You are an AI assistant", time.time()),
            SessionMessage("2", "user", "Hello", time.time()),
            SessionMessage("3", "assistant", "Hi there!", time.time()),
            SessionMessage("4", "user", "What is 2+2?", time.time()),
            SessionMessage("5", "assistant", "4", time.time()),
        ]
    )
    
    # 模擬 CLI 清理保留 2 條最新對話以及系統提示
    messages = session.messages
    system_msgs = [m for m in messages if m.role == "system"]
    other_msgs = [m for m in messages if m.role != "system"]
    
    keep_count = 2
    retained_others = other_msgs[-keep_count:]
    retained_messages = system_msgs + retained_others
    
    assert len(retained_messages) == 3
    assert retained_messages[0].content == "You are an AI assistant"
    assert retained_messages[1].content == "What is 2+2?"
    assert retained_messages[2].content == "4"
