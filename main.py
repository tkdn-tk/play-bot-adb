import sys
import yaml
import keyboard
import threading
import time
import os
import win32gui
import win32process
import psutil
import questionary

from core.logger import logger
from core.bot import RerollBot
from tools.capture_tool import CaptureTool

def load_config(config_path="config.yaml"):
    try:
        with open(config_path, "r") as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        sys.exit(1)

def run_bot(config):
    bot = RerollBot(config)
    
    # Setup hotkey for emergency stop and pause
    hotkey = config.get("hotkey", "F12")
    pause_hotkey = config.get("pause_hotkey", "F11")
    
    def check_hotkey():
        last_pause_time = 0
        while True:
            if keyboard.is_pressed(hotkey):
                logger.warning(f"\n{hotkey} pressed! Emergency stop initiated.")
                bot.stop()
                # Use os._exit to immediately terminate all threads
                os._exit(0)
                
            if keyboard.is_pressed(pause_hotkey):
                now = time.time()
                if now - last_pause_time > 1.0: # 1 second debounce
                    bot.toggle_pause()
                    last_pause_time = now
                    
            time.sleep(0.1)
            
    hotkey_thread = threading.Thread(target=check_hotkey, daemon=True)
    hotkey_thread.start()
    
    try:
        bot.start()
    except KeyboardInterrupt:
        logger.info("\nCaught KeyboardInterrupt, stopping...")
        bot.stop()
        
    logger.info("Bot execution finished.")

def interactive_select_mumu():
    print("\nScanning for running MuMu Player instances...")
    windows = []
    
    def callback(hwnd, extra):
        if not win32gui.IsWindowVisible(hwnd):
            return
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        try:
            proc_name = psutil.Process(pid).name().lower()
        except:
            proc_name = ""
            
        # Ignore system processes and common non-emulators
        if proc_name in ["explorer.exe", "searchapp.exe", "devenv.exe", "code.exe", "chrome.exe", "firefox.exe", "msedge.exe"]:
            return
            
        title = win32gui.GetWindowText(hwnd)
        if title and title != "Default" and title != "Program Manager":
            rect = win32gui.GetWindowRect(hwnd)
            w = rect[2] - rect[0]
            h = rect[3] - rect[1]
            if w > 300 and h > 300:
                windows.append({"title": title, "pid": pid, "proc": proc_name})
                    
    win32gui.EnumWindows(callback, None)
    
    if not windows:
        logger.warning("No MuMu Player instances found running.")
        return None
        
    choices = []
    for w in windows:
        choices.append(questionary.Choice(title=f"{w['title']} (PID: {w['pid']}, Proc: {w['proc']})", value=w['title']))
        
    if len(choices) == 1:
        logger.info(f"Only one instance found. Auto-selecting: {choices[0].title}")
        return choices[0].value
        
    answer = questionary.select(
        "Which MuMu instance do you want to run the bot on?",
        choices=choices
    ).ask()
    
    return answer

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "capture":
        config = load_config()
        tool = CaptureTool(config)
        tool.run()
        return
        
    print("--- Cookie Run Classic CV Reroll Bot ---")
    
    config_path = "config.yaml"
    instance_number = None
    
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg.endswith(".yaml"):
            config_path = arg
        elif arg.isdigit():
            instance_number = arg
            
    config = load_config(config_path)
    
    # If the user passed a number (e.g. '01'), format the window title if it's a template
    if instance_number is not None:
        title = config.get("emulator_window_title", "")
        if "{number}" in title:
            config["emulator_window_title"] = title.replace("{number}", instance_number)
        else:
            # Fallback if they didn't put {number} in config, just append it
            config["emulator_window_title"] = f"{title}-{instance_number}"
    else:
        # Interactive menu
        selected_title = interactive_select_mumu()
        if selected_title:
            config["emulator_window_title"] = selected_title
            
    logger.set_config(config)
    
    logger.info("Starting bot in 3 seconds (ADB Background Mode).")
    for i in range(3, 0, -1):
        print(f"{i}...", end="", flush=True)
        time.sleep(1)
    print()
    
    run_bot(config)

if __name__ == "__main__":
    main()
