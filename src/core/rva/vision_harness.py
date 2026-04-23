"""
AI Harness Vision Engine
功能：螢幕截圖、即時錄製、滑鼠/鍵盤控制、CDP 整合
版本：v1.0.0
"""
import mss
import numpy as np
import cv2
import time
import ctypes
from typing import Optional, Tuple, List, Dict, Any
from dataclasses import dataclass
from ctypes import wintypes
import threading
import queue


@dataclass
class ScreenRegion:
    """螢幕區域"""
    x: int
    y: int
    width: int
    height: int
    
    @property
    def monitor_dict(self) -> dict:
        return {
            "left": self.x,
            "top": self.y,
            "width": self.width,
            "height": self.height
        }


@dataclass
class Monitor:
    """顯示器資訊"""
    index: int
    x: int
    y: int
    width: int
    height: int
    
    @property
    def is_primary(self) -> bool:
        return self.index == 1


class VisionHarness:
    """
    Vision Engine - 螢幕視覺處理引擎
    
    提供與 OpenClaw xbrowser 同等的螢幕檢視功能。
    
    功能：
    - 多顯示器支援
    - 高效能截圖（mss + numpy）
    - 特定視窗擷取
    - 滑鼠追蹤
    - 即時錄製（規劃中）
    """
    
    def __init__(self, monitor_index: int = 1):
        """
        初始化 Vision Engine
        
        Args:
            monitor_index: 預設顯示器索引 (1 = 首要)
        """
        self.monitor_index = monitor_index
        self.sct = mss.mss()
        self._last_frame = None
        self._capture_queue = queue.Queue(maxsize=10)
        self._is_capturing = False
        
        # 取得顯示器資訊
        self.monitors = self._detect_monitors()
    
    def _detect_monitors(self) -> List[Monitor]:
        """偵測所有顯示器"""
        monitors = []
        
        for i, m in enumerate(self.sct.monitors):
            monitors.append(Monitor(
                index=i,
                x=m['x'],
                y=m['y'],
                width=m['width'],
                height=m['height']
            ))
        
        return monitors
    
    def screenshot(self, 
                  region: Optional[ScreenRegion] = None,
                  quality: int = 85,
                  format: str = 'jpg') -> bytes:
        """
        截圖
        
        Args:
            region: 截圖區域，None 為全螢幕
            quality: JPEG 品質 (1-100)
            format: 輸出格式 ('jpg', 'png', 'bmp')
        
        Returns:
            圖片資料 (bytes)
        """
        if region:
            monitor = region.monitor_dict
        else:
            monitor = self.sct.monitors[self.monitor_index]
        
        # 截圖
        img = np.array(self.sct.grab(monitor))
        
        # 轉換：BGR (mss) -> RGB
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        
        # 壓縮
        if format.lower() == 'jpg':
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
            _, buffer = cv2.imencode('.jpg', img_rgb, encode_param)
            return buffer.tobytes()
        elif format.lower() == 'png':
            _, buffer = cv2.imencode('.png', img_rgb)
            return buffer.tobytes()
        else:
            # BMP
            return img_rgb.tobytes()
    
    def screenshot_to_file(self, 
                           path: str,
                           region: Optional[ScreenRegion] = None,
                           quality: int = 85):
        """
        截圖並儲存到檔案
        
        Args:
            path: 輸出檔案路徑
            region: 截圖區域
            quality: JPEG 品質
        """
        data = self.screenshot(region, quality)
        
        ext = path.split('.')[-1].lower()
        if ext == 'png':
            format_str = '.png'
        elif ext in ('jpg', 'jpeg'):
            format_str = '.jpg'
        else:
            format_str = '.png'
        
        with open(path, 'wb') as f:
            f.write(data)
    
    def capture_window(self, window_title: str) -> Optional[bytes]:
        """
        擷取特定視窗
        
        Args:
            window_title: 視窗標題（支援部分匹配）
        
        Returns:
            視窗截圖資料，視窗不存在則返回 None
        """
        # 透過 Windows API 找到視窗
        hwnd = self._find_window(window_title)
        if not hwnd:
            return None
        
        # 取得視窗位置
        rect = wintypes.RECT()
        ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(rect))
        
        region = ScreenRegion(
            x=rect.left,
            y=rect.top,
            width=rect.right - rect.left,
            height=rect.bottom - rect.top
        )
        
        return self.screenshot(region)
    
    def _find_window(self, title: str) -> Optional[int]:
        """尋找視窗"""
        hwnd = ctypes.windll.user32.FindWindowW(None, title)
        if hwnd:
            return hwnd
        
        # 部分匹配
        def enum_callback(hwnd, _):
            length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
            if length == 0:
                return True
            
            buffer = ctypes.create_unicode_buffer(length + 1)
            ctypes.windll.user32.GetWindowTextW(hwnd, buffer, length + 1)
            
            if title.lower() in buffer.value.lower():
                return False
            
            return True
        
        EnumWindowsProc = ctypes.WINFUNCTYPE(
            ctypes.c_bool,
            ctypes.POINTER(ctypes.c_int),
            ctypes.POINTER(ctypes.c_int)
        )
        
        ctypes.windll.user32.EnumWindows(EnumWindowsProc(enum_callback), 0)
        
        return None
    
    def get_screen_info(self) -> Dict[str, Any]:
        """取得螢幕資訊"""
        monitors_data = []
        
        for m in self.monitors:
            monitors_data.append({
                'index': m.index,
                'x': m.x,
                'y': m.y,
                'width': m.width,
                'height': m.height,
                'is_primary': m.is_primary
            })
        
        return {
            'monitors': monitors_data,
            'total': len(monitors_data),
            'primary': self.monitor_index
        }
    
    def get_cursor_position(self) -> Tuple[int, int]:
        """取得滑鼠位置"""
        class POINT(ctypes.Structure):
            _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]
        
        pt = POINT()
        ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
        return (pt.x, pt.y)
    
    def start_continuous_capture(self, interval: float = 0.1):
        """
        啟動連續截圖
        
        Args:
            interval: 截圖間隔（秒）
        """
        self._is_capturing = True
        
        def capture_loop():
            while self._is_capturing:
                frame = self.screenshot()
                try:
                    self._capture_queue.put_nowait(frame)
                except queue.Full:
                    try:
                        self._capture_queue.get_nowait()
                        self._capture_queue.put_nowait(frame)
                    except:
                        pass
                time.sleep(interval)
        
        self._capture_thread = threading.Thread(target=capture_loop, daemon=True)
        self._capture_thread.start()
    
    def stop_continuous_capture(self):
        """停止連續截圖"""
        self._is_capturing = False
    
    def get_frame(self) -> Optional[bytes]:
        """取得最新一幀（需先呼叫 start_continuous_capture）"""
        try:
            return self._capture_queue.get_nowait()
        except queue.Empty:
            return None
    
    def compare_screens(self, 
                       region1: ScreenRegion, 
                       region2: ScreenRegion,
                       threshold: float = 0.95) -> float:
        """
        比較兩個區域的畫面相似度
        
        Returns:
            相似度 (0-1)
        """
        img1 = self.screenshot(region1)
        img2 = self.screenshot(region2)
        
        # 解碼
        nparr1 = np.frombuffer(img1, np.uint8)
        nparr2 = np.frombuffer(img2, np.uint8)
        
        frame1 = cv2.imdecode(nparr1, cv2.IMREAD_COLOR)
        frame2 = cv2.imdecode(nparr2, cv2.IMREAD_COLOR)
        
        if frame1 is None or frame2 is None:
            return 0.0
        
        # 調整大小相同
        if frame1.shape != frame2.shape:
            frame2 = cv2.resize(frame2, (frame1.shape[1], frame1.shape[0]))
        
        # 計算相似度
        diff = cv2.absdiff(frame1, frame2)
        similarity = 1.0 - (np.sum(diff) / (diff.shape[0] * diff.shape[1] * 255))
        
        return similarity
    
    def find_on_screen(self, 
                       template_path: str,
                       region: Optional[ScreenRegion] = None,
                       threshold: float = 0.8) -> Optional[Tuple[int, int]]:
        """
        在螢幕上尋找圖案
        
        Args:
            template_path: 模板圖片路徑
            region: 搜尋區域
            threshold: 匹配閾值
        
        Returns:
            匹配位置的 (x, y)，未找到則返回 None
        """
        # 截圖
        screenshot = self.screenshot(region)
        screen = cv2.imdecode(
            np.frombuffer(screenshot, np.uint8), 
            cv2.IMREAD_COLOR
        )
        
        # 載入模板
        template = cv2.imread(template_path, cv2.IMREAD_COLOR)
        if template is None:
            return None
        
        # 模板匹配
        result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        if max_val >= threshold:
            return (max_loc[0], max_loc[1])
        
        return None
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.close()
    
    def close(self):
        """關閉資源"""
        self.stop_continuous_capture()
        self.sct.close()


def main():
    """測試"""
    with VisionHarness() as vision:
        # 取得螢幕資訊
        info = vision.get_screen_info()
        print(f"Monitors: {info['total']}")
        for m in info['monitors']:
            print(f"  Monitor {m['index']}: {m['width']}x{m['height']} at ({m['x']}, {m['y']})")
        
        # 截圖
        print("\nCapturing screenshot...")
        screenshot = vision.screenshot()
        print(f"Screenshot size: {len(screenshot)} bytes")
        
        # 儲存
        vision.screenshot_to_file("screenshot_test.jpg")
        print("Saved to screenshot_test.jpg")


if __name__ == '__main__':
    main()
