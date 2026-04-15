import asyncio
import json
import csv
import re
import os
import argparse
import urllib.request
import ssl
from datetime import datetime

# 禁用 SSL 驗證
ssl_context = ssl._create_unverified_context()

class CPAnalyzer:
    @staticmethod
    def extract_storage(name):
        # 優化後的正則表達式，支援 GB, G, TB, T (不分大小寫)
        match = re.search(r'(\d+)\s*(GB|G|TB|T)', name, re.I)
        if not match: return 0
        val = int(match.group(1))
        unit = match.group(2).upper()
        if 'T' in unit: return val * 1024
        return val

    @staticmethod
    def extract_inches(name):
        # 提取螢幕尺寸 (研究筆記推薦)
        match = re.search(r'(\d+(\.\d+)?)\s*(吋|inch|")', name, re.I)
        return float(match.group(1)) if match else 0

    @staticmethod
    def extract_generation(name):
        # 提取系列/代數
        match = re.search(r'(iPhone|S)\s*(\d+)', name, re.I)
        return match.group(2) if match else "N/A"

    @staticmethod
    def calculate_cp(storage, price):
        if price <= 0: return 0
        # CP值公式: (儲存空間) / (價格/1萬)
        return round(storage / (price / 10000), 2)

class StoreProvider:
    def __init__(self, headers):
        self.headers = headers

    async def search(self, query):
        raise NotImplementedError

class PChomeProvider(StoreProvider):
    async def search(self, query):
        print(f"📡 [PChome] 搜尋中: {query}")
        # 整合自 pchome_iphone_cp.py 的搜尋策略
        url = f"https://ecshweb.pchome.com.tw/search/v3.3/all/results?q={urllib.parse.quote(query)}&page=1&sort=rnk/dc"
        req = urllib.request.Request(url, headers=self.headers)
        try:
            with urllib.request.urlopen(req, context=ssl_context) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                prods = data.get("prods", [])
                results = []
                for p in prods:
                    pid = p.get("Id") or p.get("ID")
                    name = p.get("name") or p.get("Name")
                    price = p.get("price") or p.get("Price")
                    if not pid or not name: continue
                    results.append({
                        "id": pid,
                        "name": name,
                        "price": price,
                        "link": f"https://24h.pchome.com.tw/prod/{pid}",
                        "source": "PChome"
                    })
                return results
        except Exception as e:
            print(f"❌ PChome 搜尋失敗: {e}")
            return []

class BigGoProvider(StoreProvider):
    async def search(self, query):
        print(f"📡 [BigGo] 搜尋中: {query}")
        url = f"https://biggo.com.tw/s/{urllib.parse.quote(query)}/?sort=lp"
        req = urllib.request.Request(url, headers=self.headers)
        try:
            with urllib.request.urlopen(req, context=ssl_context) as resp:
                html = resp.read().decode('utf-8')
                
                # 嘗試尋找 __NEXT_DATA__ JSON 區塊
                json_match = re.search(r'<script id="__NEXT_DATA__" type="application/json">({.*?})</script>', html)
                results = []
                
                if json_match:
                    try:
                        data = json.loads(json_match.group(1))
                        # 遞迴尋找所有商品物件 (簡化版)
                        # BigGo 的結構通常在 props.pageProps.initialState.search.results
                        items = data.get("props", {}).get("pageProps", {}).get("initialState", {}).get("search", {}).get("results", [])
                        for item in items:
                            results.append({
                                "id": item.get("id"),
                                "name": item.get("name"),
                                "price": int(item.get("price", 0)),
                                "link": f"https://biggo.com.tw/s/?q={item.get('id')}",
                                "source": "BigGo"
                            })
                    except Exception as je:
                        print(f"⚠️ BigGo JSON 解析警告: {je}")

                # Fallback: 使用更強壯的正則提取 (針對 Streaming HTML)
                if not results:
                    names = re.findall(r'\"name\":\"([^\"]*?)\"', html)
                    prices = re.findall(r'\"price\":(\d+)', html)
                    ids = re.findall(r'\"id\":\"([^\"]*?)\"', html)
                    limit = min(len(names), len(prices), len(ids), 30)
                    for i in range(limit):
                        if query.lower().split()[0] in names[i].lower(): # 基礎過濾
                            results.append({
                                "id": ids[i],
                                "name": names[i],
                                "price": int(prices[i]),
                                "link": f"https://biggo.com.tw/s/?q={ids[i]}",
                                "source": "BigGo"
                            })
                return results
        except Exception as e:
            print(f"❌ BigGo 搜尋失敗: {e}")
            return []

async def main():
    parser = argparse.ArgumentParser(description="biggoALL - 跨平台電商比價及 CP 值分析工具")
    parser.add_argument("query", help="搜尋關鍵字")
    parser.add_argument("--site", choices=["all", "biggo", "pchome"], default="all", help="指定搜尋站點 (預設 all)")
    parser.add_argument("--cp", action="store_true", help="啟用 CP 值分析模式 (儲存空間/價格)")
    
    args = parser.parse_args()
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Referer": "https://24h.pchome.com.tw/"
    }

    providers = []
    if args.site in ["all", "pchome"]: providers.append(PChomeProvider(headers))
    if args.site in ["all", "biggo"]: providers.append(BigGoProvider(headers))

    tasks = [p.search(args.query) for p in providers]
    all_results_list = await asyncio.gather(*tasks)
    
    flat_results = []
    for sublist in all_results_list:
        flat_results.extend(sublist)

    # 分析與計算
    analyzer = CPAnalyzer()
    processed = []
    seen = set()

    for p in flat_results:
        if p["id"] in seen: continue
        seen.add(p["id"])
        
        storage = analyzer.extract_storage(p["name"])
        cp = analyzer.calculate_cp(storage, p["price"])
        
        # 只有在 CP 模式下才需要有 storage
        if args.cp and storage == 0: continue
        
        p["storage"] = storage
        p["cp_value"] = cp
        processed.append(p)

    # 排序
    if args.cp:
        processed.sort(key=lambda x: x["cp_value"], reverse=True)
    else:
        processed.sort(key=lambda x: x["price"])

    # 輸出結果
    print("\n" + "="*110)
    if args.cp:
        print(f"🏆 CP 值排行搜尋結果: '{args.query}'")
        print("-" * 110)
        print(f"{'排名':<4} | {'來源':<8} | {'CP值':<6} | {'價格':>8} | {'容量':>6} | {'商品名稱'}")
        for i, r in enumerate(processed[:15], 1):
            print(f"{i:<4} | {r['source']:<8} | {r['cp_value']:>6.2f} | {r['price']:>8,} | {r['storage']:>4}G | {r['name'][:60]}")
    else:
        print(f"🔍 最低價搜尋結果: '{args.query}'")
        print("-" * 110)
        print(f"{'排名':<4} | {'來源':<8} | {'價格':>8} | {'商品名稱'}")
        for i, r in enumerate(processed[:15], 1):
            print(f"{i:<4} | {r['source']:<8} | {r['price']:>8,} | {r['name'][:75]}")
    print("="*110)

    # 儲存報表
    output_dir = "artifacts/scraping_results"
    if not os.path.exists(output_dir): os.makedirs(output_dir)
    
    ts = datetime.now().strftime("%Y%m%d_%H%M")
    mode_str = "cp" if args.cp else "price"
    csv_path = os.path.join(output_dir, f"biggoALL_{mode_str}_{ts}.csv")
    
    with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
        fieldnames = ["id", "source", "name", "price", "storage", "cp_value", "link"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in processed:
            writer.writerow(r)
    
    print(f"\n✅ 完成！報表已存至: {csv_path}")

if __name__ == "__main__":
    asyncio.run(main())
