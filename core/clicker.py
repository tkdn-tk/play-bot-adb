import random
import time
import adbutils
from .logger import logger
from .screen import ScreenCapture
from .detector import Detector

class Clicker:
    def __init__(self, config=None):
        self.config = config or {}
        delays = self.config.get("delays", {})
        self.click_min = delays.get("click_min", 0.5)
        self.click_max = delays.get("click_max", 2.0)
        
        self.screen_capture = ScreenCapture(config=self.config)
        self.detector = Detector(config=self.config)
        
        adb_config = self.config.get("adb", {})
        self.serial = adb_config.get("serial", "127.0.0.1:7555")
        self.adb = adbutils.AdbClient(host="127.0.0.1", port=5037)
        self.device = None
        
    def _connect(self):
        if not self.device:
            try:
                self.adb.connect(self.serial)
                self.device = self.adb.device(serial=self.serial)
            except Exception as e:
                logger.error(f"Clicker failed to connect to ADB: {e}")
                
    def random_delay(self):
        """Sleep for a random amount of time based on config."""
        delay = random.uniform(self.click_min, self.click_max)
        time.sleep(delay)
        
    def click(self, x, y, offset_range=5, button="left"):
        """Click at absolute screen coordinates with random offset."""
        self._connect()
        
        # Add random offset to simulate human clicking slightly off-center
        offset_x = random.randint(-offset_range, offset_range)
        offset_y = random.randint(-offset_range, offset_range)
        
        target_x = x + offset_x
        target_y = y + offset_y
        
        # Scale back to native resolution if needed
        sc = self.detector.screen_capture
        if sc.native_width and sc.native_height and sc.target_width and sc.target_height:
            scale_x = sc.native_width / sc.target_width
            scale_y = sc.native_height / sc.target_height
            if scale_x != 1.0 or scale_y != 1.0:
                target_x = int(target_x * scale_x)
                target_y = int(target_y * scale_y)
        
        logger.debug(f"Clicking at ({target_x}, {target_y})")
        if self.device:
            try:
                self.device.click(target_x, target_y)
            except Exception as e:
                logger.error(f"ADB click failed, resetting device: {e}")
                self.device = None
        self.random_delay()
        
    def click_window_relative(self, rel_x, rel_y, offset_range=5):
        """Click at coordinates relative to the emulator window. With ADB, this is the same as absolute."""
        self.click(rel_x, rel_y, offset_range)
        return True

    def click_template(self, template_path, timeout=5.0, threshold=None, offset_range=5):
        """Find a template and click its center."""
        result = self.detector.wait_for(template_path, timeout=timeout, threshold=threshold)
        if result:
            rel_x, rel_y, confidence = result
            logger.info(f"Found {template_path} (conf={confidence:.2f}), clicking...")
            return self.click_window_relative(rel_x, rel_y, offset_range)
        else:
            logger.error(f"Cannot click: template {template_path} not found")
            return False

    def type_text(self, text):
        """Type text using ADB."""
        logger.info(f"Typing text: {text}")
        self._connect()
        if self.device:
            # ADB shell input text doesn't like spaces unless quoted or %s
            escaped_text = text.replace(" ", "%s")
            try:
                self.device.shell(["input", "text", escaped_text])
            except Exception as e:
                logger.error(f"ADB type_text failed, resetting device: {e}")
                self.device = None
        self.random_delay()

    def press_key(self, key):
        """Press a specific keyboard key using ADB keyevents."""
        self._connect()
        logger.debug(f"Pressing key: {key} (via adb)")
        key_map = {
            "enter": 66,
            "backspace": 67,
            "esc": 111,
            "escape": 111,
            "tab": 61,
            "home": 3,
            "back": 4
        }
        
        keycode = key_map.get(key.lower())
        if keycode and self.device:
            try:
                self.device.keyevent(keycode)
            except Exception as e:
                logger.error(f"ADB keyevent failed, resetting device: {e}")
                self.device = None
        else:
            logger.warning(f"Unknown key '{key}' or device not connected.")
            
        time.sleep(random.uniform(0.1, 0.3))
