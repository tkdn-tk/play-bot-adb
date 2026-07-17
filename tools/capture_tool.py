import cv2
import os
import sys
import time

# Ensure parent directory is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.screen import ScreenCapture

REQUIRED_TEMPLATES = [
    # Login & Tutorial
    {"cat": "buttons", "name": "guest_login", "desc": "The Guest Login button on the title screen"},
    {"cat": "buttons", "name": "confirm_login", "desc": "The confirmation popup after clicking guest login (if any)"},
    {"cat": "buttons", "name": "play", "desc": "The main Play/Tap to Start button"},
    {"cat": "buttons", "name": "tutorial_confirm", "desc": "The button to start/confirm the tutorial"},
    {"cat": "buttons", "name": "settings", "desc": "The gear/settings icon at the top right"},
    {"cat": "buttons", "name": "quit_tutorial", "desc": "The quit/skip tutorial button inside settings"},
    {"cat": "buttons", "name": "confirm_quit_tutorial", "desc": "The confirmation to quit the tutorial"},
    
    # Setup & Popups
    {"cat": "buttons", "name": "name_input_field", "desc": "The text box where you type your nickname"},
    {"cat": "buttons", "name": "confirm_name", "desc": "The OK/Confirm button after typing your name"},
    {"cat": "popups", "name": "close_x", "desc": "The red X button on daily rewards/notifications"},
    {"cat": "popups", "name": "close_x_small", "desc": "Alternative smaller red X button on some notifications"},
    {"cat": "popups", "name": "ok_button", "desc": "A generic OK button on notifications"},
    {"cat": "popups", "name": "claim_reward", "desc": "A generic Claim button on notifications"},
    
    # Mailbox
    {"cat": "buttons", "name": "mailbox", "desc": "The envelope/mailbox icon on the main screen"},
    {"cat": "buttons", "name": "mailbox_reward_tab", "desc": "The 'Reward' tab inside the mailbox"},
    {"cat": "buttons", "name": "claim_all", "desc": "The 'Claim All' button inside the mailbox"},
    {"cat": "buttons", "name": "mailbox_close", "desc": "The Close button specifically for the mailbox window"},
    
    # Draws
    {"cat": "buttons", "name": "draw_menu", "desc": "The Gacha/Draw menu button on the main screen"},
    {"cat": "buttons", "name": "tab_treasure", "desc": "The Treasure tab at the top of the draw menu"},
    {"cat": "draw", "name": "treasure_draw_btn", "desc": "The 1x Free Draw button for regular treasures"},
    {"cat": "results", "name": "treasure_result_bg", "desc": "Any unique text/background that appears only on the treasure result screen"},
    {"cat": "buttons", "name": "confirm_draw", "desc": "The OK/Confirm button to exit the draw result screen"},
    
    {"cat": "buttons", "name": "tab_special_treasure", "desc": "The Special Treasure tab"},
    {"cat": "draw", "name": "special_draw_btn", "desc": "The 1x Free Draw button for special treasures"},
    {"cat": "results", "name": "special_result_bg", "desc": "Unique text/background on the special treasure result screen"},
    {"cat": "buttons", "name": "special_treasure_close_alt", "desc": "An alternate close button that appears after special treasure draws"},
    {"cat": "buttons", "name": "special_treasure_close_small", "desc": "The secondary smaller close button that appears after closing special treasure"},
    {"cat": "buttons", "name": "close_x_treasure_tab", "desc": "The close button specifically for the treasure tab"},
    
    {"cat": "buttons", "name": "tab_pet", "desc": "The Pet tab"},
    {"cat": "draw", "name": "pet_hatch_btn", "desc": "The Hatch button that appears before the pet draw button"},
    {"cat": "draw", "name": "pet_draw_btn", "desc": "The 1x Free Draw button for pets"},
    {"cat": "results", "name": "pet_result_bg", "desc": "Unique text/background on the pet result screen"},
    {"cat": "buttons", "name": "pet_close_x_btn", "desc": "The X button to close the pet draw result screen"},
    {"cat": "buttons", "name": "close_hatch_tab", "desc": "The close button specifically for the pet hatch menu popup"},
    {"cat": "buttons", "name": "close_x_pet_tab", "desc": "The close button specifically for the pet tab"},
    
    # Delete Account
    {"cat": "buttons", "name": "tab_game_info", "desc": "The 'Game Info' tab inside settings"},
    {"cat": "buttons", "name": "delete_account", "desc": "The 'Delete Account' button"},
    {"cat": "buttons", "name": "confirm_delete_active", "desc": "The final Confirm button (after the 60s wait)"},
    {"cat": "buttons", "name": "confirm_restart", "desc": "The button to restart the game after deletion"}
]

class CaptureTool:
    def __init__(self, config=None):
        self.config = config or {}
        self.screen = ScreenCapture(config=self.config)
        self.drawing = False
        self.ix, self.iy = -1, -1
        self.rect = None
        self.img_copy = None
        self.current_guide = None

    def draw_rect(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.drawing = True
            self.ix, self.iy = x, y
            self.rect = None

        elif event == cv2.EVENT_MOUSEMOVE:
            if self.drawing:
                img_temp = self.img_copy.copy()
                cv2.rectangle(img_temp, (self.ix, self.iy), (x, y), (0, 255, 0), 1)
                cv2.imshow("Capture", img_temp)

        elif event == cv2.EVENT_LBUTTONUP:
            self.drawing = False
            self.rect = (min(self.ix, x), min(self.iy, y), abs(x - self.ix), abs(y - self.iy))
            img_temp = self.img_copy.copy()
            cv2.rectangle(img_temp, (self.ix, self.iy), (x, y), (0, 255, 0), 2)
            cv2.imshow("Capture", img_temp)

    def run(self):
        print("\n--- Cookie Run Template Capture Tool ---")
        if not self.screen.find_window():
            print("Error: Could not find emulator window.")
            return

        print("\nModes:")
        print("1. Guided Mode (Walks you through all required templates)")
        print("2. Free Mode (Capture whatever you want)")
        choice = input("Select mode (1 or 2): ").strip()
        
        if choice == "1":
            self.run_guided_mode()
        else:
            self.run_free_mode()

    def run_guided_mode(self):
        print("\nStarting Guided Mode. Press 'S' in the capture window to Skip a template if you already have it.")
        
        for item in REQUIRED_TEMPLATES:
            # Check if file already exists
            filepath = os.path.join("templates", item["cat"], f"{item['name']}.png")
            if os.path.exists(filepath):
                print(f"\n[SKIP] '{item['name']}' already exists.")
                time.sleep(0.5)
                continue
                
            print(f"\n========================================")
            print(f"NOW CAPTURING: {item['cat']}/{item['name']}")
            print(f"DESCRIPTION: {item['desc']}")
            print(f"========================================")
            print("Set up your game screen to show this element, then press ENTER in this terminal to take a screenshot.")
            input("Press ENTER when ready...")
            
            success = self._do_capture(item['name'], item['cat'])
            if not success:
                print("Skipped or cancelled.")

    def run_free_mode(self):
        while True:
            print("\nCapturing emulator window...")
            success = self._do_capture()
            if not success:
                break

    def _do_capture(self, auto_name=None, auto_cat=None):
        img = self.screen.capture()
        if img is None:
            print("Failed to capture screen.")
            return False

        self.img_copy = img.copy()
        
        title = "Capture (ENTER=save, R=retake, S=skip/cancel)"
        if auto_name:
            title = f"Capturing: {auto_name} (ENTER=save, R=retake, S=skip)"
            
        cv2.namedWindow("Capture")
        cv2.setWindowTitle("Capture", title)
        cv2.setMouseCallback("Capture", self.draw_rect)

        saved = False
        while True:
            cv2.imshow("Capture", self.img_copy)
            key = cv2.waitKey(1) & 0xFF

            if key == 27 or key == ord('s') or key == ord('S'): # ESC or S
                print("Cancelled/Skipped.")
                cv2.destroyAllWindows()
                return False
                
            elif key == ord('r') or key == ord('R'):
                img = self.screen.capture()
                if img is not None:
                    self.img_copy = img.copy()
                    self.rect = None
                    print("Retook screenshot.")
                    
            elif key == 13 or key == 10: # ENTER
                if self.rect and self.rect[2] > 0 and self.rect[3] > 0:
                    x, y, w, h = self.rect
                    cropped = img[y:y+h, x:x+w]
                    cv2.destroyAllWindows()
                    
                    if auto_name and auto_cat:
                        self._save_direct(cropped, auto_cat, auto_name)
                    else:
                        self._save_dialog(cropped)
                    saved = True
                    break
                else:
                    print("Please draw a rectangle first.")
                    
        cv2.destroyAllWindows()
        return saved

    def _save_direct(self, img, folder, name):
        filepath = os.path.join("templates", folder, f"{name}.png")
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        cv2.imwrite(filepath, img)
        print(f"Saved template to {filepath}")

    def _save_dialog(self, cropped_img):
        cv2.imshow("Cropped", cropped_img)
        cv2.waitKey(500)
        
        print("\nCategories:")
        categories = ["buttons", "popups", "draw", "results", "desired"]
        for i, cat in enumerate(categories):
            print(f"{i+1}. templates/{cat}/")
            
        try:
            choice = int(input("Select category (1-5): ")) - 1
            if 0 <= choice < len(categories):
                folder = categories[choice]
            else:
                folder = "buttons"
        except:
            folder = "buttons"
            
        name = input("Enter template name (without .png): ")
        if not name:
            name = "template"
            
        self._save_direct(cropped_img, folder, name)
        cv2.destroyAllWindows()

if __name__ == "__main__":
    tool = CaptureTool()
    tool.run()
