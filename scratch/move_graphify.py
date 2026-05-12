import shutil
import os
from pathlib import Path

src = Path(r"z:\AutoAgent-TW\graphify-out")
dest = Path(r"z:\AutoAgent-TW\.planning\graphify-out")

if src.exists():
    for item in src.iterdir():
        dest_item = dest / item.name
        if dest_item.exists():
            if dest_item.is_dir():
                shutil.rmtree(dest_item)
            else:
                dest_item.unlink()
        shutil.move(str(item), str(dest))
    print("[+] Successfully moved graphify results to .planning/graphify-out/")
else:
    print("[!] Source directory not found.")
