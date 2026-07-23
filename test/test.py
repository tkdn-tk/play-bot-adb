import sys
import os
import cv2
import yaml

# Add the parent directory to sys.path so we can import 'core'
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from core.detector import Detector
from core.logger import logger

def load_config(config_path="config.yaml"):
    try:
        with open(os.path.join(parent_dir, config_path), "r") as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        return {}

def main():
    config = load_config()
    # Initialize Detector (which also initializes ScreenCapture)
    detector = Detector(config=config, template_dir=os.path.join(parent_dir, "templates"))
    
    logger.info("Capturing screen from ADB...")
    screen = detector.screen_capture.capture()
    if screen is None:
        logger.error("Failed to capture screen. Make sure the emulator is running and ADB is connected.")
        return

    # Determine which templates to search for
    templates_to_search = []
    if len(sys.argv) > 1:
        # Search specific template given in arguments
        templates_to_search = [sys.argv[1]]
        logger.info(f"Searching for specific template: {sys.argv[1]}")
    else:
        # Search all templates in the templates directory
        logger.info("No template specified. Searching for ALL templates...")
        template_dir = os.path.join(parent_dir, "templates")
        templates_to_search = [f for f in os.listdir(template_dir) if f.endswith(".png")]

    found_any = False
    # Make a copy of the screen to draw rectangles on
    display_img = screen.copy()

    for template_name in templates_to_search:
        result = detector.find(template_name, screen_img=screen)
        if result:
            center_x, center_y, confidence = result
            logger.info(f"Found {template_name} at ({center_x}, {center_y}) with confidence {confidence:.2f}")
            found_any = True
            
            # Get template width and height to draw the bounding box
            template_data = detector.load_template(template_name)
            if template_data:
                _, w, h = template_data
                top_left = (int(center_x - w/2), int(center_y - h/2))
                bottom_right = (int(center_x + w/2), int(center_y + h/2))
                
                # Draw rectangle (Green)
                cv2.rectangle(display_img, top_left, bottom_right, (0, 255, 0), 2)
                # Put text above the rectangle
                cv2.putText(display_img, f"{template_name} ({confidence:.2f})", (top_left[0], top_left[1] - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

    if not found_any:
        logger.info("No templates found on the screen.")
    
    logger.info("Displaying result. Press any key in the window to close it.")
    cv2.imshow("Detection Result", display_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
