import os
import json

INDEX_PATH = r"C:\Users\TOM\.gemini\antigravity\skills\data\skills_index.json"

def test_search(query):
    if not os.path.exists(INDEX_PATH):
        print("Index not found.")
        return
    
    with open(INDEX_PATH, 'r', encoding='utf-8') as f:
        index = json.load(f)
        
    query = query.lower()
    results = []
    for s in index:
        if query in s['name'].lower() or query in s['description'].lower() or query in s['id'].lower():
            results.append(s)
            
    print(f"--- Search Results for '{query}' ---")
    for s in results[:5]:
        print(f"[{s['id']}] {s['name']}\n    {s['description']}\n")

if __name__ == "__main__":
    queries = ["search", "price", "shopping"]
    for q in queries:
        test_search(q)
