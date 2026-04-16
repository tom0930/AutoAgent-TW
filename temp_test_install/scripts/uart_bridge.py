import serial
import socket
import threading
import json
import time
import sys

def load_config():
    with open("_configs/flash_config.json", "r") as f:
        return json.load(f)

def uart_to_udp():
    config = load_config()
    u_cfg = config["uart_settings"]
    
    # Setup UDP Sockets
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    targets = [
        (u_cfg["udp_host"], u_cfg["udp_port_human"]),
        (u_cfg["udp_host"], u_cfg["udp_port_ai"])
    ]

    print(f"[Bridge] Opening {u_cfg['port']} @ {u_cfg['baudrate']}...")
    log_file = open("logs/uart_raw.log", "ab") # Append Binary
    
    try:
        ser = serial.Serial(u_cfg["port"], u_cfg["baudrate"], timeout=u_cfg["timeout"])
        
        # Thread for receiving UDP commands and sending back to Serial
        def handle_inbound():
            cmd_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            cmd_sock.bind((u_cfg["udp_host"], u_cfg["udp_port_ai"])) # AI Port
            while True:
                data, addr = cmd_sock.recvfrom(1024)
                #print(f"[Bridge] Received Command from AI: {data.hex()}")
                #ser.write(data)
                #log_file.write(f"\n[AI-CMD] {data.hex()}\n".encode())
                #log_file.flush()
        
        t = threading.Thread(target=handle_inbound, daemon=True)
        t.start()

        print(f"[Bridge] Status: Connected. Logging to logs/uart_raw.log")
        while True:
            if ser.in_waiting > 0:
                data = ser.read(ser.in_waiting)
                # Save to file
                log_file.write(data)
                log_file.flush()
                # Broadcast to both Docklight and AI
                for target in targets:
                    sock.sendto(data, target)
            time.sleep(0.01)

    except serial.SerialException as e:
        print(f"Error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n[Bridge] Stopping...")
        log_file.close()
        ser.close()


if __name__ == "__main__":
    uart_to_udp()
