"""
AI Harness RVA (Remote Visual Automation) Package
"""
from .vision_harness import VisionHarness, ScreenRegion, Monitor
from .vision_client import RVAVisionClient
from .control_plane import VisionControlServer, VisionControlClient
from .rva_engine import RVAEngine
from .gui_control import PywinautoController
from .pyrefly_service import PyReflyService

__version__ = "1.0.0"
__all__ = [
    "VisionHarness",
    "ScreenRegion",
    "Monitor",
    "RVAVisionClient",
    "VisionControlServer",
    "VisionControlClient",
    "RVAEngine",
    "PywinautoController",
    "PyReflyService",
]
