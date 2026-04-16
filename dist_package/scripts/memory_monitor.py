import os
import sys
import json
import logging
import tiktoken
from pathlib import Path

# Windows 終端機 Emoji/UTF-8 輸出修正
if sys.platform == "win32":
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

# 設定日誌
logging.basicConfig(level=logging.INFO, format='[Memory-Monitor] %(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Tokenizer 配置
TOKENIZER = tiktoken.get_encoding("cl100k_base")

def get_context_dir() -> str:
    """自動偵測專案的 .context-[name] 目錄"""
    project_root = os.getcwd()
    basename = os.path.basename(project_root)
    context_dir = os.path.join(project_root, f".context-{basename}")
    if not os.path.exists(context_dir):
        context_dir = os.path.join(project_root, ".context")
    return context_dir

def get_memory_stats():
    """獲取各層記憶體的統計數據"""
    context_dir = get_context_dir()
    stats = {
        "context_dir": context_dir,
        "exists": os.path.exists(context_dir),
        "l1_current": {"tokens": 0, "size_kb": 0},
        "l2_archives": {"count": 0, "size_mb": 0},
        "l3_knowledge": {"count": 0, "size_mb": 0},
        "metadata_count": 0
    }

    if not stats["exists"]:
        return stats

    # L1: current.md
    current_md = os.path.join(context_dir, "current.md")
    if os.path.exists(current_md):
        with open(current_md, "r", encoding="utf-8") as f:
            content = f.read()
            stats["l1_current"]["tokens"] = len(TOKENIZER.encode(content))
            stats["l1_current"]["size_kb"] = round(os.path.getsize(current_md) / 1024, 2)

    # L2: archives/
    archives_dir = os.path.join(context_dir, "archives")
    if os.path.exists(archives_dir):
        files = [f for f in os.listdir(archives_dir) if f.endswith(".md")]
        stats["l2_archives"]["count"] = len(files)
        total_size = sum(os.path.getsize(os.path.join(archives_dir, f)) for f in files)
        stats["l2_archives"]["size_mb"] = round(total_size / (1024 * 1024), 2)

    # Metadata
    metadata_json = os.path.join(context_dir, "metadata.json")
    if os.path.exists(metadata_json):
        try:
            with open(metadata_json, "r", encoding="utf-8") as f:
                data = json.load(f)
                stats["metadata_count"] = len(data)
        except: pass

    # L3: knowledge
    knowledge_dir = os.path.join(os.getcwd(), "knowledge")
    if os.path.exists(knowledge_dir):
        files = [f for f in os.listdir(knowledge_dir) if f.endswith(".md")]
        stats["l3_knowledge"]["count"] = len(files)
        total_size = sum(os.path.getsize(os.path.join(knowledge_dir, f)) for f in files)
        stats["l3_knowledge"]["size_mb"] = round(total_size / (1024 * 1024), 2)

    return stats

def print_stats():
    stats = get_memory_stats()
    print("=" * 50)
    print(" [Memory] AutoAgent-TW Persistent Memory Status")
    print("=" * 50)
    
    if not stats["exists"]:
        print(f"❌ 找不到專案記憶體目錄: {stats['context_dir']}")
        print("💡 請執行 /aa-history init 初始化。")
        return

    print(f"📍 Directory: {stats['context_dir']}")
    print("-" * 50)
    
    # L1 Status
    l1 = stats["l1_current"]
    token_color = ""
    if l1["tokens"] > 10000: token_color = "[DANGER]"
    elif l1["tokens"] > 8000: token_color = "[WARN]"
    else: token_color = "[OK]"
    
    print(f"L1 (Working): {l1['tokens']:,} tokens {token_color}")
    print(f"             ({l1['size_kb']} KB)")
    
    # L2 Status
    l2 = stats["l2_archives"]
    print(f"L2 (Project): {l2['count']} archives recorded")
    print(f"             ({l2['size_mb']} MB)")
    print(f"             Metadata indexed: {stats['metadata_count']} items")
    
    # L3 Status
    l3 = stats["l3_knowledge"]
    print(f"L3 (Global):  {l3['count']} Knowledge Items (KIs)")
    print(f"             ({l3['size_mb']} MB)")
    
    print("-" * 50)
    if l1["tokens"] > 8000:
        print("👉 建議執行 /aa-history update 以觸發智慧壓縮。")
    print("=" * 50)

if __name__ == "__main__":
    print_stats()
