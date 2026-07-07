import smtplib
from email.message import EmailMessage
from core.logger import logger

def send_success_email(config, good_roll_details, session_stats):
    """
    Sends an email notification when a good roll is found.
    
    :param config: The main config dictionary containing email settings.
    :param good_roll_details: A string containing the summary of the good roll.
    :param session_stats: A string containing the global statistics.
    """
    email_cfg = config.get("email", {})
    if not email_cfg.get("enabled"):
        logger.info("Email notifications are disabled in config.yaml.")
        return

    sender = email_cfg.get("sender_email")
    password = email_cfg.get("app_password")
    
    recipient = email_cfg.get("recipient_email")
    if isinstance(recipient, list):
        recipient = ", ".join(recipient)
    server = email_cfg.get("smtp_server", "smtp.gmail.com")
    port = email_cfg.get("smtp_port", 465)

    if not all([sender, password, recipient]):
        logger.error("Email is enabled but missing sender, app_password, or recipient in config.yaml.")
        return

    logger.info("Constructing success email...")
    
    msg = EmailMessage()
    msg['Subject'] = 'Cookie Run Reroll: Good Account Found!'
    msg['From'] = sender
    msg['To'] = recipient

    body = f"""Hello!

Your Cookie Run Reroll Bot has successfully found a good account!

=== GOOD ROLL DETAILS ===
{good_roll_details}

=== GLOBAL STATISTICS ===
{session_stats}

The bot has been paused and is waiting for you at the emulator.

Happy running,
Cookie Run CV Bot
"""
    msg.set_content(body)

    try:
        logger.info(f"Connecting to SMTP server {server}:{port}...")
        # Use SMTP_SSL for port 465
        if port == 465:
            with smtplib.SMTP_SSL(server, port) as smtp:
                smtp.login(sender, password)
                smtp.send_message(msg)
        else:
            # Fallback for TLS on port 587
            with smtplib.SMTP(server, port) as smtp:
                smtp.ehlo()
                smtp.starttls()
                smtp.login(sender, password)
                smtp.send_message(msg)
                
        logger.success("Success email sent!")
    except Exception as e:
        logger.error(f"Failed to send email: {e}")

def send_bad_roll_email(config, bad_roll_details, session_stats):
    """
    Sends an email notification when a bad roll is encountered.
    """
    email_cfg = config.get("email", {})
    if not email_cfg.get("enabled"):
        return

    sender = email_cfg.get("sender_email")
    password = email_cfg.get("app_password")
    
    recipient = email_cfg.get("bad_roll_recipient_email") or email_cfg.get("recipient_email")
    if isinstance(recipient, list):
        recipient = ", ".join(recipient)
        
    server = email_cfg.get("smtp_server", "smtp.gmail.com")
    port = email_cfg.get("smtp_port", 465)

    if not all([sender, password, recipient]):
        logger.error("Email is enabled but missing sender, app_password, or recipient for bad rolls in config.yaml.")
        return

    logger.info("Constructing bad roll email...")
    
    msg = EmailMessage()
    msg['Subject'] = 'Cookie Run Reroll: Bad Roll Session'
    msg['From'] = sender
    msg['To'] = recipient

    body = f"""Hello!

Your Cookie Run Reroll Bot encountered a bad roll and is resetting the account.

=== BAD ROLL DETAILS ===
{bad_roll_details}

=== GLOBAL STATISTICS ===
{session_stats}

The bot is continuing to the next session.

Happy running,
Cookie Run CV Bot
"""
    msg.set_content(body)

    try:
        # Use SMTP_SSL for port 465
        if port == 465:
            with smtplib.SMTP_SSL(server, port) as smtp:
                smtp.login(sender, password)
                smtp.send_message(msg)
        else:
            # Fallback for TLS on port 587
            with smtplib.SMTP(server, port) as smtp:
                smtp.ehlo()
                smtp.starttls()
                smtp.login(sender, password)
                smtp.send_message(msg)
                
        logger.success("Bad roll email sent!")
    except Exception as e:
        logger.error(f"Failed to send bad roll email: {e}")

def send_error_email(config, error_message, state_name):
    """
    Sends an email notification when the bot encounters 9 consecutive errors.
    """
    email_cfg = config.get("email", {})
    if not email_cfg.get("enabled"):
        return

    sender = email_cfg.get("sender_email")
    password = email_cfg.get("app_password")
    
    recipient = email_cfg.get("error_recipient_email") or email_cfg.get("recipient_email")
    if isinstance(recipient, list):
        recipient = ", ".join(recipient)
        
    server = email_cfg.get("smtp_server", "smtp.gmail.com")
    port = email_cfg.get("smtp_port", 465)

    if not all([sender, password, recipient]):
        logger.error("Email is enabled but missing sender, app_password, or recipient for errors in config.yaml.")
        return

    logger.info("Constructing error notification email...")
    
    msg = EmailMessage()
    msg['Subject'] = 'Cookie Run Reroll: Bot Error Alert'
    msg['From'] = sender
    msg['To'] = recipient

    body = f"""Hello!

Your Cookie Run Reroll Bot has encountered 9 consecutive step failures and had to restart 3 times in a row.

=== ERROR DETAILS ===
State: {state_name}
Error Message: {error_message}

The bot is currently keeping trying from the LOGIN phase.

Please check your emulator if this persists.

Happy running,
Cookie Run CV Bot
"""
    msg.set_content(body)

    try:
        # Use SMTP_SSL for port 465
        if port == 465:
            with smtplib.SMTP_SSL(server, port) as smtp:
                smtp.login(sender, password)
                smtp.send_message(msg)
        else:
            # Fallback for TLS on port 587
            with smtplib.SMTP(server, port) as smtp:
                smtp.ehlo()
                smtp.starttls()
                smtp.login(sender, password)
                smtp.send_message(msg)
                
        logger.success("Error notification email sent!")
    except Exception as e:
        logger.error(f"Failed to send error email: {e}")
