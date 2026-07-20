import sys
import os
import cv2
import numpy as np
import yaml

# Add parent directory to path so we can import core
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.bot import AutoPlayBot

def load_config(path="config.yaml"):
    try:
        with open(path, "r") as f:
            return yaml.safe_load(f) or {}
    except Exception as e:
        print(f"Failed to load config: {e}")
        return {}

def find_all_matches(screen, template, threshold=0.7):
    """Find all matches of a template on the screen, returning a list of (cx, cy, conf)."""
    h, w = template.shape[:2]
    res = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
    
    # Get all locations above threshold
    loc = np.where(res >= threshold)
    
    matches = []
    # loc[::-1] swaps (y, x) to (x, y)
    for pt in zip(*loc[::-1]):
        conf = res[pt[1], pt[0]]
        cx = pt[0] + w // 2
        cy = pt[1] + h // 2
        
        # Simple Non-Maximum Suppression (ignore if too close to an existing match)
        is_duplicate = False
        for mx, my, mconf in matches:
            # If distance is less than half the template width/height, consider it the same object
            if abs(mx - cx) < w // 2 and abs(my - cy) < h // 2:
                is_duplicate = True
                break
        
        if not is_duplicate:
            matches.append((cx, cy, conf))
            
    return matches, w, h

def main():
    if len(sys.argv) > 1:
        template_name = sys.argv[1]
    else:
        template_name = input("Enter template name (or 'all' for all templates): ")

    if not template_name:
        print("Template name cannot be empty.")
        return

    # Load config and initialize bot
    config = load_config("config.yaml")
    bot = AutoPlayBot(config)

    print(f"Capturing screen...")
    screen = bot.detector.screen_capture.capture()
    if screen is None:
        print("Failed to capture screen. Is the emulator running and connected?")
        return

    templates_to_check = []
    if template_name.lower() == 'all':
        print("Scanning for ALL templates in the 'templates' folder...")
        template_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "templates")
        if os.path.exists(template_dir):
            for f in os.listdir(template_dir):
                if f.endswith(".png"):
                    templates_to_check.append(f)
    else:
        templates_to_check.append(template_name)

    found_anything = False
    
    for t_name in templates_to_check:
        # We use bot.detector to load the template so it handles paths correctly
        template_data = bot.detector.load_template(t_name)
        if not template_data:
            if template_name.lower() != 'all':
                print(f"Could not load template '{t_name}'.")
            continue
            
        template_img, w, h = template_data
        
        # Find ALL matches for this specific template
        matches, w, h = find_all_matches(screen, template_img, threshold=0.7)
        
        if matches:
            found_anything = True
            for cx, cy, conf in matches:
                print(f"Found '{t_name}'!")
                print(f"  -> Center coordinates: X: {cx}, Y: {cy} (Confidence: {conf:.2f})")
                
                # Calculate top-left and bottom-right corners
                top_left = (int(cx - w/2), int(cy - h/2))
                bottom_right = (int(cx + w/2), int(cy + h/2))
                
                # Draw a thick green rectangle
                cv2.rectangle(screen, top_left, bottom_right, (0, 255, 0), 4)
                
                # Draw a red dot at the center (where the click would happen)
                cv2.circle(screen, (int(cx), int(cy)), 5, (0, 0, 255), -1)
                
                # Add text label above the rectangle
                cv2.putText(screen, f"{os.path.basename(t_name)} ({conf:.2f})", 
                            (top_left[0], max(20, top_left[1] - 10)), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

    if found_anything:
        output_file = "test_result.png"
        cv2.imwrite(output_file, screen)
        print(f"\nSaved visual result to '{output_file}'. Check this image to see exactly where they were found!")
    else:
        print(f"\nCould not find any matches on screen with confidence >= 0.7.")
        output_file = "test_result_failed.png"
        cv2.imwrite(output_file, screen)
        print(f"Saved current screen to '{output_file}' so you can see what the bot was looking at.")

if __name__ == "__main__":
    main()
