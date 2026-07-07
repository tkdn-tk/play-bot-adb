import sys
import yaml
import time
from core.logger import logger
from core.screen import ScreenCapture
from core.detector import Detector
from core.adb_resolver import resolve_adb_serial
import cv2

def load_config(config_path="config.yaml"):
    try:
        with open(config_path, "r") as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        sys.exit(1)

def main():
    print("--- Testing Tutorial Confirm Button Detection ---")
    
    config = load_config()
    
    # Setup ADB similar to how bot.py does it
    resolved_serial = resolve_adb_serial(config)
    if "adb" not in config:
        config["adb"] = {}
    config["adb"]["serial"] = resolved_serial
    
    logger.set_config(config)
    
    screen = ScreenCapture(config)
    detector = Detector(config)
    
    print("Connecting to emulator...")
    if not screen.find_window():
        print("[ERROR] Could not connect to emulator window/ADB.")
        sys.exit(1)
        
    print("Capturing screen...")
    img = screen.capture()
    if img is None:
        print("[ERROR] Failed to capture screen.")
        sys.exit(1)
        
    print("Screen captured successfully! Analyzing for tutorial_confirm...")
    
    template_path = "buttons/tutorial_confirm"
    
    # Load the template using the detector
    template_data = detector.load_template(template_path)
    if template_data is None:
        print(f"[ERROR] Could not load template: {template_path}")
        sys.exit(1)
        
    template, w, h = template_data
    
    # Perform template matching directly to print exact confidence scores
    res = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    
    print("\n=== RESULTS ===")
    print(f"Max Confidence (0.0 to 1.0): {max_val:.4f}")
    
    center_x = max_loc[0] + w // 2
    center_y = max_loc[1] + h // 2
    print(f"Location Found At (Internal ADB Coords): x={center_x}, y={center_y}")
    
    if max_val >= 0.8:
        print("\n[SUCCESS] The button was found with confidence >= 0.8 (original threshold).")
    elif max_val >= 0.7:
        print("\n[SUCCESS] The button was found with confidence >= 0.7 (new updated threshold).")
    elif max_val >= 0.5:
        print("\n[WARNING] The button is visible but the confidence is too low. You should recrop the image.")
    else:
        print("\n[FAIL] Confidence is very low. The button is either not on screen, or the template is completely wrong.")

    # 1. Attempt to move the physical mouse
    try:
        import win32gui
        import win32api
        
        window_title = config.get("emulator_window_title", "")
        hwnd = win32gui.FindWindow(None, window_title)
        
        # If not found directly, try partial match
        if not hwnd and window_title:
            def callback(h, extra):
                if win32gui.IsWindowVisible(h) and window_title.lower() in win32gui.GetWindowText(h).lower():
                    extra.append(h)
            hwnds = []
            win32gui.EnumWindows(callback, hwnds)
            if hwnds:
                hwnd = hwnds[0]
                
        if hwnd:
            left, top, right, bottom = win32gui.GetWindowRect(hwnd)
            win_w = right - left
            win_h = bottom - top
            
            target_w = config.get("resolution", {}).get("width", 1280)
            target_h = config.get("resolution", {}).get("height", 720)
            
            # Rough scaling in case window is resized
            scale_x = win_w / max(1, target_w)
            scale_y = win_h / max(1, target_h)
            
            # Add ~35px offset for the title bar of the emulator window
            screen_x = int(left + (center_x * scale_x))
            screen_y = int(top + 35 + (center_y * scale_y))
            
            win32api.SetCursorPos((screen_x, screen_y))
            print(f"-> Moved physical mouse to approximate desktop coordinates: ({screen_x}, {screen_y})")
        else:
            print("-> Could not find emulator window to move the mouse.")
    except Exception as e:
        print("-> Failed to move mouse:", e)

    # 2. Show the image visually so you can confirm exactly what OpenCV sees
    print("-> Showing visual popup... (Press any key on the image window to close it)")
    cv2.circle(img, (center_x, center_y), 5, (0, 0, 255), -1) # Red dot at center
    cv2.rectangle(img, max_loc, (max_loc[0] + w, max_loc[1] + h), (0, 255, 0), 2) # Green box around template
    
    cv2.imshow("Detected Location - Press any key to close", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
