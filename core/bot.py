import time
import sys
from enum import Enum, auto
from .logger import logger
from .screen import ScreenCapture
from .clicker import Clicker
from .detector import Detector
from .evaluator import Evaluator
from .adb_resolver import resolve_adb_serial

class State(Enum):
    LOGIN = auto()
    PLAY = auto()
    TUTORIAL = auto()
    NAME_INPUT = auto()
    CLEAR_POPUPS = auto()
    COUPON_REDEMPTION = auto()
    MAILBOX = auto()
    TREASURE_DRAW = auto()
    SPECIAL_TREASURE = auto()
    CLOSE_TREASURE = auto()
    PET_DRAW = auto()
    EVALUATE = auto()
    DELETE_ACCOUNT = auto()
    SUCCESS = auto()

class RerollBot:
    def __init__(self, config):
        self.config = config
        
        # Resolve ADB serial once for all components
        resolved_serial = resolve_adb_serial(self.config)
        if "adb" not in self.config:
            self.config["adb"] = {}
        self.config["adb"]["serial"] = resolved_serial
        
        self.screen = ScreenCapture(config)
        self.clicker = Clicker(config)
        self.detector = Detector(config)
        self.evaluator = Evaluator(config)
        
        self.current_state = State.LOGIN
        self.session_count = 0
        self.running = False
        self.paused = False
        self.consecutive_restarts = 0
        
        # Load step modules dynamically to avoid circular imports during init
        self.steps = {}
        
    def _import_steps(self):
        import steps.login
        import steps.tutorial
        import steps.setup
        import steps.coupon_redemption
        import steps.mailbox
        import steps.treasure_draw
        import steps.pet_draw
        import steps.evaluate
        import steps.delete_account
        
        self.steps = {
            State.LOGIN: steps.login.execute,
            State.PLAY: steps.tutorial.execute_play,
            State.TUTORIAL: steps.tutorial.execute_tutorial,
            State.NAME_INPUT: steps.setup.execute_name_input,
            State.CLEAR_POPUPS: steps.setup.execute_clear_popups,
            State.COUPON_REDEMPTION: steps.coupon_redemption.execute,
            State.MAILBOX: steps.mailbox.execute,
            State.TREASURE_DRAW: steps.treasure_draw.execute_regular,
            State.SPECIAL_TREASURE: steps.treasure_draw.execute_special,
            State.CLOSE_TREASURE: steps.treasure_draw.execute_close,
            State.PET_DRAW: steps.pet_draw.execute,
            State.EVALUATE: steps.evaluate.execute,
            State.DELETE_ACCOUNT: steps.delete_account.execute
        }

    def start(self):
        if not self.screen.find_window():
            logger.error("Emulator window not found. Cannot start.")
            return

        self._import_steps()
        self.running = True
        logger.info("Bot started. Press F11 to Pause/Resume, F12 to Stop.")
        
        while self.running:
            self.wait_if_paused()
            if self.current_state == State.LOGIN:
                self.session_count += 1
                self.session_start_time = time.time()
                self.evaluator.reset()
                logger.info(f"--- Starting Reroll Session #{self.session_count} ---")
                
            try:
                self._run_current_state()
            except Exception as e:
                logger.error(f"Error in state {self.current_state.name}: {e}")
                
                self.consecutive_restarts += 1
                if self.consecutive_restarts >= 3:
                    logger.error("Bot has restarted 3 times consecutively (9 total step failures). Sending error email.")
                    if self.config.get("email", {}).get("enabled"):
                        try:
                            from .emailer import send_error_email
                            send_error_email(self.config, str(e), self.current_state.name)
                        except Exception as mail_err:
                            logger.error(f"Could not send error email: {mail_err}")
                    self.consecutive_restarts = 0
                    
                if self.config.get("retry", {}).get("restart_on_failure", True):
                    logger.warning("Restarting session from LOGIN.")
                    self.current_state = State.LOGIN
                else:
                    self.stop()

    def _run_current_state(self):
        max_retries = self.config.get("retry", {}).get("max_per_step", 3)
        retries = 0
        success = False
        
        while retries < max_retries and self.running:
            self.wait_if_paused()
            logger.info(f"Executing state: {self.current_state.name} (Attempt {retries + 1}/{max_retries})")
            
            if self.current_state == State.SUCCESS:
                self._handle_success()
                return
                
            step_func = self.steps.get(self.current_state)
            if not step_func:
                logger.error(f"No step function defined for state {self.current_state}")
                self.stop()
                return
                
            # Execute step
            # Pass bot instance (self) to step function so it can use screen, clicker, evaluator, config
            next_state = step_func(self)
            
            if next_state:
                logger.success(f"State {self.current_state.name} completed. Moving to {next_state.name}")
                self.current_state = next_state
                self.consecutive_restarts = 0
                success = True
                
                # Sleep between steps
                delay_min = self.config.get("delays", {}).get("between_steps_min", 1.0)
                delay_max = self.config.get("delays", {}).get("between_steps_max", 3.0)
                time.sleep(self.clicker.random_delay() or delay_min) # Re-use random delay logic but override range
                # Wait, clicker.random_delay uses click delays. Let's just use time.sleep with random
                import random
                time.sleep(random.uniform(delay_min, delay_max))
                break
            else:
                retries += 1
                logger.warning(f"State {self.current_state.name} failed.")
                time.sleep(2.0) # Wait before retry
                
        if not success and self.running:
            raise Exception(f"Failed to complete state {self.current_state.name} after {max_retries} retries.")

    def _handle_success(self):
        logger.success("=========================================")
        logger.success("GOOD ROLL FOUND! Stopping bot.")
        logger.success(f"Items: {list(self.evaluator.items_found)}")
        logger.success("=========================================")
        
        # Log to file
        items_dict = dict(self.evaluator.items_found)
        duration = time.time() - self.session_start_time if getattr(self, 'session_start_time', None) else 0.0
        logger.log_session(self.session_count, items_dict, "keep", self.evaluator.all_drawn_items, duration=duration)
        
        # Send Email
        if self.config.get("email", {}).get("enabled"):
            from .emailer import send_success_email
            
            # Format good roll details
            details_lines = []
            for item, count in items_dict.items():
                details_lines.append(f"- {item}: {count}")
            details_lines.append("\nAll Items Drawn:")
            for tag, name in self.evaluator.all_drawn_items:
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
            
            send_success_email(self.config, "\n".join(details_lines), stats)
        
        # Play alert sound
        try:
            import winsound
            winsound.Beep(1000, 500)
            time.sleep(0.1)
            winsound.Beep(1000, 500)
            time.sleep(0.1)
            winsound.Beep(1500, 1000)
        except:
            print("\a") # fallback terminal bell
            
        self.stop()

    def stop(self):
        logger.info("Stopping bot...")
        self.running = False
        
    def toggle_pause(self):
        self.paused = not self.paused
        if self.paused:
            logger.warning("\n[PAUSED] Bot paused! Press F11 again to resume.")
        else:
            logger.success("\n[RESUMED] Bot resuming...")
            
    def wait_if_paused(self):
        """Blocks execution if the bot is paused."""
        while self.paused and self.running:
            time.sleep(0.5)
