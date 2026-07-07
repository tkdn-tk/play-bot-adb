import time
import numpy as np
import cv2
import adbutils
from .logger import logger

class ScreenCapture:
    def __init__(self, config=None):
        self.config = config or {}
        self.target_width = self.config.get("resolution", {}).get("width", 1280)
        self.target_height = self.config.get("resolution", {}).get("height", 720)
        
        adb_config = self.config.get("adb", {})
        self.serial = adb_config.get("serial", "127.0.0.1:7555")
        
        self.adb = adbutils.AdbClient(host="127.0.0.1", port=5037)
        self.device = None
        self.native_width = None
        self.native_height = None
        
    def find_window(self):
        """Connect to the emulator via ADB."""
        try:
            # Try to connect, if it's already connected it will be a no-op
            self.adb.connect(self.serial)
            self.device = self.adb.device(serial=self.serial)
            logger.info(f"Connected to ADB device: {self.serial}")
            return True
        except Exception as e:
            logger.error(f"Could not connect to ADB device {self.serial}: {e}")
            return False
            
    def adjust_window(self):
        """No-op for ADB (we don't need to resize physical windows)."""
        pass
        
    def get_window_rect(self):
        """Return the logical screen rectangle for ADB."""
        if not self.device:
            if not self.find_window():
                return None
        return {"left": 0, "top": 0, "width": self.target_width, "height": self.target_height}
        
    def capture(self, return_rgb=False):
        """Capture the emulator screen via ADB and return as numpy array (BGR by default)."""
        if not self.device:
            if not self.find_window():
                return None
                
        try:
            # Capture using adbutils
            pil_img = self.device.screenshot()
            
            # Convert to numpy array (RGB format from PIL)
            img_np = np.array(pil_img)
            
            # Check if image is valid
            if img_np.size == 0:
                logger.error("Empty screenshot received from ADB")
                return None
                
            # PIL returns RGB, we need to convert to BGR for OpenCV
            img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
            
            # Verify resolution matches config, if not, warn or resize
            h, w = img_bgr.shape[:2]
            self.native_width = w
            self.native_height = h
            if w != self.target_width or h != self.target_height:
                # Use debug or trace to avoid spamming the log on every frame
                # logger.debug(f"ADB screenshot is {w}x{h}, config expects {self.target_width}x{self.target_height}. Resizing.")
                img_bgr = cv2.resize(img_bgr, (self.target_width, self.target_height))
            
            if return_rgb:
                return cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
                
            return img_bgr
        except Exception as e:
            logger.error(f"Failed to capture screen via ADB: {e}")
            # Reset device so it tries to reconnect next time
            self.device = None
            return None

    def save_screenshot(self, filepath):
        """Save a screenshot of the emulator to disk."""
        img = self.capture()
        if img is not None:
            cv2.imwrite(filepath, img)
            logger.info(f"Saved screenshot to {filepath}")
            return True
        return False

