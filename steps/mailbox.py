from core.bot import State
from core.logger import logger
from steps.setup import execute_clear_popups
import time

def execute(bot):
    """Open mailbox, claim all rewards, and close."""
    logger.info("Handling mailbox...")
    
    max_retries = 3
    for attempt in range(max_retries):
        logger.info(f"Mailbox attempt {attempt + 1}/{max_retries}")
        
        # Click mailbox icon from main screen
        if bot.clicker.click_template("buttons/mailbox", timeout=15.0):
            logger.info("Opened mailbox.")
            
            # Click the reward tab inside the mailbox
            if bot.clicker.click_template("buttons/mailbox_reward_tab", timeout=10.0):
                logger.info("Clicked mailbox reward tab.")
                time.sleep(1.0)
                
                # Wait for mailbox to open and click Claim All
                if bot.clicker.click_template("buttons/claim_all", timeout=10.0):
                    logger.info("Clicked Claim All.")
                    
                    # Wait for reward claim animation/confirmation
                    time.sleep(3.0)
                    
                    # Click OK/Confirm on the rewards popup if it appears
                    if bot.detector.find("popups/ok_button"):
                        bot.clicker.click_template("popups/ok_button")
                        time.sleep(1.0)
                    
            # Close mailbox
            logger.info("Closing mailbox...")
            closed = False
            for template in ["buttons/mailbox_close", "popups/close_x", "popups/close_x_small"]:
                if bot.clicker.click_template(template, timeout=3.0):
                    logger.info(f"Closed mailbox using {template}.")
                    closed = True
                    break
                    
            if closed:
                time.sleep(2.0)
                return State.TREASURE_DRAW
            else:
                logger.warning("Could not find a button to close the mailbox.")
                
        if attempt < max_retries - 1:
            logger.warning("Stuck in mailbox phase. Attempting to clear popups before retrying...")
            execute_clear_popups(bot, initial_delay=0.0)
            time.sleep(2.0)
            
    logger.error("Failed to process mailbox after max retries.")
    return None
