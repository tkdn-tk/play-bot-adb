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
    print("--- Testing 'Close X' Button Detection ---")
    
    config = load_config()
    
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
        
    print("Screen captured successfully!")
    
    templates_to_test = [
        "popups/close_x",
        "popups/close_x_small"
    ]
    
    found_any = False
    
    for template_path in templates_to_test:
        print(f"\n--- Analyzing for {template_path} ---")
        template_data = detector.load_template(template_path)
        if template_data is None:
            print(f"[ERROR] Could not load template: {template_path}.png")
            continue
            
        template, w, h = template_data
        
        res = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        
        print(f"Max Confidence: {max_val:.4f}")
        
        center_x = max_loc[0] + w // 2
        center_y = max_loc[1] + h // 2
        
        if max_val >= 0.8:
            print("[SUCCESS] Found with confidence >= 0.8.")
        elif max_val >= 0.6:
            print("[SUCCESS] Found with confidence >= 0.6 (Current config threshold).")
        elif max_val >= 0.4:
            print("[WARNING] Visible but confidence is very low. Needs re-crop.")
        else:
            print("[FAIL] Confidence is extremely low.")
            
        # Draw on the image for the popup
        if max_val >= 0.4:
            found_any = True
            cv2.circle(img, (center_x, center_y), 5, (0, 0, 255), -1) 
            cv2.rectangle(img, max_loc, (max_loc[0] + w, max_loc[1] + h), (0, 255, 0), 2)
            cv2.putText(img, f"{template_path.split('/')[-1]}: {max_val:.2f}", (max_loc[0], max_loc[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            # Optional: attempt to move the physical mouse if found
            try:
                import win32gui
                import win32api
                
                window_title = config.get("emulator_window_title", "")
                hwnd = win32gui.FindWindow(None, window_title)
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
                    scale_x = win_w / max(1, target_w)
                    scale_y = win_h / max(1, target_h)
                    
                    screen_x = int(left + (center_x * scale_x))
                    screen_y = int(top + 35 + (center_y * scale_y))
                    
                    win32api.SetCursorPos((screen_x, screen_y))
                    print(f"-> Moved physical mouse to: ({screen_x}, {screen_y})")
            except Exception as e:
                pass

    if found_any:
        print("\n-> Showing visual popup... (Press any key on the image window to close it)")
        cv2.imshow("Detected Close Buttons - Press any key to close", img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        print("\n-> Did not find any buttons with high enough confidence to display.")

if __name__ == "__main__":
    main()
