
import time
import os
import sys
print(f"Sub-agent PID: {os.getpid()}")
try:
    print("Attempting to allocate 1.5GB...")
    size = 1500 * 1024 * 1024
    data = bytearray(size)
    print("Touching pages...")
    for i in range(0, size, 4096):
        data[i] = 1
    print("SUCCESS: Allocation and touch worked (BAD!)")
except MemoryError:
    print("MemoryError caught (GOOD!)")
    sys.exit(1)
except Exception as e:
    print(f"Caught other exception: {e}")
    sys.exit(2)
time.sleep(1)
