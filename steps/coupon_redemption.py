import time
import win32clipboard
from core.bot import State
from core.logger import logger
from tools.submit_coupon import submit_coupon

def get_clipboard_text():
    """Reads text from the Windows clipboard."""
    try:
        win32clipboard.OpenClipboard()
        data = win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
        win32clipboard.CloseClipboard()
        return data
    except Exception as e:
        logger.error(f"Failed to read clipboard: {e}")
        try:
            win32clipboard.CloseClipboard()
        except:
            pass
        return None

def execute(bot):
    """Navigate to Game Info, copy User ID, and redeem coupons."""
    logger.info("Initiating Coupon Redemption step...")
    
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
            from steps.setup import execute_clear_popups
            execute_clear_popups(bot, initial_delay=0.0)
            
    if not game_info_opened:
        logger.error("Failed to reach Game Info tab.")
        return None
        
    # Click Copy ID button
    logger.info("Looking for Copy ID button...")
    if not bot.clicker.click_template("buttons/copy_id", timeout=5.0):
        logger.error("Could not find Copy ID button.")
        return None
        
    logger.info("Clicked Copy ID. Waiting a moment for clipboard to update...")
    time.sleep(1.0)
    
    # Click confirm/ok on the "ID Copied" popup
    logger.info("Clicking confirm on ID popup...")
    confirm_clicked = False
    for template in ["buttons/confirm_id", "popups/ok_button"]:
        if bot.clicker.click_template(template, timeout=2.0):
            confirm_clicked = True
            time.sleep(1.0)
            break
            
    if not confirm_clicked:
        logger.warning("Could not find the confirm/OK button for ID copy. Continuing anyway...")
    
    # Get ID from clipboard
    user_id = get_clipboard_text()
    if not user_id:
        logger.error("Clipboard was empty or could not be read.")
        return None
        
    # Clean up the user ID (sometimes it might have spaces or newlines)
    user_id = user_id.strip()
    logger.success(f"Successfully copied User ID: {user_id}")
    
    # Check if there are coupons configured before pausing the game to open browser
    from tools.submit_coupon import get_coupon_codes_from_config
    coupons = get_coupon_codes_from_config("config.yaml")
    
    if coupons:
        logger.info(f"Redeeming {len(coupons)} coupon(s) via background API...")
        # This will silently get the Turnstile token and submit the API request
        results = submit_coupon(user_id)
        logger.info(f"Coupon redemption finished with results: {results}")
    else:
        logger.info("No valid coupons found in config. Skipping redemption.")
        
    # Close Settings to return to Lobby
    logger.info("Closing Settings menu...")
    
    # Try closing with a general close 'X' button. Add fallback templates if needed.
    close_templates = ["popups/close_x", "buttons/close_settings", "popups/close_x_small"]
    closed = False
    
    for template in close_templates:
        if bot.clicker.click_template(template, timeout=2.0):
            logger.info(f"Clicked {template} to close settings.")
            closed = True
            time.sleep(2.0) # wait for animation
            break
            
    if not closed:
        logger.warning("Could not find a button to close settings. It might still be open.")
        
    return State.MAILBOX
