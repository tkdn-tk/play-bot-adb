import sys
import os
import cv2

# Ensure parent directory is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.screen import ScreenCapture
from core.ocr import WindowsOCR

def test_ocr():
    print("--- Testing Windows Built-in OCR ---")
    screen = ScreenCapture(window_title="Non-Root")
    
    if not screen.find_window():
        print("Error: Could not find emulator window.")
        return
        
    print("Capturing emulator screen...")
    img = screen.capture()
    if img is None:
        print("Failed to capture screen.")
        return
        
    print("Running OCR...")
    ocr = WindowsOCR()
    text = ocr.recognize(img)
    
    print("\n=== RAW OCR TEXT FOUND ===")
    print(text)
    print("==========================")
    
    clean_lower = text.replace('\n', ' | ').strip().lower()
    import re
    
    # Try Treasure parse
    treasure_match = re.search(r"treasure received!\s*(.*?)\s*[\*•]", clean_lower)
    if treasure_match:
        print(f"\n[PARSED TREASURE] {treasure_match.group(1).strip().title()}")
        
    # Try Pet parse
    pet_match = re.search(r"!\s*(.*?)\s*(?:hatched|!)", clean_lower)
    if pet_match:
        print(f"\n[PARSED PET] {pet_match.group(1).strip().title()}")
    
    # Show the captured image to confirm what it saw
    cv2.imshow("Captured Image for OCR", img)
    print("\nPress any key in the image window to close...")
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    test_ocr()
