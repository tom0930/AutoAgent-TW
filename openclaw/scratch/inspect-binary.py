import sys
import re

binary_path = r"C:\Users\TOM\AppData\Local\Programs\Antigravity\resources\app\extensions\antigravity\bin\language_server_windows_x64.exe"

patterns = [
    rb'X-Goog-.*',
    rb'auth_token',
    rb'session_token',
    rb'local_token',
    rb'Authorization',
    rb'Bearer',
    rb'https://.*\.googleapis\.com'
]

with open(binary_path, 'rb') as f:
    content = f.read()
    for p in patterns:
        matches = re.findall(p, content)
        if matches:
            print(f"Pattern {p} matched {len(matches)} times. Samples:")
            for m in matches[:5]:
                try:
                    print(f"  {m.decode('utf-8', errors='ignore')}")
                except:
                    print(f"  {m}")
