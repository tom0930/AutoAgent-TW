from pywinauto import Desktop
import sys

def inspect_all(pattern=None, class_name=None):
    if class_name:
        print(f"Searching for Class: {class_name}")
        windows = Desktop(backend="uia").windows(class_name=class_name)
    else:
        print(f"Searching for Title: {pattern}")
        windows = Desktop(backend="uia").windows(title_re=f".*{pattern}.*")
    
    print(f"Found {len(windows)} matches.")
    
    for i, win in enumerate(windows):
        print(f"\n=== Window {i}: {win.window_text()} (Class: {win.class_name()}) ===")
        try:
            win.print_control_identifiers()
        except:
            print("Could not dump identifiers for this window.")

if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--class":
        inspect_all(class_name=sys.argv[2])
    else:
        p = sys.argv[1] if len(sys.argv) > 1 else "Status"
        inspect_all(pattern=p)
