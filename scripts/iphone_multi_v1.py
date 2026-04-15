"""
iPhone 15 Cross-Platform CP Value Comparison Engine (v2.5.0)
-----------------------------------------------------------
Authors: Antigravity AI Engine
Description: 
    Autonomous data extraction tool for comparing iPhone 15 prices across 
    PChome (API-based) and BigGo (Next.js Stream-based). Calculates 
    CP (Cost-Performance) values using Storage/Price ratio.
    
Usage:
    python scripts/iphone_multi_v1.py
"""
import asyncio
import json
import csv
import re
from datetime import datetime
import os
import urllib.request
import urllib.parse
import ssl

# Disable SSL verification for local runs
ssl_context = ssl._create_unverified_context()

def extract_storage(name):
    # Support GB, G, TB, T (case-insensitive), handles no-space cases like 256G
    match = re.search(r'(\d+)\s*(GB|G|TB|T)', name, re.I)
    if not match:
        # Fallback for patterns like 256g 128g
        match = re.search(r'(\d+)(gb|g|tb|t)', name, re.I)
        if not match:
            return 0
    val = int(match.group(1))
    unit = match.group(2).upper()
    if 'T' in unit:
        return val * 1024
    return val

def fetch_biggo_data(query="iphone 15"):
    print(f"📡 正在從 BigGo 抓取資料: {query}...")
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"}
    encoded_query = urllib.parse.quote(query)
    url = f"https://biggo.com.tw/s/{encoded_query}/?sort=lp"
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, context=ssl_context) as resp:
            html = resp.read().decode('utf-8')
            
        print(f"   - BigGo HTML 長度: {len(html)}")
        # Parse Next.js stream
        pushes = re.findall(r'self\.__next_f\.push\(\[1,"(.*?)"\]\)', html)
        print(f"   - BigGo 串流區塊: {len(pushes)}")
        all_results = []
        
        for i, p in enumerate(pushes):
            unescaped = p.replace('\\"', '"').replace('\\\\', '\\').replace('\\/', '/')
            if '"list":[' in unescaped:
                print(f"   - 在區塊 {i+1} 找到商品列表 (長度: {len(unescaped)})")
                match = re.search(r'"list":\s*(\[.*?\])(?=\s*,"promo")', unescaped)
                if not match:
                    match = re.search(r'"list":\s*(\[.*\])', unescaped)
                
                if match:
                    try:
                        items_json = match.group(1)
                        decoder = json.JSONDecoder()
                        # Handle potential trailing garbage in Next.js stream
                        items, index = decoder.raw_decode(items_json)
                        
                        found_count = 0
                        for item in items:
                            title = item.get("title") or item.get("name", "")
                            storage = extract_storage(title)
                            price = item.get("price", 0)
                            if storage > 0 and price > 1000:
                                cp_value = round(storage / (price / 10000), 2)
                                all_results.append({
                                    "platform": "BigGo",
                                    "store": item.get("store", {}).get("name", "Unknown"),
                                    "title": title,
                                    "price": price,
                                    "storage": storage,
                                    "cp_value": cp_value,
                                    "link": f"https://biggo.com.tw{item.get('purl', '')}"
                                })
                                found_count += 1
                        print(f"   - BigGo 成功提取 {found_count} 筆商品")
                        return all_results
                    except Exception as e:
                        print(f"   - BigGo 解析錯誤: {e}")
                        # Last ditch effort: manual truncation
                        try:
                            last_bracket = items_json.rfind(']')
                            items = json.loads(items_json[:last_bracket+1])
                        except Exception:
                            pass
        return all_results
    except Exception as e:
        print(f"   - BigGo 抓取失敗: {e}")
        return []

async def fetch_pchome_data():
    print("📡 正在從 PChome 抓取資料...")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Referer": "https://24h.pchome.com.tw/"
    }
    
    all_raw_prods = []
    # iPhone Category
    cat_url = "https://ecapi-24h.pchome.com.tw/category/v1.1/DYAX00C/products?page=1&limit=40"
    # Search
    search_url = "https://ecshweb.pchome.com.tw/search/v3.3/all/results?q=iPhone%2015&page=1&sort=rnk/dc"
    
    for url in [cat_url, search_url]:
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, context=ssl_context) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                if isinstance(data, list):
                    all_raw_prods.extend(data)
                elif "Nodes" in data:
                    all_raw_prods.extend(data["Nodes"])
                elif "prods" in data:
                    all_raw_prods.extend(data["prods"])
        except Exception:
            continue
        
    results = []
    seen = set()
    for p in all_raw_prods:
        pid = p.get("Id") or p.get("ID") or p.get("id")
        name = p.get("Name") or p.get("name", "")
        price = p.get("Price") or p.get("price", 0)
        if not pid or pid in seen:
            continue
        seen.add(pid)
        storage = extract_storage(name)
        if storage > 0 and price > 1000:
            cp_value = round(storage / (price / 10000), 2)
            results.append({
                "platform": "PChome",
                "store": "PChome 24h",
                "title": name,
                "price": price,
                "storage": storage,
                "cp_value": cp_value,
                "link": f"https://24h.pchome.com.tw/prod/{pid}"
            })
    return results

async def main():
    print("🚀 啟動跨平台 iPhone 15 CP值比價系統...")
    
    # Run fetchers - Use more specific queries to find real phones
    biggo_results = fetch_biggo_data("iphone 15 128G")
    pchome_results = await fetch_pchome_data()
    
    all_results = biggo_results + pchome_results
    all_results.sort(key=lambda x: x['cp_value'], reverse=True)
    
    if not all_results:
        print("❌ 未能獲取任何有效資料。")
        return

    # Display Top 20
    print("\n" + "🏆 跨平台 iPhone 15 CP值排行榜 (Top 20)")
    print("="*110)
    print(f"{'排名':<4} | {'來源':<10} | {'CP值':<6} | {'價格':>8} | {'容量':>6} | {'商品名稱'}")
    print("-" * 110)
    for i, r in enumerate(all_results[:20], 1):
        print(f"{i:<4} | {r['platform']:<10} | {r['cp_value']:>6.2f} | {r['price']:>8,} | {r['storage']:>4}GB | {r['title'][:60]}")
    print("="*110)

    # Save Results
    output_dir = "artifacts/scraping_results"
    os.makedirs(output_dir, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M")
    csv_path = os.path.join(output_dir, f"iphone_cross_platform_{ts}.csv")
    
    with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=['platform', 'store', 'cp_value', 'price', 'storage', 'title', 'link'])
        writer.writeheader()
        writer.writerows(all_results)
        
    print(f"\n📂 報表已儲存至: {csv_path}")

if __name__ == "__main__":
    asyncio.run(main())
