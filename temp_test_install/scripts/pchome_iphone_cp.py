import asyncio
import json
import csv
import re
from datetime import datetime
import os
import urllib.request
import ssl

# 禁用 SSL 驗證
ssl_context = ssl._create_unverified_context()

def extract_storage(name):
    # 優化後的正則表達式，支援 GB, G, TB, T (不分大小寫)
    match = re.search(r'(\d+)\s*(GB|G|TB|T)', name, re.I)
    if not match:
        return 0
    
    val = int(match.group(1))
    unit = match.group(2).upper()
    
    if 'T' in unit:
        return val * 1024
    return val

async def fetch_pchome_data():
    print("🚀 啟動 PChome 深度資料獲取系統...")
    output_dir = "artifacts/scraping_results"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Referer": "https://24h.pchome.com.tw/"
    }

    all_raw_prods = []
    
    # 策略 1: 抓取特定分類 DYAX00C (iPhone 福利品)
    category_id = "DYAX00C"
    print(f"📡 正在抓取分類 API: {category_id}...")
    for page in range(1, 3): # 抓前兩頁
        url = f"https://ecapi-24h.pchome.com.tw/category/v1.1/{category_id}/products?page={page}&limit=40"
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, context=ssl_context) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                if isinstance(data, list): # 分類 API 有時回傳 list
                    all_raw_prods.extend(data)
                elif "Nodes" in data:
                    all_raw_prods.extend(data["Nodes"])
                print(f"   - 第 {page} 頁抓取成功")
        except Exception as e:
            print(f"   - 分類 API 第 {page} 頁失敗: {e}")

    # 策略 2: 抓取關鍵字搜尋 (補足遺珠)
    print("🔍 正在抓取搜尋 API: iPhone 福利品...")
    search_url = "https://ecshweb.pchome.com.tw/search/v3.3/all/results?q=iPhone%20%E7%A6%8F%E5%88%A9%E5%93%81&page=1&sort=rnk/dc"
    try:
        req = urllib.request.Request(search_url, headers=headers)
        with urllib.request.urlopen(req, context=ssl_context) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            if "prods" in data:
                all_raw_prods.extend(data["prods"])
    except Exception as e:
        print(f"   - 搜尋 API 失敗: {e}")

    # 資料處理
    results = []
    seen_ids = set()
    
    for p in all_raw_prods:
        # PChome API 欄位名稱可能不一 (Id vs ID, Name vs name)
        pid = p.get("Id") or p.get("ID") or p.get("id")
        name = p.get("Name") or p.get("name", "")
        price = p.get("Price") or p.get("price", 0)
        
        if not pid or not name or pid in seen_ids:
            continue
            
        seen_ids.add(pid)
        storage = extract_storage(name)
        
        if storage > 0 and price > 0:
            cp_value = round(storage / (price / 10000), 2)
            results.append({
                "id": pid,
                "title": name,
                "price": price,
                "storage": storage,
                "cp_value": cp_value,
                "link": f"https://24h.pchome.com.tw/prod/{pid}"
            })

    # 排序
    results.sort(key=lambda x: x['cp_value'], reverse=True)

    if not results:
        print("⚠️ 未能提取到任何有效商品。")
        return

    print(f"✅ 成功處理 {len(results)} 筆有效商品。")

    # 顯示前 10 名
    print("\n" + "🏆 PChome iPhone 福利品 CP值排行榜 (Top 10)")
    print("="*95)
    print(f"{'排名':<4} | {'CP值':<6} | {'價格':>8} | {'容量':>6} | {'商品名稱'}")
    print("-" * 95)
    for i, r in enumerate(results[:10], 1):
        print(f"{i:<4} | {r['cp_value']:>6.2f} | {r['price']:>8,} | {r['storage']:>4}GB | {r['title']}")
    print("="*95)

    # 儲存報表
    ts = datetime.now().strftime("%Y%m%d_%H%M")
    csv_path = os.path.join(output_dir, f"iphone_final_ranks_{ts}.csv")
    json_path = os.path.join(output_dir, f"iphone_final_ranks_{ts}.json")

    # CSV
    with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=['rank', 'cp_value', 'price', 'storage', 'title', 'link', 'id'])
        writer.writeheader()
        for i, r in enumerate(results, 1):
            row = r.copy()
            row['rank'] = i
            writer.writerow(row)

    # JSON
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n📁 報表已匯出：\n - CSV: {csv_path}\n - JSON: {json_path}")

if __name__ == "__main__":
    asyncio.run(fetch_pchome_data())




