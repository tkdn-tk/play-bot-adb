import os
import sys
import yaml
from main import load_config, interactive_select_mumu
from core.screen import ScreenCapture
from core.detector import Detector
from core.adb_resolver import resolve_adb_serial

def main():
    print("--- Template Detection Tester ---")
    config = load_config("config.yaml")
    
    # Prompt for Mumu instance
    selected_title = interactive_select_mumu()
    if selected_title:
        config["emulator_window_title"] = selected_title
    else:
        print("No Mumu instance found or selected. Exiting.")
        return
        
    # Setup ADB
    resolved_serial = resolve_adb_serial(config)
    if "adb" not in config:
        config["adb"] = {}
    config["adb"]["serial"] = resolved_serial
    
    # Initialize components
    screen = ScreenCapture(config)
    if not screen.find_window():
        print("Could not connect to ADB.")
        return
        
    detector = Detector(config)
    default_thresh = detector.threshold
    
    print("\nTaking screenshot from ADB...")
    img = screen.capture()
    if img is None:
        print("Failed to capture screen.")
        return
        
    print(f"Screenshot captured (shape: {img.shape}).")
    print(f"Checking all PNG templates in 'templates/' folder against this screenshot...\n")
    print(f"Default Confidence Threshold: {default_thresh}\n")
    
    templates_dir = "templates"
    if not os.path.exists(templates_dir):
        print(f"Directory {templates_dir} does not exist.")
        return
        
    found_count = 0
    files_checked = 0
    
    # Loop through all files in templates directory
    for root, _, files in os.walk(templates_dir):
        for file in files:
            if not file.endswith(".png"):
                continue
                
            files_checked += 1
            # Get relative path like "buttons/play.png" or "main_menu.png"
            rel_path = os.path.relpath(os.path.join(root, file), templates_dir)
            
            # Use a low threshold so we can see the confidence score even if it fails
            result = detector.find(rel_path, screen_img=img, threshold=0.3)
            
            if result:
                x, y, conf = result
                if conf >= default_thresh:
                    print(f"[ MATCHED ] {rel_path} - Conf: {conf:.2f} at ({x}, {y})")
                    found_count += 1
                else:
                    print(f"[LOW CONF ] {rel_path} - Conf: {conf:.2f} at ({x}, {y})")
            else:
                print(f"[NO MATCH ] {rel_path} - Conf: <0.30")
                
    print(f"\n--- Summary ---")
    print(f"Templates checked: {files_checked}")
    print(f"Successful matches (>= {default_thresh}): {found_count}")

if __name__ == "__main__":
    main()
