import uiautomation as auto
import time

def try_fix():
    print("Listing potential targets...")
    targets = ["Status", "com.lbjlaq.antigravity-tools-siw", "Antigravity Manager"]
    
    for target_name in targets:
        win = auto.WindowControl(searchDepth=1, Name=target_name)
        if not win.Exists(0):
            # Try partial match
            win = auto.WindowControl(searchDepth=1, Name=target_name, searchInterval=1)
            
        if win.Exists(1):
            print(f"--- Scanning Window: {target_name} ---")
            win.SetFocus()
            
            # Find elements with 'Proxy' in Name
            proxy_items = win.GetChildren()
            # Deep search for any button or list item
            for item in win.ButtonControl(searchDepth=10).GetChildren():
                if "Proxy" in item.Name:
                    print(f"Found match: {item.Name} at {item.BoundingRectangle}")
                    item.Click()
                    return True
            
            # Fallback direct search
            target_btn = win.ButtonControl(searchDepth=10, Name="Proxy")
            if target_btn.Exists(0):
                target_btn.Click()
                print("Clicked Proxy Button.")
                return True
                
            # Try toggle pattern
            for child in win.GetChildren():
                if "Proxy" in child.Name:
                    print(f"Clicking related item: {child.Name}")
                    child.Click()
                    return True
    
    print("Could not find Proxy control.")
    return False

if __name__ == "__main__":
    try_fix()
