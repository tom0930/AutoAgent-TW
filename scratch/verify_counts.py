import os

active_dir = r"C:\Users\TOM\.gemini\antigravity\skills"
library_dir = r"C:\Users\TOM\.gemini\antigravity\skills_library"

active_count = len([d for d in os.listdir(active_dir) if os.path.isdir(os.path.join(active_dir, d))])
library_count = len([d for d in os.listdir(library_dir) if os.path.isdir(os.path.join(library_dir, d))])

print(f"Active Skills: {active_count}")
print(f"Library Skills: {library_count}")

if 50 < active_count < 200:
    print("[PASS] Active count valid.")
else:
    print("[FAIL] Active count out of range.")
    
if library_count >= 1500:
    print("[PASS] Library intact.")
else:
    print("[FAIL] Library is missing skills.")
