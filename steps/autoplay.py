import time
import random
from core.logger import logger
from core.bot import State
import pyautogui

def execute_wait_main_menu(bot):
    logger.info("Waiting for main menu. Checking for popups...")
    start_time = time.time()
    
    while time.time() - start_time < 30.0:  # Allow 30 seconds to find main menu
        # Capture screen once per iteration for efficiency
        screen = bot.screen.capture()
        if screen is None:
            time.sleep(1.0)
            continue
            
        if bot.detector.find("main_menu.png", screen_img=screen):
            logger.info("Main menu found!")
            return State.PREPARE_PLAY
            
        # Try to close variants of popups dynamically
        import os
        popups = [f for f in os.listdir("templates") if f.startswith("popup_confirm") and f.endswith(".png")]
        
        popup_closed = False
        for popup in popups:
            # Added threshold=0.8 to prevent false positives that cause click misses
            result = bot.detector.find(popup, screen_img=screen, threshold=0.8)
            if result:
                bot.clicker.click_window_relative(result[0], result[1])
                logger.info(f"Closed popup using {popup} (conf={result[2]:.2f})")
                time.sleep(1.0)
                popup_closed = True
                break # Break out of inner loop to check for main menu again
                
        if not popup_closed:
            time.sleep(1.0)
        
    logger.error("Timed out waiting for main menu.")
    return None

def execute_prepare_play(bot):
    if bot.clicker.click_template("play_tab.png", timeout=5.0):
        time.sleep(1.0)
        return State.BUY_BUFFS
    return None

def execute_buy_buffs(bot):
    logger.info("Buying fast start buff...")
    if bot.clicker.click_template("buy_fast_start.png", timeout=3.0):
        time.sleep(0.5)
        bot.clicker.click_template("buy_boost_confirm.png", timeout=3.0)
        time.sleep(0.5)
        
    logger.info("Buying cookie relay buff...")
    if bot.clicker.click_template("buy_cookie_relay.png", timeout=3.0):
        time.sleep(0.5)
        bot.clicker.click_template("buy_boost_confirm.png", timeout=3.0)
        time.sleep(0.5)
        
    return State.MULTI_BUY

def execute_multi_buy(bot):
    logger.info("Pressing multi-buy tab...")
    if bot.clicker.click_template("multi_buy_tab.png", timeout=5.0):
        time.sleep(0.5)
        logger.info("Pressing buy button...")
        if bot.clicker.click_template("multi_buy_button.png", timeout=3.0):
            time.sleep(0.5)
            logger.info("Pressing confirm buy button...")
            if bot.clicker.click_template("multi_buy_confirm.png", timeout=3.0):
                logger.info("Waiting for multi-buy stop button to appear...")
                # Wait for stop button to appear
                if bot.detector.wait_for("stop_button.png", timeout=10.0):
                    logger.info("Stop button found, waiting for it to disappear...")
                    # Wait for stop button to disappear
                    start_wait = time.time()
                    while time.time() - start_wait < 60.0: # 60 second timeout for multi-buy
                        if not bot.detector.find("stop_button.png"):
                            logger.info("Stop button disappeared. Multi-buy complete.")
                            time.sleep(1.0)
                            return State.START_GAME
                        time.sleep(1.0)
                    logger.error("Multi-buy stop button did not disappear within timeout.")
                    return None
                else:
                    logger.error("Multi-buy stop button did not appear.")
                    return None
            else:
                logger.error("Failed to click confirm buy.")
                return None
        else:
            logger.error("Failed to click buy button.")
            return None
    else:
        logger.error("Failed to click multi-buy tab.")
        return None

def execute_start_game(bot):
    if bot.clicker.click_template("play_button.png", timeout=5.0):
        time.sleep(2.0)
        return State.WAIT_START_BOOST
    return None

def execute_wait_start_boost(bot):
    mode = bot.config.get("bot_mode", "default")
    
    if mode == "fast_start":
        logger.info("[Fast Start] Spam clicking center until start boost appears...")
        center_x, center_y = 640, 360 # Assuming 1280x720 resolution
        
        # Phase 1: Spam click center until start_boost.png appears
        start_wait = time.time()
        found_boost = False
        while time.time() - start_wait < 15.0 and bot.running:
            bot.clicker.fast_click(center_x, center_y, offset_range=5)
            if bot.detector.find("start_boost.png"):
                found_boost = True
                break
                
        if not found_boost:
            logger.error("Fast Start: start boost did not appear in time.")
            return None
            
        logger.info("[Fast Start] Start boost appeared! Spam clicking until it disappears...")
        
        # Phase 2: Spam click center until start_boost.png disappears
        disappear_start = time.time()
        while time.time() - disappear_start < 15.0 and bot.running:
            bot.clicker.fast_click(center_x, center_y, offset_range=5)
            if not bot.detector.find("start_boost.png"):
                logger.info("[Fast Start] Start boost disappeared, proceeding to WAIT_RESULT.")
                return State.WAIT_RESULT
                
        logger.error("Fast Start: start boost did not disappear in time.")
        return None
    else:
        logger.info("Waiting for start boost button to appear...")
        if bot.detector.wait_for("start_boost.png", timeout=15.0):
            if bot.config.get("skip_macro", False):
                logger.info("Start boost button detected. Skipping macro, proceeding to WAIT_RESULT.")
                return State.WAIT_RESULT
            else:
                logger.info("Start boost button detected, proceeding to run macro.")
                return State.RUN_MACRO
        return None

def execute_run_macro(bot):
    logger.info("Searching Windows desktop for play_record.png...")
    try:
        # Search the entire Windows screen, not the ADB emulator screen
        center = pyautogui.locateCenterOnScreen("templates/play_record.png", confidence=0.8)
        if center:
            logger.info(f"Found play record button at {center}. Clicking...")
            # Add random offset to simulate human clicking slightly off-center
            offset_x = random.randint(-5, 5)
            offset_y = random.randint(-5, 5)
            target_x = center.x + offset_x
            target_y = center.y + offset_y
            
            # Note: This will temporarily hijack the real mouse cursor
            pyautogui.click(target_x, target_y)
            time.sleep(1.0)
            return State.WAIT_RESULT
        else:
            logger.error("Could not find play_record.png on the Windows desktop.")
    except Exception as e:
        logger.error(f"Error while searching for play record button: {e}")
        
    return None

def execute_wait_result(bot):
    logger.info("Waiting for macro to finish and result screen to appear...")
    # This might take a long time (minutes)
    if bot.detector.wait_for("result_screen.png", timeout=300.0): # 5 minutes timeout
        return State.CLOSE_RESULT
    return None

def execute_close_result(bot):
    if bot.clicker.click_template("close_result.png", timeout=5.0):
        time.sleep(2.0)
        return State.WAIT_MAIN_MENU
    return None
