import yaml
import time
import requests
import asyncio
import os
import nodriver as uc

# Suppress messy asyncio cleanup warnings on Windows
import warnings
warnings.filterwarnings("ignore", category=ResourceWarning)

def get_coupon_codes_from_config(config_path="config.yaml"):
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
            if "coupon_codes" in config and isinstance(config["coupon_codes"], list):
                return config["coupon_codes"]
            elif "coupon_code" in config:
                return [config["coupon_code"]]
            return []
    except Exception as e:
        print(f"[-] Error reading config: {e}")
        return []

async def process_all_coupons(user_id, coupon_codes):
    """
    Main async worker that handles the browser session and submissions.
    """
    url = f"https://coupon.devplay.com/coupon/crg/en?userId={user_id}"
    
    # Account format check
    email = ""
    mid = ""
    if "@" in user_id or user_id.startswith("GUEST-"):
        email = user_id
    else:
        mid = user_id
        
    api_url = "https://coupon.devplay.com/v1/coupon/crg"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    results = {}
    
    for i, code in enumerate(coupon_codes):
        print(f"\n[*] Processing ({i+1}/{len(coupon_codes)}): {code}")
        browser = None
        
        try:
            print("[*] Starting nodriver to bypass Cloudflare Turnstile...")
            browser = await uc.start()
            
            # Navigate to page to trigger Turnstile
            page = await browser.get(url)
            print("[*] Waiting for Turnstile token to generate...")
            
            token = None
            for _ in range(20):
                await asyncio.sleep(1)
                try:
                    elem = await page.select('input[name="cf-turnstile-response"]')
                    if elem:
                        val = elem.attrs.get("value")
                        if val:
                            token = val
                            break
                except Exception:
                    pass
            
            if not token:
                print("[-] Failed to get Turnstile token for this request.")
                results[code] = False
                continue
                
            print(f"[+] Got Turnstile token: {token[:15]}...[TRUNCATED]")
            print("[*] Sending API request in the background...")
            
            payload = {
                "email": email,
                "mid": mid,
                "game_code": "crg",
                "coupon_code": code,
                "token": token
            }
            
            # Direct API request
            try:
                # Running sync requests.post in async function (blocks loop briefly, but fine here)
                resp = requests.post(api_url, json=payload, headers=headers, timeout=15)
                if resp.status_code == 200:
                    data = resp.json()
                    response_code = data.get('responseCode')
                    print(f"[+] API Response: {response_code}")
                    results[code] = (response_code == "RESPONSE_CODE_SUCCESS")
                else:
                    print(f"[-] Server returned status {resp.status_code}")
                    results[code] = False
            except Exception as e:
                print(f"[-] API request failed: {e}")
                results[code] = False
                
        except Exception as e:
            print(f"[-] Browser automation error: {e}")
        finally:
            if browser:
                print("[*] Closing browser window for this code...")
                browser.stop()
                # Give it a second to clean up cleanly
                await asyncio.sleep(1)
                
    return results

def submit_coupon(user_id, config_path="config.yaml"):
    """
    Submits coupons completely in the background via API requests!
    Uses nodriver to silently get the Cloudflare token.
    """
    coupon_codes = get_coupon_codes_from_config(config_path)
    coupon_codes = [c for c in coupon_codes if c and c not in ["YOUR_COUPON_CODE_HERE", "YOUR_FIRST_COUPON_CODE_HERE", "YOUR_SECOND_COUPON_CODE_HERE"]]
    
    if not coupon_codes:
        print("[-] Please set valid coupon_codes in config.yaml.")
        return {}
    if not user_id:
        print("[-] No User ID provided.")
        return {}

    print(f"[*] Starting background API coupon submission for user: {user_id}")
    
    # Silence the Windows proactor event loop exceptions on shutdown
    if os.name == 'nt':
        try:
            # We wrap it in a try block in case the loop is already running
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        except:
            pass

    try:
        results = asyncio.run(process_all_coupons(user_id, coupon_codes))
    except Exception as e:
        # Ignore noisy runtime errors from loop tear-down
        if "Event loop is closed" not in str(e):
            print(f"[-] Error: {e}")
        results = {}
        
    print("\n[*] Finished all background coupons!")
    return results

if __name__ == "__main__":
    test_uid = input("Enter a test DevPlay User ID: ")
    submit_coupon(test_uid)
