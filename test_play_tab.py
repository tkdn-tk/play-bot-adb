import os
import sys
import yaml
from main import load_config, interactive_select_mumu
from core.screen import ScreenCapture
from core.detector import Detector
from core.clicker import Clicker
from core.adb_resolver import resolve_adb_serial
from steps.autoplay import execute_prepare_play
from core.bot import State
import time

def main():
    print("--- Play Tab Alternate Variants Tester ---")
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
    
    # We need a dummy bot object to pass to execute_prepare_play
    class DummyBot:
        pass
    
    bot = DummyBot()
    bot.screen = screen
    
    detector.screen_capture = screen
    bot.detector = detector
    
    bot.config = config
    
    bot.clicker = Clicker(config=config)
    bot.clicker.screen_capture = screen
    bot.clicker.detector = detector
    
    bot.running = True
    
    print("\nExecuting 'execute_prepare_play' to test for alternate variants...")
    print("Make sure you are on the screen with the play tab visible.")
    
    result = execute_prepare_play(bot)
    
    if result == State.BUY_BUFFS:
        print("\n✅ SUCCESS! Successfully found and clicked a play tab variant.")
        print(f"Function returned: {result}")
    else:
        print("\n❌ FAILURE! Could not find any play tab variants within the timeout.")
        print(f"Function returned: {result}")

if __name__ == "__main__":
    main()
