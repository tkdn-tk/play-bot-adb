import time
import os
from core.logger import logger
from core.bot import State

def execute_wait_main_menu(bot):
    logger.info("Waiting for main menu (Gift Bot). Checking for popups...")
    start_time = time.time()
    
    while time.time() - start_time < 30.0:
        screen = bot.screen.capture()
        if screen is None:
            time.sleep(1.0)
            continue
            
        if bot.detector.find("main_menu.png", screen_img=screen):
            logger.info("Main menu found!")
            return State.SEND_GIFTS
            
        # Try to close variants of popups dynamically
        popups = [f for f in os.listdir("templates") if f.startswith("popup_confirm") and f.endswith(".png")]
        
        popup_closed = False
        for popup in popups:
            result = bot.detector.find(popup, screen_img=screen, threshold=0.7)
            if result:
                bot.clicker.click_window_relative(result[0], result[1])
                logger.info(f"Closed popup using {popup} (conf={result[2]:.2f})")
                time.sleep(1.0)
                popup_closed = True
                break
                
        if not popup_closed:
            time.sleep(1.0)
        
    logger.error("Timed out waiting for main menu.")
    return None

def execute_send_gifts(bot):
    logger.info("Sending gifts...")
    
    # Get all variants of the send gift button
    gift_btns = [f for f in os.listdir("templates") if f.startswith("gift_send_button") and f.endswith(".png")]
    if not gift_btns:
        logger.warning("No templates found starting with 'gift_send_button'. Please add some.")
        
    # Scroll to top first
    logger.info("Scrolling to the top of the list...")
    sc = bot.screen
    cx = int((sc.target_width if sc.target_width else 1280) * 0.25)
    cy = sc.target_height if sc.target_height else 720
    
    # Use the same safe scroll bounds as the downward scroll, just inverted (40% to 60%)
    y1_up = int(cy * 0.4)
    y2_up = int(cy * 0.6)
    
    top_found = False
    max_scrolls = 30 # Avoid infinite loops if template is completely missing
    for _ in range(max_scrolls): 
        screen = bot.screen.capture()
        if screen is None:
            time.sleep(0.5)
            continue
            
        # check if top of list indicator ("1" symbol) is visible
        if bot.detector.find("list_top_indicator.png", screen_img=screen, threshold=0.8):
            logger.info("Reached the top of the list.")
            top_found = True
            break
            
        # Check if there's a popup blocking the screen before scrolling up
        popups = [f for f in os.listdir("templates") if f.startswith("popup_confirm") and f.endswith(".png")]
        popup_closed = False
        for popup in popups:
            result = bot.detector.find(popup, screen_img=screen, threshold=0.7)
            if result:
                logger.info(f"Closed popup using {popup} (conf={result[2]:.2f}) during upward scroll")
                bot.clicker.click_window_relative(result[0], result[1])
                time.sleep(1.0)
                popup_closed = True
                break
                
        if popup_closed:
            continue # Skip scrolling and check for top indicator again on the next loop
            
        # Fast duration (250ms) for strong inertia flick
        bot.clicker.swipe(cx, y1_up, cx, y2_up, duration=250)
        time.sleep(0.5) # reduced from 1.5s for faster upward scrolling
        
    if not top_found:
        logger.error("Could not reach the top of the list (indicator not found). Aborting gift sending phase.")
        return None # Returning None fails this state and triggers the bot's retry/recovery mechanics
    
    last_sent_time = time.time()
    
    while time.time() - last_sent_time < 60.0:
        screen = bot.screen.capture()
        if screen is None:
            time.sleep(0.5)
            continue
            
        found_gift_btn = False
        for btn_template in gift_btns:
            # Reduced threshold to 0.7 specifically for send gift buttons
            result = bot.detector.find(btn_template, screen_img=screen, threshold=0.7)
            if result:
                logger.info(f"Found Send Gift button using {btn_template} (conf={result[2]:.2f}). Clicking...")
                bot.clicker.click_window_relative(result[0], result[1])
                
                # Wait for and click confirm prompt
                logger.info("Waiting for first confirm prompt...")
                confirm_btn = bot.detector.wait_for("send_confirm.png", timeout=3.0, threshold=0.8)
                if confirm_btn:
                    logger.info("Clicking first confirm button...")
                    bot.clicker.click_window_relative(confirm_btn[0], confirm_btn[1])
                    time.sleep(0.5)
                    
                    # Wait for and click second confirm prompt
                    logger.info("Waiting for second confirm prompt...")
                    confirm_btn_2 = bot.detector.wait_for("send_confirm_2.png", timeout=3.0, threshold=0.8)
                    if not confirm_btn_2:
                        # Fallback to the same template if they look identical
                        confirm_btn_2 = bot.detector.wait_for("send_confirm.png", timeout=1.0, threshold=0.8)
                        
                    if confirm_btn_2:
                        logger.info("Clicking second confirm button...")
                        bot.clicker.click_window_relative(confirm_btn_2[0], confirm_btn_2[1])
                    else:
                        logger.warning("Second confirm button not found, continuing anyway...")
                else:
                    logger.warning("First confirm button not found, continuing anyway...")
                    
                last_sent_time = time.time()
                time.sleep(1.0) # wait for animation
                found_gift_btn = True
                break # Break out of inner loop to capture a fresh screen after clicking
                
        if not found_gift_btn:
            # First, check if there's a popup blocking the screen
            popups = [f for f in os.listdir("templates") if f.startswith("popup_confirm") and f.endswith(".png")]
            popup_closed = False
            for popup in popups:
                result = bot.detector.find(popup, screen_img=screen, threshold=0.7)
                if result:
                    logger.info(f"Closed popup using {popup} (conf={result[2]:.2f})")
                    bot.clicker.click_window_relative(result[0], result[1])
                    time.sleep(1.0)
                    popup_closed = True
                    # Reset timeout so it doesn't time out while dealing with popups
                    last_sent_time = time.time()
                    break
                    
            if popup_closed:
                continue # Skip scrolling and check for gifts again on the next loop
                
            # Swipe up to scroll down
            logger.info("No more gift buttons visible. Scrolling down (left side, shorter distance)...")
            sc = bot.screen
            
            # Position at 25% from the left instead of center
            cx = int((sc.target_width if sc.target_width else 1280) * 0.25)
            cy = sc.target_height if sc.target_height else 720
            
            # Shorter swipe distance to avoid skipping players (60% to 40%)
            y1 = int(cy * 0.6)
            y2 = int(cy * 0.4)
            
            # Slightly longer duration (500ms) for less inertia
            bot.clicker.swipe(cx, y1, cx, y2, duration=500)
            time.sleep(0.5) # reduced from 1.5s to speed up scanning
            
    logger.info("No gifts sent for 60 seconds. Finished sending gifts.")
    return State.OPEN_MAIL_MENU

def execute_open_mail_menu(bot):
    logger.info("Opening mail menu...")
    # Reset gift timer when transitioning to open mail state
    bot.last_gift_time = time.time()
    if bot.clicker.click_template("mail_button.png", timeout=5.0):
        time.sleep(1.5)
        return State.WAIT_MAIL_TAB
    return None

def execute_wait_mail_tab(bot):
    logger.info("Waiting for mail menu to load...")
    start_time = time.time()
    
    while time.time() - start_time < 15.0:
        screen = bot.screen.capture()
        if screen is None:
            time.sleep(0.5)
            continue
            
        # First, check if the receive gift button is already visible (means correct tab is open)
        receive_btn = bot.detector.find("receive_gift_button.png", screen_img=screen, threshold=0.8)
        if receive_btn:
            logger.info("Receive gift button already visible, no need to click tab...")
            return State.RECEIVE_GIFTS
            
        # Otherwise, check if we can see the gift tab and click it
        gift_tab = bot.detector.find("mail_gift_tab.png", screen_img=screen, threshold=0.8)
        if gift_tab:
            logger.info("Found gift tab, clicking it to switch tabs...")
            bot.clicker.click_window_relative(gift_tab[0], gift_tab[1])
            time.sleep(1.0)
            return State.RECEIVE_GIFTS
            
        time.sleep(0.5)
        
    logger.error("Timed out waiting for mail menu to load.")
    return None

def execute_receive_gifts(bot):
    logger.info("Receiving gifts...")
    
    # We loop to click "Receive" and then any confirmation prompt
    # Stop after 3 successful receives to avoid infinite loops if button stays visible
    
    empty_checks = 0
    receive_count = 0
    
    while empty_checks < 3: # 3 consecutive checks without receive button means done
        screen = bot.screen.capture()
        if screen is None:
            time.sleep(0.5)
            continue
            
        receive_btn = bot.detector.find("receive_gift_button.png", screen_img=screen, threshold=0.8)
        if receive_btn:
            empty_checks = 0
            logger.info("Found receive gift button, clicking...")
            bot.clicker.click_window_relative(receive_btn[0], receive_btn[1])
            time.sleep(1.0)
            
            # Wait for and click confirm prompt if it appears
            confirm_btn = bot.detector.wait_for("receive_confirm.png", timeout=3.0, threshold=0.8)
            if confirm_btn:
                logger.info("Confirming gift receipt...")
                bot.clicker.click_window_relative(confirm_btn[0], confirm_btn[1])
                time.sleep(1.0)
                
            receive_count += 1
            if receive_count >= 3:
                logger.info("Received gifts 3 times. Assuming all gifts are collected (or Receive All was used).")
                break
        else:
            empty_checks += 1
            time.sleep(1.0)
            
    if receive_count < 3:
        logger.info("No more gifts to receive.")
        
    return State.CLOSE_MAIL

def execute_close_mail(bot):
    logger.info("Closing mail menu...")
    if bot.clicker.click_template("close_button.png", timeout=5.0):
        time.sleep(2.0)
        return State.WAIT_MAIN_MENU
    
    # Fallback close button name
    if bot.clicker.click_template("mail_close.png", timeout=5.0):
        time.sleep(2.0)
        return State.WAIT_MAIN_MENU
        
    logger.error("Could not close mail menu.")
    return None
