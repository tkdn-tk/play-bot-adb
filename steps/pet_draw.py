from core.bot import State
from core.logger import logger
from steps.treasure_draw import _perform_draws
import time

def execute(bot):
    """Switch to pet tab and perform pet draws."""
    logger.info("Handling pet draws...")
    
    # Switch to pet draw tab with retries for lingering popups
    tab_pet_clicked = False
    for attempt in range(3):
        logger.info(f"Looking for Pet tab (attempt {attempt+1}/3)...")
        if bot.clicker.click_template("buttons/tab_pet", timeout=4.0):
            tab_pet_clicked = True
            time.sleep(2.0)
            break
        else:
            logger.warning("Could not find Pet tab. Trying to close lingering treasure popups...")
            bot.clicker.click_template("popups/close_x", timeout=1.0)
            bot.clicker.click_template("buttons/special_treasure_close_alt", timeout=1.0)
            bot.clicker.click_template("popups/close_x_small", timeout=1.0)
            bot.clicker.click_template("buttons/special_treasure_close_small", timeout=1.0)
            bot.clicker.click_template("buttons/close_x_treasure_tab", timeout=1.0)
            time.sleep(1.0)
            
    if tab_pet_clicked:
        
        draws_count = bot.config.get("draws", {}).get("pet", 2)
        
        if _perform_draws(bot, "Pet", draws_count, 
                          "draw/pet_draw_btn", 
                          "results/pet_result_bg", 
                          "buttons/pet_close_x_btn",
                          pre_draw_btn_template="draw/pet_hatch_btn"):
                              
            # Close the gacha/draw menu entirely after we're done with all draws
            logger.info("Finished all draws. Closing draw menu.")
            
            # Close hatch menu first
            if bot.clicker.click_template("buttons/close_hatch_tab", timeout=3.0):
                logger.info("Clicked close_hatch_tab")
                time.sleep(1.0)
                
            if bot.clicker.click_template("popups/close_x", timeout=3.0):
                logger.info("Clicked primary close_x")
                time.sleep(1.0)
            elif bot.clicker.click_template("buttons/close_x_pet_tab", timeout=2.0):
                logger.info("Clicked close_x_pet_tab")
                time.sleep(1.0)
            
            return State.EVALUATE
            
    return None
