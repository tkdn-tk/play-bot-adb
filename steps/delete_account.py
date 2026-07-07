from core.bot import State
from core.logger import logger
import time

def close_all_x_buttons(bot):
    """Explicitly check for and close any stray windows with 'X' buttons."""
    logger.info("Scanning for stray 'X' close buttons...")
    x_templates = [
        "popups/close_x",
        "popups/close_x_small",
        "buttons/close_settings",
        "buttons/close_hatch_tab",
        "buttons/close_x_pet_tab",
        "buttons/close_x_treasure_tab",
        "buttons/pet_close_x_btn",
        "buttons/special_treasure_close_alt",
        "buttons/special_treasure_close_small"
    ]
    
    for _ in range(3): # max 3 layers of popups
        current_screen = bot.detector.screen_capture.capture()
        if current_screen is None:
            break
            
        found_in_scan = False
        for template in x_templates:
            result = bot.detector.find(template, screen_img=current_screen)
            if result:
                x, y, conf = result
                logger.info(f"Found stray X button {template} (conf={conf:.2f}), clicking...")
                bot.clicker.click_window_relative(x, y)
                time.sleep(1.0)
                found_in_scan = True
                break
                
        if not found_in_scan:
            break

def execute(bot):
    """Delete account and restart cycle."""
    logger.info("Initiating account deletion...")
    
    # Attempt to open settings and game info, retrying if popups block it
    game_info_opened = False
    for attempt in range(3):
        logger.info(f"Attempting to open settings (attempt {attempt+1}/3)...")
        settings_clicked = False
        for template in ["buttons/settings_main", "buttons/settings"]:
            if bot.clicker.click_template(template, timeout=3.0):
                settings_clicked = True
                break
                
        if settings_clicked:
            logger.info("Looking for Game Info tab...")
            if bot.clicker.click_template("buttons/tab_game_info", timeout=4.0):
                game_info_opened = True
                break
            else:
                logger.warning("Settings clicked, but Game Info tab not found. Menu might not have opened.")
        else:
            logger.warning("Could not find settings button.")
            
        # If we didn't succeed, do a thorough popup clear and try again
        if attempt < 2:
            logger.info("Clearing all popups before retrying...")
            close_all_x_buttons(bot)
            from steps.setup import execute_clear_popups
            execute_clear_popups(bot, initial_delay=0.0)
            
    if not game_info_opened:
        logger.error("Failed to reach Game Info tab for deletion.")
        return None
        
    # Click Delete Account
    if not bot.clicker.click_template("buttons/delete_account", timeout=5.0):
        logger.error("Could not find Delete Account button.")
        return None
        
    logger.info("Waiting 70 seconds for delete confirmation button to activate...")
    time.sleep(70.0)
    
    logger.info("Attempting to click confirm delete...")
    # It should be active now. Click it.
    if bot.clicker.click_template("buttons/confirm_delete_active", timeout=5.0):
        logger.info("Clicked confirm delete.")
        
        # There's usually a final confirmation to restart the game
        time.sleep(2.0)
        if bot.clicker.click_template("buttons/confirm_restart", timeout=10.0):
            logger.info("Confirmed game restart.")
            
            # Game will restart, wait a long time before returning to login state
            logger.info("Waiting for game to restart...")
            time.sleep(15.0) 
            
            return State.LOGIN
            
    logger.error("Timeout waiting for delete confirmation.")
    return None
