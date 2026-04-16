import os
import requests

def send_line_notification(message):
    token = os.getenv("LINE_NOTIFY_TOKEN")
    
    if not token:
        print("[MOCK] LINE NOTIFY: " + message)
        return False
        
    url = "https://notify-api.line.me/api/notify"
    headers = {"Authorization": "Bearer " + token}
    payload = {"message": message}
    
    try:
        response = requests.post(url, headers=headers, params=payload)
        if response.status_code == 200:
            print("LINE notification sent.")
            return True
        else:
            print(f"Failed to send LINE notification: {response.status_code}")
            return False
    except Exception as e:
        print(f"Error sending LINE notification: {e}")
        return False

if __name__ == "__main__":
    import sys
    msg = "Test from AutoAgent-TW" if len(sys.argv) < 2 else sys.argv[1]
    send_line_notification(msg)
