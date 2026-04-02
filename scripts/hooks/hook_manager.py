import json
import os
import subprocess
from pathlib import Path
import threading

class HookManager:
    """
    攔截系統事件並根據配置觸發對應行為
    """
    _local = threading.local()

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.hooks_file = self.project_root / ".agents" / "hooks.json"
        self.hooks = self.load_config()
        
        # 內置預測引擎組件 (Legacy)
        from scripts.predictor.context_tracker import ContextTracker
        from scripts.predictor.command_predictor import CommandPredictor
        self.tracker = ContextTracker(str(project_root))
        self.predictor = CommandPredictor()
        self.predictions_file = self.project_root / ".agent-state" / "predictions.json"

    def load_config(self) -> dict:
        """載入 .agents/hooks.json 檔案"""
        if not self.hooks_file.exists():
            return {"hooks": {}}
        try:
            with open(self.hooks_file, "r", encoding="utf-8") as f:
                return json.load(f).get("hooks", {})
        except Exception as e:
            print(f"[HookManager] Error loading hooks.json: {e}")
            return {}

    def trigger(self, event_name: str, event_data: dict = None):
        """觸發指定的系統事件"""
        # 重入保護 (Re-entry Guard)
        if getattr(self._local, 'is_executing_hook', False):
            return
            
        print(f"[HookManager] Event: {event_name}")
        
        # 1. 處理內置邏輯 (Legacy Predictor)
        self._handle_legacy_logic(event_name, event_data)
        
        # 2. 處理配置中的客製化 Hooks
        self._execute_custom_hooks(event_name, event_data)

    def _execute_custom_hooks(self, event_name: str, event_data: dict):
        event_hooks = self.hooks.get(event_name, [])
        if not event_hooks:
            return

        self._local.is_executing_hook = True
        try:
            for hook in event_hooks:
                if not hook.get("enabled", True):
                    continue
                
                # TODO: 支援更複雜的 condition 評估器 (如 Python eval 或 DSL)
                # 目前僅做基本變數替換
                target_cmd = hook.get("target", "")
                if event_data:
                    for k, v in event_data.items():
                        target_cmd = target_cmd.replace(f"{{{k}}}", str(v))
                
                print(f"[HookManager] Executing Hook [{hook.get('id')}]: {target_cmd}")
                try:
                    subprocess.run(target_cmd, shell=True, check=False, cwd=str(self.project_root))
                except Exception as e:
                    print(f"[HookManager] Failed to execute hook {hook.get('id')}: {e}")
        finally:
            self._local.is_executing_hook = False

    def _handle_legacy_logic(self, event_name: str, event_data: dict):
        if event_name == "PostToolUse":
            if event_data and "file_path" in event_data:
                self.tracker.track_file_change(event_data["file_path"])
        elif event_name == "git.post-commit":
            self.tracker.track_git_event("post-commit", event_data or {})
            
        self.run_prediction_cycle()

    def run_prediction_cycle(self):
        """執行一次預測週期並儲存結果"""
        try:
            ctx = self.tracker.get_current_context()
            predictions = self.predictor.predict(ctx)
            with open(self.predictions_file, "w", encoding="utf-8") as f:
                json.dump(predictions, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[HookManager] Prediction failure: {e}")
