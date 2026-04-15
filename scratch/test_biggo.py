import urllib.request
import ssl
import json
import re

ssl_context = ssl._create_unverified_context()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}

def search_biggo(query):
    query_encoded = urllib.parse.quote(query)
    url = f"https://biggo.com.tw/s/{query_encoded}/?sort=lp"
    print(f"Fetching {url}...")
    
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, context=ssl_context) as resp:
            html = resp.read().decode('utf-8')
            
            # BigGo often hides data in a script tag as JSON
            # Look for something like window.__PRELOADED_STATE__ or similar
            # Or just scrape the DOM if it's rendered server-side (older results)
            
            # Find JSON in script tags
            scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.S)
            for s in scripts:
                if 'itemListElement' in s: # Schema.org JSON-LD
                    print("Found Schema.org JSON-LD")
                    # Try to extract JSON
                    match = re.search(r'(@context.*?})', s, re.S)
                    if match:
                        return match.group(1)
            
            return html[:2000] # Return snippet if nothing found
    except Exception as e:
        return str(e)

if __name__ == "__main__":
    result = search_biggo("iPhone 15")
    print(result)
