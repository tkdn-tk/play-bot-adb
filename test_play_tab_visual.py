import os
import sys
import yaml
import time
import cv2
from main import load_config, interactive_select_mumu
from core.screen import ScreenCapture
from core.detector import Detector
from core.adb_resolver import resolve_adb_serial

def main():
    print("--- Visual Play Tab Variants Tester ---")
    config = load_config("config.yaml")
    
    selected_title = interactive_select_mumu()
    if selected_title:
        config["emulator_window_title"] = selected_title
    else:
        print("No Mumu instance found or selected. Exiting.")
        return
        
    resolved_serial = resolve_adb_serial(config)
    if "adb" not in config:
        config["adb"] = {}
    config["adb"]["serial"] = resolved_serial
    
    screen = ScreenCapture(config)
    if not screen.find_window():
        print("Could not connect to ADB.")
        return
        
    detector = Detector(config)
    
    print("\nCapturing screen...")
    img = screen.capture()
    if img is None:
        print("Failed to capture screen.")
        return
        
    play_tabs = [f for f in os.listdir("templates") if f.startswith("play_tab") and f.endswith(".png")]
    
    best_match = None
    all_matches = []
    
    print("\nAnalyzing variants:")
    for tab in play_tabs:
        template_data = detector.load_template(tab)
        if not template_data:
            continue
        _, w, h = template_data
        
        result = detector.find(tab, screen_img=img, threshold=0.8)
        if result:
            cx, cy, conf = result
            print(f"[{tab}] Found with confidence {conf:.4f} at ({cx}, {cy})")
            
            match_data = {
                'tab': tab,
                'x': cx,
                'y': cy,
                'w': w,
                'h': h,
                'conf': conf
            }
            all_matches.append(match_data)
            
            if best_match is None or conf > best_match['conf']:
                best_match = match_data
        else:
            print(f"[{tab}] Not found (confidence < 0.8)")
            
    if all_matches:
        print(f"\n✅ BEST MATCH: {best_match['tab']} with {best_match['conf']:.4f} confidence!")
        print(f"The bot would click at ({best_match['x']}, {best_match['y']})")
        
        # Draw all other matches in gray/red
        for match in all_matches:
            if match['tab'] != best_match['tab']:
                cx, cy = match['x'], match['y']
                w, h = match['w'], match['h']
                top_left = (cx - w // 2, cy - h // 2)
                bottom_right = (top_left[0] + w, top_left[1] + h)
                
                # Gray bounding box for ignored variants
                cv2.rectangle(img, top_left, bottom_right, (100, 100, 100), 2)
                text = f"IGNORED: {match['tab']} ({match['conf']:.2f})"
                cv2.putText(img, text, (top_left[0], top_left[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 100, 100), 2)
        
        # Draw best match in green
        cx, cy = best_match['x'], best_match['y']
        w, h = best_match['w'], best_match['h']
        top_left = (cx - w // 2, cy - h // 2)
        bottom_right = (top_left[0] + w, top_left[1] + h)
        
        # Draw red dot where the bot will click
        cv2.circle(img, (cx, cy), 6, (0, 0, 255), -1) 
        # Draw green bounding box around the template
        cv2.rectangle(img, top_left, bottom_right, (0, 255, 0), 2)
        text = f"BEST: {best_match['tab']} ({best_match['conf']:.2f})"
        cv2.putText(img, text, (top_left[0], top_left[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        print("\n-> Showing visual popup... (Press any key on the image window to close it)")
        cv2.imshow("Detected Play Tab - Press any key to close", img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        print("\n❌ No play_tab variants found with >= 0.8 confidence.")

if __name__ == "__main__":
    main()
