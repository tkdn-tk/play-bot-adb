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
            
            # Verify connection is working
            try:
                # If device is offline or not found, this will raise an error
                self.device.shell("echo 1")
            except Exception as e:
                logger.warning(f"ADB device {self.serial} unresponsive ({e}), reconnecting...")
                try:
                    self.adb.disconnect(self.serial)
                except Exception:
                    pass
                self.adb.connect(self.serial)
                self.device = self.adb.device(serial=self.serial)
                # Test again; if it fails, it will drop to the outer except block
                self.device.shell("echo 1")
                
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
        if hasattr(self, 'bot'):
            self.bot.wait_if_paused()
            if not getattr(self.bot, 'running', True):
                raise Exception("Bot stopped by user.")
                
        if not self.device:
            if not self.find_window():
                return None
                
        try:
            # Capture using adb exec-out screencap -p
            import subprocess
            import adbutils
            
            try:
                adb = adbutils.adb_path()
            except (ImportError, AttributeError):
                # Fallback if adbutils.adb_path() is removed or broken in this version
                if hasattr(adbutils.adb, 'path'):
                    adb = adbutils.adb.path
                else:
                    adb = "adb"
                    
            png_bytes = subprocess.check_output(
                [adb, "-s", self.serial, "exec-out", "screencap", "-p"],
                stderr=subprocess.STDOUT
            )
            
            if not png_bytes or not png_bytes.startswith(b'\x89PNG'):
                logger.error("Empty or invalid screenshot received from ADB")
                return None
                
            # Decode the PNG bytes into a numpy array (BGR format for OpenCV)
            img_np = np.frombuffer(png_bytes, np.uint8)
            img_bgr = cv2.imdecode(img_np, cv2.IMREAD_COLOR)
            
            if img_bgr is None:
                logger.error("Failed to decode screenshot")
                return None
            
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

