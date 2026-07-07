from core.bot import State
from core.logger import logger
import time

def _perform_draws(bot, draw_type, count, draw_btn_template, result_template, confirm_template, confirms_per_draw=1, alt_draw_btn_template=None, alt_draw_confirm_template=None, pre_draw_btn_template=None):
    """Helper to perform multiple single draws."""
    for i in range(count):
        if not bot.running:
            return False
            
        logger.info(f"Performing {draw_type} draw {i+1}/{count}...")
        
        if pre_draw_btn_template:
            logger.info(f"Checking for pre-draw button for {draw_type}...")
            if bot.clicker.click_template(pre_draw_btn_template, timeout=3.0):
                time.sleep(1.5)
        
        # Click draw button
        if bot.clicker.click_template(draw_btn_template, timeout=5.0):
            logger.info(f"Clicked primary {draw_type} draw button.")
        elif alt_draw_btn_template and bot.clicker.click_template(alt_draw_btn_template, timeout=5.0):
            logger.info(f"Clicked alternate {draw_type} draw button.")
            if alt_draw_confirm_template:
                time.sleep(1.0)
                logger.info(f"Confirming alternate {draw_type} draw (First Popup)...")
                if not bot.clicker.click_template(alt_draw_confirm_template, timeout=5.0):
                    logger.warning(f"Could not find alternate draw confirm button. Trying generic ok.")
                    bot.clicker.click_template("popups/ok_button", timeout=3.0)
                    
                time.sleep(1.5)
                logger.info(f"Checking for a second confirm button (Second Popup)...")
                # Try a few common confirm buttons in case the second one looks different
                second_confirm_clicked = False
                for template in ["popups/ok_button_2", "popups/ok_button", "buttons/confirm_draw"]:
                    if bot.clicker.click_template(template, timeout=2.0):
                        second_confirm_clicked = True
                        break
                        
                if not second_confirm_clicked:
                    logger.info("No second confirm popup found, proceeding...")
                    
                time.sleep(1.5)
                logger.info("Clicking the alternate draw button AGAIN to proceed to results...")
                bot.clicker.click_template(alt_draw_btn_template, timeout=3.0)
        else:
            logger.error(f"Could not find {draw_type} draw button.")
            return False
            
        # Handle the result screens (multiple if it's a multi-pull like 7 treasures)
        for c in range(confirms_per_draw):
            logger.info(f"Waiting for {draw_type} result screen ({c+1}/{confirms_per_draw})...")
            # Wait longer for the initial draw animation, shorter for subsequent items
            timeout = 15.0 if c == 0 else 5.0
            
            if bot.detector.wait_for(result_template, timeout=timeout):
                # Wait for animation to finish rendering text
                time.sleep(2.0)
                
                # Evaluate the result
                screen_img = bot.screen.capture()
                if screen_img is not None:
                    found = bot.evaluator.evaluate_screen(screen_img, draw_type)
                    if found:
                        logger.info(f"Evaluated {draw_type} result: found {found}")
                
                # Click confirm to go to next item or back to draw screen
                time.sleep(1.0)
                if not bot.clicker.click_template(confirm_template, timeout=5.0):
                    logger.warning(f"Could not find confirm button after {draw_type} draw. Trying generic OK.")
                    bot.clicker.click_template("popups/ok_button", timeout=3.0)
                    
                time.sleep(1.0)
            else:
                logger.error(f"Timeout waiting for {draw_type} result screen. Breaking out early.")
                break
                
        time.sleep(2.0) # Wait to return to draw menu
        
    return True

def execute_regular(bot):
    """Navigate to treasure draw and perform regular draws."""
    logger.info("Handling regular treasure draws...")
    
    # Click Gacha/Draw menu from main screen
    if bot.clicker.click_template("buttons/draw_menu", timeout=15.0):
        time.sleep(2.0)
        
        # Make sure we are on the treasure tab
        if bot.clicker.click_template("buttons/tab_treasure", timeout=5.0):
            time.sleep(1.0)
            
        draws_count = bot.config.get("draws", {}).get("treasure_regular", 8)
        
        if _perform_draws(bot, "Regular Treasure", draws_count, 
                          "draw/treasure_draw_btn", 
                          "results/treasure_result_bg", 
                          "buttons/confirm_draw"):
            return State.SPECIAL_TREASURE
            
    return None

def execute_special(bot):
    """Switch to special treasure tab and perform special draws."""
    logger.info("Handling special treasure draws...")
    
    # Try to switch to special treasure tab (optional)
    logger.info("Checking for special treasure tab...")
    if bot.clicker.click_template("buttons/tab_special_treasure", timeout=3.0):
        logger.info("Clicked special treasure tab.")
        time.sleep(2.0)
    else:
        logger.info("Special treasure tab not found. Assuming already there or not needed.")
        
    draws_count = bot.config.get("draws", {}).get("treasure_special", 2)
    
    if _perform_draws(bot, "Special Treasure", draws_count, 
                      "draw/special_draw_btn", 
                      "results/special_result_bg", 
                      "buttons/confirm_draw",
                      confirms_per_draw=7,
                      alt_draw_btn_template="draw/special_draw_btn_alt",
                      alt_draw_confirm_template="popups/ok_button"):
        return State.CLOSE_TREASURE
            
    return None

def execute_close(bot):
    """Close the treasure tab to return to main menu or move to pet draw."""
    logger.info("Closing treasure tab...")
    
    # Try primary close (generic X)
    if bot.clicker.click_template("popups/close_x", timeout=3.0):
        logger.info("Clicked primary close_x")
        time.sleep(1.0)
    # Try alternate close specific to special treasure
    elif bot.clicker.click_template("buttons/special_treasure_close_alt", timeout=2.0):
        logger.info("Clicked special_treasure_close_alt")
        time.sleep(1.0)
        
    # Check for any lingering secondary popups requiring the smaller X
    if bot.clicker.click_template("popups/close_x_small", timeout=3.0):
        logger.info("Clicked secondary smaller close_x_small")
        time.sleep(1.0)
    elif bot.clicker.click_template("buttons/special_treasure_close_small", timeout=2.0):
        logger.info("Clicked alternative secondary smaller close button")
        time.sleep(1.0)
        
    # Check for the specific treasure tab close button
    if bot.clicker.click_template("buttons/close_x_treasure_tab", timeout=2.0):
        logger.info("Clicked close_x_treasure_tab")
        time.sleep(1.0)
        
    # Early evaluation optimization: skip pet draw if treasure criteria failed
    if not bot.evaluator.check_treasure_early():
        logger.info("Skipping Pet Draw and heading straight to evaluation/deletion.")
        return State.EVALUATE
        
    return State.PET_DRAW
