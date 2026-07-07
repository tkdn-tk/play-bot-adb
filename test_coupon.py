import time
import webbrowser
import pyautogui
import os

def test_browser_automation(user_id="GUEST-TEST12345", coupon_code="TESTCOUPON123"):
    """
    Test script to verify PyAutoGUI can correctly find and interact with 
    the DevPlay coupon website using your browser templates.
    """
    print(f"[*] Starting test with User ID: {user_id} and Coupon: {coupon_code}")
    
    # Using the exact URL requested
    url = "https://coupon.devplay.com/coupon/crg/en?"
    print(f"[*] Opening URL: {url}")
    webbrowser.open(url)
    
    print("[*] Waiting 7 seconds for page load and Cloudflare verification...")
    time.sleep(7.0)
    
    # Template paths
    account_box_path = os.path.join("templates", "browser", "account_box.png")
    code_box_path = os.path.join("templates", "browser", "code_box.png")
    submit_btn_path = os.path.join("templates", "browser", "submit_btn.png")
    
    # Verify templates exist
    missing = []
    for path in [account_box_path, code_box_path, submit_btn_path]:
        if not os.path.exists(path):
            missing.append(path)
            
    if missing:
        print(f"[-] ERROR: Missing browser templates.")
        print(f"Please take screenshots of the website elements and save them as:")
        for m in missing:
            print(f"  - {m}")
        return False
        
    try:
        # 1. Fill Account ID
        print("[*] Looking for Account box...")
        acc_loc = pyautogui.locateCenterOnScreen(account_box_path, confidence=0.8)
        if acc_loc:
            pyautogui.click(acc_loc)
            time.sleep(0.5)
            pyautogui.write(user_id, interval=0.05)
            time.sleep(1.0)
        else:
            print("[-] Could not find the Account box on screen.")
            return False
            
        # 2. Fill Coupon Code
        print("[*] Looking for Coupon Code box...")
        code_loc = pyautogui.locateCenterOnScreen(code_box_path, confidence=0.8)
        if code_loc:
            pyautogui.click(code_loc)
            time.sleep(0.5)
            pyautogui.write(coupon_code, interval=0.05)
            time.sleep(1.0)
        else:
            print("[-] Could not find the Coupon Code box on screen.")
            return False
            
        # 3. Click Submit
        print("[*] Looking for Submit button...")
        submit_loc = pyautogui.locateCenterOnScreen(submit_btn_path, confidence=0.8)
        if submit_loc:
            pyautogui.click(submit_loc)
            
            print("[*] Waiting for result alert...")
            time.sleep(3.0)
            
            # Press Enter to clear the alert dialog
            pyautogui.press('enter')
            time.sleep(1.0)
            
            # Close the browser tab (Ctrl+W)
            print("[*] Closing tab...")
            pyautogui.hotkey('ctrl', 'w')
            
            print("[+] Test completed successfully!")
            return True
        else:
            print("[-] Could not find the Submit button on screen.")
            return False
            
    except Exception as e:
        print(f"[-] Error during PyAutoGUI interaction: {e}")
        return False

if __name__ == "__main__":
    print("=== DEVPLAY COUPON BROWSER AUTOMATION TEST ===")
    test_uid = input("Enter a test DevPlay User ID (or press enter for default): ")
    if not test_uid.strip():
        test_uid = "GUEST-TEST12345"
        
    test_coupon = input("Enter a test Coupon Code (or press enter for default): ")
    if not test_coupon.strip():
        test_coupon = "TESTCOUPON123"
        
    test_browser_automation(test_uid, test_coupon)
