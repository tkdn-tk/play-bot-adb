from core.bot import State
from core.logger import logger

def execute(bot):
    """Guest login flow."""
    logger.info("Waiting for login screen...")
    
    # Wait for the guest login button to appear
    if bot.clicker.click_template("buttons/guest_login", timeout=30.0):
        logger.info("Clicked guest login.")
        
        # We might have a confirmation prompt for guest login
        # We can either wait for it, or just assume it goes to the main menu/tutorial
        # Let's check for a confirm button
        if bot.detector.wait_for("buttons/confirm_login", timeout=10.0):
            bot.clicker.click_template("buttons/confirm_login")
            logger.info("Confirmed guest login.")
            
        return State.PLAY
        
    return None
