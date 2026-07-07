import yaml
from core.emailer import send_success_email, send_bad_roll_email, send_error_email
from core.logger import logger

def main():
    print("--- Testing Email Notifications ---")
    try:
        with open('config.yaml', 'r') as file:
            config = yaml.safe_load(file)
            
        # Initialize logger so we can see the output of the emailer functions
        logger.set_config(config)

        if not config.get('email', {}).get('enabled', False):
            print("Email is disabled in config.yaml. Please enable it to test.")
            return

        print("\n1. Testing Success Email (Good Roll)...")
        dummy_good_details = "- laurel: 1\n- lantern: 1\n\nAll Items Drawn:\n[Treasure] laurel\n[Treasure] lantern"
        dummy_stats = "Total Sessions Run: 10\nTotal Bad Rolls: 9\nTotal Time Elapsed: 15m 30s"
        send_success_email(config, dummy_good_details, dummy_stats)

        print("\n2. Testing Bad Roll Email...")
        dummy_bad_details = "- tater: 0\n\nAll Items Drawn:\n[Pet] sitter"
        send_bad_roll_email(config, dummy_bad_details, dummy_stats)

        print("\n3. Testing Error Email...")
        dummy_error = "Exception: Failed to find element after 3 retries."
        dummy_state = "State.COUPON_REDEMPTION"
        send_error_email(config, dummy_error, dummy_state)

        print("\nAll test emails triggered! Please check your inboxes.")

    except Exception as e:
        print(f"Test failed with error: {e}")

if __name__ == "__main__":
    main()
