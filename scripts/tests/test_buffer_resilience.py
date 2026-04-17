import sys
import os
import time

# Ensure scripts root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# pyrefly: ignore [missing-import]
from utils.buffer_manager import BufferManager

def run_test():
    task_name = "resilience_demo"
    bm = BufferManager(task_name)
    
    # 1. 模擬任務清單 (10 個虛擬任務)
    mock_tasks = [{"id": f"task_{i}", "payload": f"Data for task {i}"} for i in range(1, 11)]
    
    # 2. 初始化 (若已存在則自動 Resume)
    bm.initialize(mock_tasks)
    
    # 3. 獲取下一批 (模擬分片)
    chunk = bm.get_next_chunk(chunk_size=3)
    
    if not chunk:
        print("== [COMPLETE] All tasks done! Cleaning up... ==")
        bm.cleanup()
        return

    print(f"[*] Starting chunk: {[t['task_id'] for t in chunk]}")
    
    for task in chunk:
        print(f"  正在處理 {task['task_id']}...")
        time.sleep(0.5) # 模擬耗時 I/O
        bm.mark_done(task['task_id'], result=f"Processed-{task['task_id']}")
        print(f"  [DONE] {task['task_id']}")

    print("\n--- Chunk processed ---")
    print("Run again to process next chunk or check resume.")

if __name__ == "__main__":
    run_test()
