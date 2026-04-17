import os
import sqlite3
# pyrefly: ignore [missing-import]
from langgraph.checkpoint.sqlite import SqliteSaver

def get_checkpointer(db_path: str = "checkpoints.sqlite"):
    """
    Initializes and returns a SqliteSaver checkpointer for LangGraph 
    persistence (Phase 120 - Task 1.2).
    """
    # Ensure directory exists
    os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
    
    # Initialize connection
    conn = sqlite3.connect(db_path, check_same_thread=False)
    # Recommended for SQLite checkpointing to avoid locking
    conn.execute("PRAGMA journal_mode=WAL")
    
    return SqliteSaver(conn)

if __name__ == "__main__":
    print("Verifying SqliteSaver Initialization...")
    try:
        checkpointer = get_checkpointer("temp/test_checkpoints.sqlite")
        print("Success: SqliteSaver initialized and WAL mode enabled.")
    except Exception as e:
        print(f"Failed: {str(e)}")
