import sys
import os
import cv2

# Ensure parent directory is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.screen import ScreenCapture
from core.detector import Detector

def test_special():
    print("--- Special Treasure Detection Debug ---")
    
    # Initialize screen and detector
    screen = ScreenCapture(window_title="Non-Root")
    if not screen.find_window():
        print("Error: Could not find emulator window.")
        return
        
    print("Capturing emulator screen...")
    img = screen.capture()
    if img is None:
        print("Failed to capture screen.")
        return
        
    # Initialize detector (using main templates folder)
    detector = Detector(template_dir="templates")
    
    templates_to_check = [
        "buttons/tab_special_treasure",
        "draw/special_draw_btn",
        "draw/special_draw_btn_alt",
        "results/special_result_bg",
        "buttons/confirm_draw",
        "buttons/special_treasure_close_alt",
        "buttons/special_treasure_close_small",
        "buttons/close_x_treasure_tab"
    ]
    
    print("\n--- Detection Results ---")
    for t in templates_to_check:
        # Detector automatically appends .png internally if needed,
        # but let's make sure it's checking exactly the right paths.
        template_path = t if t.endswith(".png") else t + ".png"
        
        result = detector.find(template_path, screen_img=img)
        if result:
            x, y, conf = result
            print(f"[FOUND]  {t:<30} | Confidence: {conf:.2f} | Pos: ({x}, {y})")
        else:
            print(f"[FAILED] {t:<30} | Not found (confidence < {detector.threshold}) or file missing.")
            
    print("-------------------------\n")
    print("If a button is visible on your screen but says FAILED, it means the bot doesn't recognize it.")
    print("You may need to recapture that specific image using: python main.py capture")

if __name__ == "__main__":
    test_special()
