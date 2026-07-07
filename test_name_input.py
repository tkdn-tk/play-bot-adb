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
    print("--- Testing Name Input Detection ---")
    
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
        "buttons/name_input_field",
        "buttons/confirm_name"
    ]
    
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
            print("[SUCCESS] Found with confidence >= 0.8 (original threshold).")
        elif max_val >= 0.7:
            print("[SUCCESS] Found with confidence >= 0.7 (but lower than default 0.8).")
        elif max_val >= 0.5:
            print("[WARNING] Visible but confidence is too low. Needs re-crop or lower threshold.")
        else:
            print("[FAIL] Confidence is very low.")
            
        # Draw on the image for the popup
        if max_val >= 0.5:
            cv2.circle(img, (center_x, center_y), 5, (0, 0, 255), -1) 
            cv2.rectangle(img, max_loc, (max_loc[0] + w, max_loc[1] + h), (0, 255, 0), 2)
            cv2.putText(img, f"{template_path.split('/')[-1]}: {max_val:.2f}", (max_loc[0], max_loc[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    print("\n-> Showing visual popup for both... (Press any key on the image window to close it)")
    cv2.imshow("Detected Locations - Press any key to close", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
