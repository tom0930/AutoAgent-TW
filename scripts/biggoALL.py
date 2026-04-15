"""
biggoALL - Industrial Cross-Platform Comparison Engine (v2.5.1)
--------------------------------------------------------------
Optimized for Next.js App Router streaming data extraction.
"""
import asyncio
import json
import csv
import re
import os
import argparse
import urllib.request
import urllib.parse
import ssl
from datetime import datetime

# 禁用 SSL 驗證
ssl_context = ssl._create_unverified_context()

class CPAnalyzer:
    @staticmethod
    def extract_storage(name):
        # 優化後的正則表達式，支援 GB, G, TB, T (不分大小寫)
        match = re.search(r'(\d+)\s*(GB|G|TB|T)', name, re.I)
        if not match:
            # Fallback for patterns like 256g
            match = re.search(r'(\d+)(gb|g|tb|t)', name, re.I)
            if not match: return 0
        val = int(match.group(1))
        unit = match.group(2).upper()
        if 'T' in unit: return val * 1024
        return val

    @staticmethod
    def extract_inches(name):
        match = re.search(r'(\d+(\.\d+)?)\s*(吋|inch|")', name, re.I)
        return float(match.group(1)) if match else 0

    @staticmethod
    def calculate_cp(storage, price):
        if price <= 0: return 0
        return round(storage / (price / 10000), 2)

class StoreProvider:
    def __init__(self, headers):
        self.headers = headers

    async def search(self, query):
        raise NotImplementedError

class PChomeProvider(StoreProvider):
    async def search(self, query):
        print(f"📡 [PChome] 搜尋中: {query}")
        # 搜尋 API
        url = f"https://ecshweb.pchome.com.tw/search/v3.3/all/results?q={urllib.parse.quote(query)}&page=1&sort=rnk/dc"
        req = urllib.request.Request(url, headers=self.headers)
        try:
            with urllib.request.urlopen(req, context=ssl_context) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                prods = data.get("prods", []) or data.get("Nodes", []) or []
                results = []
                for p in prods:
                    pid = p.get("Id") or p.get("ID") or p.get("id")
                    name = p.get("name") or p.get("Name") or ""
                    price = p.get("price") or p.get("Price") or 0
                    if not pid or not name: continue
                    results.append({
                        "id": pid,
                        "name": name,
                        "price": price,
                        "link": f"https://24h.pchome.com.tw/prod/{pid}",
                        "source": "PChome",
                        "store": "PChome 24h"
                    })
                return results
        except Exception as e:
            print(f"❌ PChome 搜尋失敗: {e}")
            return []

class BigGoProvider(StoreProvider):
    async def search(self, query):
        print(f"📡 [BigGo] 搜尋中: {query}")
        encoded_query = urllib.parse.quote(query)
        url = f"https://biggo.com.tw/s/{encoded_query}/?sort=lp"
        req = urllib.request.Request(url, headers=self.headers)
        results = []
        try:
            with urllib.request.urlopen(req, context=ssl_context) as resp:
                html = resp.read().decode('utf-8')
            
            # 解析 Next.js stream 區塊 (self.__next_f.push)
            pushes = re.findall(r'self\.__next_f\.push\(\[1,"(.*?)"\]\)', html)
            for p in pushes:
                unescaped = p.replace('\\"', '"').replace('\\\\', '\\').replace('\\/', '/')
                if '"list":[' in unescaped:
                    # 匹配 list 陣列直到 promo 或結尾
                    match = re.search(r'"list":\s*(\[.*?\])(?=\s*,"promo")', unescaped)
                    if not match:
                        match = re.search(r'"list":\s*(\[.*\])', unescaped)
                    
                    if match:
                        try:
                            items_json = match.group(1)
                            decoder = json.JSONDecoder()
                            items, _ = decoder.raw_decode(items_json)
                            for item in items:
                                title = item.get("title") or item.get("name", "")
                                price = item.get("price", 0)
                                pid = item.get("id") or item.get("purl", "")
                                if not title: continue
                                results.append({
                                    "id": pid,
                                    "name": title,
                                    "price": price,
                                    "link": f"https://biggo.com.tw{item.get('purl', '')}",
                                    "source": "BigGo",
                                    "store": item.get("store", {}).get("name", "Unknown")
                                })
                            if results: break # 找到主列表後退出
                        except Exception:
                            # 備份修剪解析
                            try:
                                last_bracket = items_json.rfind(']')
                                items = json.loads(items_json[:last_bracket+1])
                                for item in items:
                                    results.append({
                                        "id": item.get("id"),
                                        "name": item.get("title") or item.get("name", ""),
                                        "price": item.get("price", 0),
                                        "link": f"https://biggo.com.tw{item.get('purl', '')}",
                                        "source": "BigGo",
                                        "store": item.get("store", {}).get("name", "Unknown")
                                    })
                            except Exception: pass
            return results
        except Exception as e:
            print(f"❌ BigGo 搜尋失敗: {e}")
            return []

async def main():
    parser = argparse.ArgumentParser(description="biggoALL - 跨平台電商比價及 CP 值分析工具 (v2.5.1)")
    # 支援 positional 或 --query
    parser.add_argument("query_pos", nargs='?', help="搜尋關鍵字 (Positional)")
    parser.add_argument("--query", help="搜尋關鍵字 (Optional)")
    parser.add_argument("--site", choices=["all", "biggo", "pchome"], default="all", help="指定站點")
    parser.add_argument("mode_cp", nargs='?', help="設為 'cp' 啟用 CP 分析模式")
    parser.add_argument("--cp", action="store_true", help="啟用 CP 分析模式")
    
    args = parser.parse_args()
    
    final_query = args.query or args.query_pos
    is_cp = args.cp or (args.mode_cp == 'cp') or (args.query_pos == 'cp' and args.query)
    
    if not final_query:
        print("❌ 請提供搜尋關鍵字。範例: python scripts/biggoALL.py \"iPhone 15\" cp")
        return
    
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"}
    providers = []
    if args.site in ["all", "pchome"]: providers.append(PChomeProvider(headers))
    if args.site in ["all", "biggo"]: providers.append(BigGoProvider(headers))

    tasks = [p.search(final_query) for p in providers]
    all_results_list = await asyncio.gather(*tasks)
    
    flat_results = []
    for sublist in all_results_list: flat_results.extend(sublist)

    analyzer = CPAnalyzer()
    processed = []
    seen = set()

    for p in flat_results:
        if p["id"] in seen: continue
        seen.add(p["id"])
        
        storage = analyzer.extract_storage(p["name"])
        cp = analyzer.calculate_cp(storage, p["price"])
        
        if is_cp and (storage == 0 or p["price"] < 5000): # 過濾配件
            continue
        
        p["storage"] = storage
        p["cp_value"] = cp
        processed.append(p)

    # 排序
    if is_cp:
        processed.sort(key=lambda x: x["cp_value"], reverse=True)
    else:
        processed.sort(key=lambda x: x["price"])

    # 輸出結果
    print("\n" + "="*120)
    if is_cp:
        print(f"🏆 CP 值排行搜尋結果: '{final_query}'")
        print("-" * 120)
        print(f"{'排名':<4} | {'來源':<8} | {'店鋪':<12} | {'CP值':<6} | {'價格':>8} | {'容量':>6} | {'商品名稱'}")
        for i, r in enumerate(processed[:20], 1):
            store_name = r.get("store", "N/A")[:10]
            print(f"{i:<4} | {r['source']:<8} | {store_name:<12} | {r['cp_value']:>6.2f} | {r['price']:>8,} | {r['storage']:>4}G | {r['name'][:60]}")
    else:
        print(f"🔍 最低價搜尋結果: '{final_query}'")
        print("-" * 120)
        print(f"{'排名':<4} | {'來源':<8} | {'價格':>8} | {'商品名稱'}")
        for i, r in enumerate(processed[:20], 1):
            print(f"{i:<4} | {r['source']:<8} | {r['price']:>8,} | {r['name'][:80]}")
    print("="*120)

    # 儲存
    output_dir = "artifacts/scraping_results"
    os.makedirs(output_dir, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M")
    csv_path = os.path.join(output_dir, f"biggoALL_final_{ts}.csv")
    
    with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=["id", "source", "store", "name", "price", "storage", "cp_value", "link"])
        writer.writeheader()
        writer.writerows(processed)
    
    print(f"\n✅ 完成！報表已存至: {csv_path}")

if __name__ == "__main__":
    asyncio.run(main())
