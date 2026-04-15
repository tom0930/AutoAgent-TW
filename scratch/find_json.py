import urllib.request
import ssl
import json
import re

ssl_context = ssl._create_unverified_context()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}

def analyze_biggo():
    url = "https://biggo.com.tw/s/iPhone+15/?sort=lp"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, context=ssl_context) as resp:
        html = resp.read().decode('utf-8')
        
        # Next.js often uses __NEXT_DATA__
        match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html)
        if match:
            print("Found __NEXT_DATA__")
            with open("scratch/biggo_data.json", "w", encoding="utf-8") as f:
                f.write(match.group(1))
            return "Saved to scratch/biggo_data.json"
        
        # Or look for any large JSON-like script
        match = re.search(r'self\.__next_f\.push\(\[1,"(.*?)"\]\)', html)
        if match:
            print("Found next_f.push data")
            return "Found streaming data"
            
        return "No clear JSON found"

if __name__ == "__main__":
    print(analyze_biggo())
