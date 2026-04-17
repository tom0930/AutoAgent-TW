import re
import json

def extract_biggo_products(html):
    print("Extracting products from BigGo stream...")
    
    # 1. Extract all push content
    pushes = re.findall(r'self\.__next_f\.push\(\[1,"(.*?)"\]\)', html)
    print(f"Chunks found: {len(pushes)}")
    
    for i, p in enumerate(pushes):
        # Unescape the chunk
        # Note: it's not pure JSON, it's a serialized string in a JSON array
        unescaped = p.replace('\\"', '"').replace('\\\\', '\\').replace('\\/', '/')
        
        # Look for the product list marker
        if '"list":[' in unescaped:
            print(f"Target found in chunk {i+1} (length: {len(unescaped)})")
            
            # Find the start of the list
            match = re.search(r'"list":\s*(\[.*?\])(?=\s*,"promo")', unescaped)
            if not match:
                match = re.search(r'"list":\s*(\[.*\])', unescaped)
                
            if match:
                try:
                    items_json = match.group(1)
                    # Use JSONDecoder to find the first valid array in the captured string
                    decoder = json.JSONDecoder()
                    items, index = decoder.raw_decode(items_json)
                    print(f"Successfully parsed {len(items)} items using raw_decode.")
                    return items
                except Exception as e:
                    print(f"JSON parsing failed: {e}")
                    # Try manual truncation logic
                    print("Attempting manual truncation...")
                    # pyrefly: ignore [unbound-name]
                    last_bracket = items_json.rfind(']')
                    if last_bracket != -1:
                        try:
                            items = json.loads(items_json[:last_bracket+1])
                            print(f"Parsed {len(items)} items after manual truncation.")
                            return items
                        except: pass
                    
                    # Fallback: regex for individual items (more flexible)
                    print("Falling back to item regex...")
                    item_blocks = re.findall(r'\{"nindex":".*?","title":".*?","price":\d+.*?\}', unescaped)
                    print(f"Individual item regex found {len(item_blocks)} blocks.")
                    results = []
                    for block in item_blocks:
                        try:
                            results.append(json.loads(block))
                        except: continue
                    return results

    print("No 'list' marker found in any chunk.")
    return []

if __name__ == "__main__":
    try:
        with open("scratch/biggo_raw.html", "r", encoding="utf-8") as f:
            content = f.read()
            
        products = extract_biggo_products(content)
        if products:
            print(f"\nTotal products extracted: {len(products)}")
            print("-" * 50)
            for i, p in enumerate(products[:15]):
                title = p.get("title", "No Title")
                price = p.get("price", "N/A")
                store = p.get("store", {}).get("name", "Unknown Store")
                print(f"{i+1:2}. [{store:12}] {title[:60]}... ${price}")
        else:
            print("Extraction failed.")
    except FileNotFoundError:
        print("Error: scratch/biggo_raw.html not found. Please run the data capture step first.")
