from core.bot import State
from core.logger import logger
import time

def execute_play(bot):
    """Wait for and click the play button after login."""
    logger.info("Waiting for play button...")
    
    # After login, there might be a loading screen. Wait for the Play button
    if bot.clicker.click_template("buttons/play", timeout=60.0):
        logger.info("Clicked Play button.")
        return State.TUTORIAL
        
    return None

def execute_tutorial(bot):
    """Handle the tutorial confirmation, open settings, and quit tutorial."""
    logger.info("Handling tutorial...")
    
    # Wait for the tutorial confirmation popup
    if bot.clicker.click_template("buttons/tutorial_confirm", timeout=30.0, threshold=0.7):
        logger.info("Confirmed tutorial start.")
        
        # Wait a moment for the tutorial to actually start and UI to appear
        time.sleep(3.0)
        
        # Click settings button (usually top right or top left during tutorial)
        if bot.clicker.click_template("buttons/settings", timeout=15.0):
            logger.info("Opened settings during tutorial.")
            
            # Click the quit tutorial button
            if bot.clicker.click_template("buttons/quit_tutorial", timeout=10.0):
                logger.info("Clicked quit tutorial.")
                
                # There might be a confirmation prompt to quit the tutorial
                if bot.clicker.click_template("buttons/confirm_quit_tutorial", timeout=5.0):
                    logger.info("Confirmed quitting tutorial.")
                
                return State.NAME_INPUT
                
    return None
