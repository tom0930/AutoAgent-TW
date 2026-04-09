import os
import json
import logging
import re
import subprocess
from datetime import datetime
from typing import Optional, List, Dict
from mcp.server.fastmcp import FastMCP

# 初始化 FastMCP
mcp = FastMCP("AutoAgent Persistent Memory Server")

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 自定義路徑 (應從環境變數讀取或預設)
PROJECT_ROOT = os.getcwd()

def get_context_dir() -> str:
    """自動偵測專案的 .context-[name] 目錄"""
    basename = os.path.basename(PROJECT_ROOT)
    context_dir = os.path.join(PROJECT_ROOT, f".context-{basename}")
    if not os.path.exists(context_dir):
        # 降級嘗試使用預設的 .context
        context_dir = os.path.join(PROJECT_ROOT, ".context")
    return context_dir

@mcp.tool()
async def query(keyword: str, scope: str = "archives") -> str:
    """
    持久化記憶檢索：搜尋專案歷史紀錄、決策歸檔與 SOP。
    :param keyword: 搜尋關鍵字
    :param scope: 搜尋範圍 (archives|core|all)
    """
    context_path = get_context_dir()
    if not os.path.exists(context_path):
        return f"❌ 找不到記憶體目錄: {context_path}，請先執行 /aa-history init"

    search_path = context_path
    if scope == "archives":
        search_path = os.path.join(context_path, "archives")
    elif scope == "core":
        search_path = os.path.join(context_path, "core.md")

    logger.info(f"🧠 正在記憶庫中檢索: {keyword} (範圍: {scope})")

    try:
        # 使用 ripgrep (rg) 進行全文檢索，若無則回退至 grep
        cmd = ["rg", "-a", "-i", "--context", "2", keyword, search_path]
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode != 0:
            # 嘗試一般的 grep
            cmd = ["grep", "-r", "-i", "-A", "2", keyword, search_path]
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')

        if not result.stdout.strip():
            return f"ℹ️ 記憶庫中查無與 '{keyword}' 相關的明確紀錄。"

        return f"--- 檢索結果 ---\n{result.stdout.strip()}"

    except Exception as e:
        logger.error(f"❌ 檢索出錯: {e}")
        return f"❌ 記憶庫存取失敗: {str(e)}"

@mcp.tool()
async def save(content: str, title: str, tags: str = "general", importance: int = 3) -> str:
    """
    手動持久化記憶：將當前的重要發現、決策或 SOP 存入長期記憶庫。
    :param content: 記憶內容 (Markdown)
    :param title: 標題
    :param tags: 標籤 (逗號分隔)
    :param importance: 重要性等級 (1-5)
    """
    context_path = get_context_dir()
    archives_dir = os.path.join(context_path, "archives")
    
    if not os.path.exists(archives_dir):
        os.makedirs(archives_dir, exist_ok=True)

    date_str = datetime.now().strftime("%Y-%m-%d")
    sanitized_title = re.sub(r'[^\w\s-]', '', title).strip().replace(" ", "-")
    filename = f"{date_str}_{sanitized_title}.md"
    file_path = os.path.join(archives_dir, filename)

    # 封裝 Markdown 格式
    formatted_content = f"""# {title}
- Date: {date_str}
- Tags: {tags}
- Importance: {importance}

{content}
"""

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(formatted_content)

        # 更新 Metadata 索引 (簡單追加或維持 index.md)
        index_path = os.path.join(context_path, "metadata.json")
        index_data = []
        if os.path.exists(index_path):
            with open(index_path, "r", encoding="utf-8") as f:
                try:
                    index_data = json.load(f)
                except: pass
        
        index_data.append({
            "title": title,
            "filename": filename,
            "tags": tags.split(","),
            "importance": importance,
            "timestamp": datetime.now().isoformat()
        })

        with open(index_path, "w", encoding="utf-8") as f:
            json.dump(index_data, f, indent=2, ensure_ascii=False)

        logger.info(f"✅ 記憶已持久化至: {filename}")
        return f"✅ 記憶已成功歸檔至 {filename} 並更新 Metadata 索引。"

    except Exception as e:
        logger.error(f"❌ 儲存失敗: {e}")
        return f"❌ 儲存記憶時發生錯誤: {str(e)}"

if __name__ == "__main__":
    mcp.run()
