import os
import sys
import yaml
from main import load_config, interactive_select_mumu
from core.screen import ScreenCapture
from core.detector import Detector
from core.clicker import Clicker
from core.adb_resolver import resolve_adb_serial
import time

def main():
    print("--- Play Record Tester ---")
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
    
    # We need a dummy bot object to initialize the clicker
    class DummyBot:
        pass
    
    bot = DummyBot()
    bot.screen = screen
    bot.detector = detector
    bot.config = config
    bot.clicker = Clicker(config=config)
    
    print("\nLooking for 'play_record.png' on your Windows Desktop and attempting to click it...")
    
    # Try to click it!
    import pyautogui
    try:
        center = pyautogui.locateCenterOnScreen("templates/play_record.png", confidence=0.8)
        if center:
            pyautogui.click(center.x, center.y)
            print("\n✅ SUCCESS! Successfully found and clicked the play record button.")
            print("Your macro should have just started running in the emulator.")
        else:
            print("\n❌ FAILURE! Could not find 'play_record.png' on your Windows desktop.")
            print("Make sure the Operation Recorder menu is open, visible on your actual monitor screen, and not covered by other windows.")
    except Exception as e:
        print(f"\n❌ ERROR during desktop search: {e}")

if __name__ == "__main__":
    main()
