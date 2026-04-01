import jedi
import argparse
import json
import sys
import os
import io
from pathlib import Path

# Force UTF-8 for console output on Windows
if hasattr(sys.stdout, 'detach'):
    sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding='utf-8', errors='replace')

def probe_definition(file_path, line, column):
    """
    使用 Jedi 語言引擎定位符號定義點。
    """
    abs_path = str(Path(file_path).resolve())
    curr_dir = os.getcwd()
    
    try:
        # 建立 Jedi 專案以掃描目前目錄
        project = jedi.Project(curr_dir)
        script = jedi.Script(path=abs_path, project=project)
        
        # 進行定義跳轉
        definitions = script.goto(line=line, column=column)
        
        results = []
        for d in definitions:
            results.append({
                "name": d.full_name if d.full_name else d.name,
                "type": d.type,
                "path": str(d.module_path) if d.module_path else "Unknown",
                "line": d.line,
                "column": d.column,
                "docstring": d.docstring()[:100] + "..." if d.docstring() else ""
            })
        
        return results
    except Exception as e:
        return [{"error": str(e)}]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AutoAgent-TW Semantic LSP Probe (Pilot)")
    parser.add_argument("--file", type=str, required=True, help="Target file path")
    parser.add_argument("--line", type=int, required=True, help="Line number (1-indexed)")
    parser.add_argument("--col", type=int, required=True, help="Column number (0-indexed)")
    
    args = parser.parse_args()
    
    # 執行探測
    results = probe_definition(args.file, args.line, args.col)
    
    # 輸出 JSON 以便後續自動化解析
    print(json.dumps(results, indent=2, ensure_ascii=False))
