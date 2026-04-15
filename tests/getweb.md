**✅ 完整 Python + Playwright 腳本：PChome 24h iPhone 福利品 CP值排行**

這個腳本會：

- 進入你給的福利品分類頁
- 自動滾動載入所有商品
- 提取每個 iPhone 的 **型號、價格、容量、連結**
- 計算簡單 **CP值**（目前以「容量 GB / 價格」為基準，越高越划算）
- 排序後輸出前10名最高 CP 值，並存成 CSV + JSON

```python
from playwright.async_api import async_playwright
import asyncio
import json
import csv
import re
from datetime import datetime

async def scrape_pchome_iphones():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=800)  # 改 True 就變無頭
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        page = await context.new_page()
      
        print("正在前往 PChome iPhone 福利品頁...")
        await page.goto(
            "https://24h.pchome.com.tw/category/DYAX00C",
            wait_until="networkidle"
        )
      
        # 滾動載入所有商品
        print("正在滾動載入所有商品...")
        last_height = 0
        for _ in range(15):  # 最多滾15次
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_timeout(1500)
            new_height = await page.evaluate("document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
      
        # 提取商品資料
        print("正在提取商品資料...")
        products = await page.evaluate('''() => {
            const items = Array.from(document.querySelectorAll('div.c1, div.item, .goods, article, li')) // 常見容器
                .filter(el => el.textContent.includes('iPhone') || el.textContent.includes('Apple'));
          
            return items.map(el => {
                const titleEl = el.querySelector('h3, .title, .name, a') || el;
                const priceEl = el.querySelector('.price, .amount, .value, .sale-price');
                const linkEl = el.querySelector('a');
              
                const title = titleEl ? titleEl.innerText.trim() : '';
                let priceText = priceEl ? priceEl.innerText.trim() : '';
                priceText = priceText.replace(/[^0-9]/g, '');
                const price = parseInt(priceText) || 0;
              
                const link = linkEl ? (linkEl.href.startsWith('http') ? linkEl.href : 'https://24h.pchome.com.tw' + linkEl.href) : '';
              
                // 提取容量 (GB)
                const gbMatch = title.match(/(\d+)\s*GB/i);
                const storage = gbMatch ? parseInt(gbMatch[1]) : 0;
              
                return { title, price, storage, link };
            }).filter(p => p.title && p.price > 0);
        }''')
      
        # 計算 CP 值並排序
        for p in products:
            p['cp_value'] = round(p['storage'] / (p['price'] / 10000), 2) if p['price'] > 0 else 0  # GB / 萬
      
        products.sort(key=lambda x: x['cp_value'], reverse=True)
      
        # 顯示結果
        print("\n=== iPhone 福利品 CP值排行 (前10名) ===")
        for i, p in enumerate(products[:10], 1):
            print(f"{i:2d}. {p['title'][:60]:60} | "
                  f"價格: NT${p['price']:,} | "
                  f"容量: {p['storage']}GB | "
                  f"CP值: {p['cp_value']}")
      
        # 儲存檔案
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
      
        # CSV
        with open(f'iphone_cp_ranking_{timestamp}.csv', 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=['rank', 'title', 'price', 'storage_gb', 'cp_value', 'link'])
            writer.writeheader()
            for i, p in enumerate(products, 1):
                writer.writerow({
                    'rank': i,
                    'title': p['title'],
                    'price': p['price'],
                    'storage_gb': p['storage'],
                    'cp_value': p['cp_value'],
                    'link': p['link']
                })
      
        # JSON
        with open(f'iphone_cp_ranking_{timestamp}.json', 'w', encoding='utf-8') as f:
            json.dump(products, f, ensure_ascii=False, indent=2)
      
        print(f"\n✅ 完成！共找到 {len(products)} 筆商品")
        print(f"   已儲存 CSV 和 JSON 檔案")
      
        await browser.close()

# 執行
if __name__ == "__main__":
    asyncio.run(scrape_pchome_iphones())
```

### 如何使用

1. 安裝依賴：

```bash
pip install playwright
playwright install chromium
```

2. 執行腳本：

```bash
python pchome_iphone_cp.py
```

### 注意事項 & 優化建議

- **選擇器**：PChome 常更新，如果抓不到資料，請按 `F12` 看實際 class 名稱，修改 `querySelectorAll` 那行即可。
- **CP值計算**：目前用「容量/價格」，你可以改成更複雜的公式（例如加上型號年份、Pro 等級權重）。
- **想更精準**：我可以再幫你加上「點進每個商品頁抓完整規格」的版本。
- **無頭模式**：正式跑時把 `headless=False` 改成 `True`。

需要我幫你**加上排序功能**（價格由低到高、最新機型優先等）、**自動通知**（Line / Email），或是**抓取更多頁面細節**，告訴我！
