from core.bot import State
from core.logger import logger
from tools.name_generator import generate_random_name
import time

def execute_name_input(bot):
    """Input a random name for the new account."""
    logger.info("Waiting for name input screen...")
    
    if bot.detector.wait_for("buttons/name_input_field", timeout=20.0):
        # Click the text field to focus
        if bot.clicker.click_template("buttons/name_input_field"):
            time.sleep(1.0)
            
            # Generate and type name
            name = generate_random_name()
            bot.clicker.type_text(name)
            
            # Press enter multiple times until the confirm button can be clicked
            for attempt in range(5):
                bot.clicker.press_key("enter")
                time.sleep(1.0)
                
                logger.info(f"Checking for confirm_name (attempt {attempt+1}/5)...")
                if bot.clicker.click_template("buttons/confirm_name", timeout=2.0):
                    logger.info("Clicked confirm_name. Waiting for it to disappear...")
                    if bot.detector.wait_for_gone("buttons/confirm_name", timeout=5.0):
                        logger.info(f"Entered name: {name} successfully.")
                        return State.CLEAR_POPUPS
                    else:
                        logger.warning("Confirm name button is still on screen. Retrying...")
                
    return None

def execute_clear_popups(bot, initial_delay=5.0):
    """Loop to detect and close all notifications/daily rewards."""
    logger.info("Clearing popups and notifications...")
    
    consecutive_empty_scans = 0
    max_empty_scans = 3
    
    # Config options
    popup_config = bot.config.get("clear_popups", {})
    batch_screenshots = popup_config.get("batch_screenshots", True)
    empty_scan_delay = popup_config.get("empty_scan_delay", 0.2)
    animation_delay = popup_config.get("animation_delay", 1.0)
    
    # Give the game a moment to load the main screen and first popup
    if initial_delay > 0:
        time.sleep(initial_delay)
    
    close_x_clicks = 0
    
    while consecutive_empty_scans < max_empty_scans:
        if not bot.running:
            return None
            
        found_popup = False
        
        popup_templates = [
            "popups/close_x",
            "popups/close_x_small",
            "popups/ok_button",
            "popups/claim_reward",
            "popups/cancel_button",
            "popups/skip_button"
        ]
        
        # Take ONE screenshot for this entire batch of templates if enabled
        current_screen = None
        if batch_screenshots:
            current_screen = bot.detector.screen_capture.capture()
            if current_screen is None:
                continue
        
        for template in popup_templates:
            # Use the batched screenshot if enabled, otherwise find() takes a fresh one
            result = bot.detector.find(template, screen_img=current_screen)
            if result:
                x, y, conf = result
                logger.info(f"Found popup {template} (conf={conf:.2f}), closing...")
                bot.clicker.click_window_relative(x, y)
                found_popup = True
                consecutive_empty_scans = 0
                time.sleep(animation_delay) # Wait for popup animation to close
                
                if template in ["popups/close_x", "popups/close_x_small"]:
                    close_x_clicks += 1
                else:
                    close_x_clicks = 0
                    
                if close_x_clicks > 30:
                    logger.warning("Clicked close_x more than 30 times, checking for confirm buttons...")
                    confirm_templates = [
                        "buttons/tutorial_confirm",
                        "buttons/ok_button_2", 
                        "buttons/confirm_quit_tutorial",
                        "buttons/confirm_name",
                        "buttons/confirm_restart",
                        "buttons/confirm_draw",
                        "buttons/confirm_delete_active",
                        "buttons/confirm_id"
                    ]
                    for confirm_btn in confirm_templates:
                        c_result = bot.detector.find(confirm_btn)
                        if c_result:
                            cx, cy, cconf = c_result
                            logger.info(f"Found confirm button {confirm_btn} (conf={cconf:.2f}), clicking to unstick...")
                            bot.clicker.click_window_relative(cx, cy)
                            time.sleep(animation_delay)
                            close_x_clicks = 0 # Reset after clicking
                            break
                            
                break # Break out of template loop to rescan from top
                
        if not found_popup:
            consecutive_empty_scans += 1
            time.sleep(empty_scan_delay)
            
    logger.info("All popups cleared.")
    return State.COUPON_REDEMPTION
