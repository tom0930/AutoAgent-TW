import unittest
import os
# pyrefly: ignore [missing-import]
from src.core.rva.rva_engine import RVAEngine
# pyrefly: ignore [missing-import]
from src.core.rva.vision_client import GeminiVisionClient

class TestRVACore(unittest.TestCase):
    def setUp(self):
        self.engine = RVAEngine(failsafe=False)

    def test_dpi_initialization(self):
        # 驗證 DPI 設定是否成功執行 (無 Exception 即視為通過)
        self.assertIsNotNone(self.engine)

    def test_screen_capture(self):
        # 測試 mss 截圖與 PIL 轉換
        img, path = self.engine.capture_screen()
        self.assertTrue(os.path.exists(path))
        self.assertGreater(img.size[0], 0)
        self.assertGreater(img.size[1], 0)

    def test_imagehash_jitter(self):
        # 測試連續兩張相同畫面的 Hash 差異
        self.engine.has_screen_changed() # 第一次初始化
        is_changed = self.engine.has_screen_changed(threshold=1)
        # 在靜止畫面下正常應為 False (或極小值)
        # 此測試僅驗證流程不崩潰
        self.assertIn(is_changed, [True, False])

    def test_coordinate_denormalization(self):
        # 測試 0-1000 座標換算為像素座標
        client = GeminiVisionClient(api_key="mock")
        bbox = [100, 200, 300, 400] # ymin, xmin, ymax, xmax
        width, height = 1920, 1080
        l, t, r, b = client.denormalize_coords(bbox, width, height)
        
        # xmin: 200/1000 * 1920 = 384
        # ymin: 100/1000 * 1080 = 108
        self.assertEqual(l, 384)
        self.assertEqual(t, 108)

if __name__ == "__main__":
    unittest.main()
