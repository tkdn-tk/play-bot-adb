import cv2
import numpy as np
import asyncio
from winsdk.windows.media.ocr import OcrEngine
from winsdk.windows.graphics.imaging import BitmapPixelFormat, SoftwareBitmap
from winsdk.windows.storage.streams import DataWriter
from .logger import logger

class WindowsOCR:
    def __init__(self):
        self.engine = OcrEngine.try_create_from_user_profile_languages()
        if not self.engine:
            logger.error("Failed to initialize Windows built-in OCR. Are languages installed?")
            
    async def _recognize_async(self, image_np):
        if not self.engine or image_np is None:
            return ""
            
        try:
            # Convert BGR (OpenCV) to RGBA (Windows API)
            img_rgba = cv2.cvtColor(image_np, cv2.COLOR_BGR2RGBA)
            h, w, _ = img_rgba.shape
            
            # Write pixels to a DataWriter
            writer = DataWriter()
            # tobytes() is fast and flattens the array
            writer.write_bytes(img_rgba.tobytes())
            buffer = writer.detach_buffer()
            
            # Create SoftwareBitmap from buffer
            bmp = SoftwareBitmap.create_copy_from_buffer(buffer, BitmapPixelFormat.RGBA8, w, h)
            
            # Run OCR engine
            result = await self.engine.recognize_async(bmp)
            return result.text
        except Exception as e:
            logger.error(f"OCR Error: {e}")
            return ""

    def recognize(self, image_np):
        """
        Takes an OpenCV BGR image and returns recognized text as a single lowercase string.
        Synchronous wrapper around the async Windows API.
        """
        try:
            # Run async function in a new event loop
            text = asyncio.run(self._recognize_async(image_np))
            # Return lowercase for easier partial string matching
            return text.lower()
        except Exception as e:
            logger.error(f"Failed to run OCR: {e}")
            return ""
