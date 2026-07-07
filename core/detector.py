import cv2
import os
import time
import numpy as np
from .logger import logger
from .screen import ScreenCapture

class Detector:
    def __init__(self, config=None, template_dir="templates", threshold=0.6):
        self.config = config or {}
        self.template_dir = template_dir
        # Read from config if available, otherwise use default
        self.threshold = self.config.get("match_threshold", threshold)
        self.templates = {}
        
        self.screen_capture = ScreenCapture(config=self.config)
        
    def load_template(self, template_path):
        """Load a template image into memory."""
        if template_path in self.templates:
            return self.templates[template_path]
            
        full_path = os.path.join(self.template_dir, template_path)
        if not os.path.exists(full_path):
            if not full_path.endswith(".png"):
                full_path += ".png"
            if not os.path.exists(full_path):
                logger.warning(f"Template not found: {full_path}")
                return None
                
        template = cv2.imread(full_path, cv2.IMREAD_COLOR)
        if template is None:
            logger.error(f"Failed to read template: {full_path}")
            return None
            
        # Store width and height
        h, w = template.shape[:2]
        self.templates[template_path] = (template, w, h)
        return self.templates[template_path]

    def find(self, template_path, screen_img=None, threshold=None):
        """
        Find a template on the screen.
        Returns (center_x, center_y, confidence) or None if not found.
        Coordinates are relative to the screen_img provided (or emulator window).
        """
        if threshold is None:
            threshold = self.threshold
            
        if screen_img is None:
            screen_img = self.screen_capture.capture()
            if screen_img is None:
                return None
                
        template_data = self.load_template(template_path)
        if template_data is None:
            return None
            
        template, w, h = template_data
        
        # Perform template matching
        res = cv2.matchTemplate(screen_img, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        
        if max_val >= threshold:
            # Return center coordinates
            center_x = max_loc[0] + w // 2
            center_y = max_loc[1] + h // 2
            return (center_x, center_y, max_val)
            
        return None

    def wait_for(self, template_path, timeout=30.0, interval=0.5, threshold=None):
        """Wait until a template appears on screen."""
        # Check if the file actually exists first, otherwise we'll wait uselessly
        if self.load_template(template_path) is None:
            logger.error(f"Cannot wait for {template_path} because the file doesn't exist.")
            return None
            
        logger.debug(f"Waiting for {template_path} (timeout={timeout}s)")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            result = self.find(template_path, threshold=threshold)
            if result:
                return result
            time.sleep(interval)
            
        logger.warning(f"Timeout waiting for {template_path}")
        return None

    def wait_for_gone(self, template_path, timeout=30.0, interval=0.5, threshold=None):
        """Wait until a template disappears from screen."""
        if self.load_template(template_path) is None:
            # If the file doesn't exist, it's technically already gone from the screen
            return True
            
        logger.debug(f"Waiting for {template_path} to disappear")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            result = self.find(template_path, threshold=threshold)
            if not result:
                return True
            time.sleep(interval)
            
        logger.warning(f"Timeout waiting for {template_path} to disappear")
        return False
