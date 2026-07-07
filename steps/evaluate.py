from core.bot import State
from core.logger import logger
import time

def execute(bot):
    """Final evaluation of the session."""
    logger.info("Evaluating session results...")
    
    # The actual evaluation is done in real-time during draws using bot.evaluator.evaluate_screen()
    # Here we just make the final decision based on accumulated items
    
    keep_account = bot.evaluator.final_decision()
    
    # We only need to manually log "reroll" here. "keep" is handled by bot._handle_success()
    if keep_account:
        return State.SUCCESS
    else:
        items_dict = dict(bot.evaluator.items_found)
        duration = time.time() - bot.session_start_time if getattr(bot, 'session_start_time', None) else 0.0
        logger.log_session(bot.session_count, items_dict, "reroll", bot.evaluator.all_drawn_items, duration=duration)
        
        # Send Email
        if bot.config.get("email", {}).get("enabled"):
            from core.emailer import send_bad_roll_email
            
            # Format bad roll details
            details_lines = []
            for item, count in items_dict.items():
                details_lines.append(f"- {item}: {count}")
            details_lines.append("\nAll Items Drawn:")
            for tag, name in bot.evaluator.all_drawn_items:
                details_lines.append(f"[{tag}] {name}")
            
            # Format global stats
            total_sessions = len(logger.session_data)
            bad_rolls = sum(1 for s in logger.session_data if str(s.get("result", "")).lower() != "keep")
            total_time = sum(s.get("duration_seconds", 0) for s in logger.session_data)
            
            mins = int(total_time // 60)
            secs = int(total_time % 60)
            
            stats = (
                f"Total Sessions Run: {total_sessions}\n"
                f"Total Bad Rolls: {bad_rolls}\n"
                f"Total Time Elapsed: {mins}m {secs}s"
            )
            
            send_bad_roll_email(bot.config, "\n".join(details_lines), stats)

        return State.DELETE_ACCOUNT
