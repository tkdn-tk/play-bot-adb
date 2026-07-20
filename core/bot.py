import time
import sys
from enum import Enum, auto
from .logger import logger
from .screen import ScreenCapture
from .clicker import Clicker
from .detector import Detector
from .adb_resolver import resolve_adb_serial

class State(Enum):
    WAIT_MAIN_MENU = auto()
    PREPARE_PLAY = auto()
    BUY_BUFFS = auto()
    MULTI_BUY = auto()
    START_GAME = auto()
    WAIT_START_BOOST = auto()
    RUN_MACRO = auto()
    WAIT_RESULT = auto()
    CLOSE_RESULT = auto()
    
    # Gift Bot States
    SEND_GIFTS = auto()
    OPEN_MAIL_MENU = auto()
    WAIT_MAIL_TAB = auto()
    RECEIVE_GIFTS = auto()
    CLOSE_MAIL = auto()

class AutoPlayBot:
    def __init__(self, config):
        self.config = config
        
        # Resolve ADB serial once for all components
        resolved_serial = resolve_adb_serial(self.config)
        if "adb" not in self.config:
            self.config["adb"] = {}
        self.config["adb"]["serial"] = resolved_serial
        
        self.screen = ScreenCapture(config)
        self.screen.bot = self
        
        self.detector = Detector(config)
        self.detector.screen_capture = self.screen
        
        self.clicker = Clicker(config)
        self.clicker.screen_capture = self.screen
        self.clicker.detector = self.detector
        
        self.current_state = State.WAIT_MAIN_MENU
        self.session_count = 0
        self.start_time = 0
        self.current_loop_start_time = 0
        self.current_state_start_time = 0
        self.running = False
        self.paused = False
        self.consecutive_restarts = 0
        self.last_gift_time = 0
        
        self.steps = {}
        
    def _import_steps(self):
        import steps.autoplay
        import steps.send_gift
        
        self.steps = {
            State.WAIT_MAIN_MENU: steps.autoplay.execute_wait_main_menu,
            State.PREPARE_PLAY: steps.autoplay.execute_prepare_play,
            State.BUY_BUFFS: steps.autoplay.execute_buy_buffs,
            State.MULTI_BUY: steps.autoplay.execute_multi_buy,
            State.START_GAME: steps.autoplay.execute_start_game,
            State.WAIT_START_BOOST: steps.autoplay.execute_wait_start_boost,
            State.RUN_MACRO: steps.autoplay.execute_run_macro,
            State.WAIT_RESULT: steps.autoplay.execute_wait_result,
            State.CLOSE_RESULT: steps.autoplay.execute_close_result,
            
            # Gift steps
            State.SEND_GIFTS: steps.send_gift.execute_send_gifts,
            State.OPEN_MAIL_MENU: steps.send_gift.execute_open_mail_menu,
            State.WAIT_MAIL_TAB: steps.send_gift.execute_wait_mail_tab,
            State.RECEIVE_GIFTS: steps.send_gift.execute_receive_gifts,
            State.CLOSE_MAIL: steps.send_gift.execute_close_mail
        }

    def start(self):
        if not self.screen.find_window():
            logger.error("Emulator window not found. Cannot start.")
            return

        self._import_steps()
        self.running = True
        self.start_time = time.time()
        self.current_loop_start_time = time.time()
        self.current_state_start_time = time.time()
        
        try:
            import ctypes
            # ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED
            ctypes.windll.kernel32.SetThreadExecutionState(0x80000000 | 0x00000001 | 0x00000002)
            logger.debug("Windows sleep prevention activated.")
        except Exception:
            pass
            
        logger.info("Bot started. Press F11 to Pause/Resume, F12 to Stop.")
        
        while self.running:
            self.wait_if_paused()
            if self.current_state == State.WAIT_MAIN_MENU:
                self.session_count += 1
                self.current_loop_start_time = time.time()
                logger.info(f"--- Starting Gameplay Loop #{self.session_count} ---")
                
            try:
                self._run_current_state()
            except Exception as e:
                logger.error(f"Error in state {self.current_state.name}: {e}")
                
                self.consecutive_restarts += 1
                if self.consecutive_restarts >= 3:
                    logger.error("Bot has restarted 3 times consecutively. Please check your setup.")
                    self.consecutive_restarts = 0
                    
                if self.config.get("retry", {}).get("restart_on_failure", True):
                    logger.warning("Restarting loop from WAIT_MAIN_MENU.")
                    self.current_state = State.WAIT_MAIN_MENU
                    self.current_state_start_time = time.time()
                else:
                    self.stop()

    def _run_current_state(self):
        max_retries = self.config.get("retry", {}).get("max_per_step", 3)
        retries = 0
        success = False
        
        while retries < max_retries and self.running:
            self.wait_if_paused()
            logger.info(f"Executing state: {self.current_state.name} (Attempt {retries + 1}/{max_retries})")
                
            step_func = self.steps.get(self.current_state)
            if not step_func:
                logger.error(f"No step function defined for state {self.current_state}")
                self.stop()
                return
                
            # Execute step
            next_state = step_func(self)
            
            if next_state:
                logger.success(f"State {self.current_state.name} completed. Moving to {next_state.name}")
                self.current_state = next_state
                self.current_state_start_time = time.time()
                self.consecutive_restarts = 0
                success = True
                
                # Sleep between steps (skip delay if moving to RUN_MACRO for instant trigger)
                if next_state != State.RUN_MACRO:
                    delay_min = self.config.get("delays", {}).get("between_steps_min", 1.0)
                    delay_max = self.config.get("delays", {}).get("between_steps_max", 3.0)
                    import random
                    time.sleep(random.uniform(delay_min, delay_max))
                break
            else:
                retries += 1
                logger.warning(f"State {self.current_state.name} failed.")
                time.sleep(2.0) # Wait before retry
                
        if not success and self.running:
            raise Exception(f"Failed to complete state {self.current_state.name} after {max_retries} retries.")

    def stop(self):
        logger.info("Stopping bot...")
        self.running = False
        
        try:
            import ctypes
            # Restore normal sleep behavior (ES_CONTINUOUS)
            ctypes.windll.kernel32.SetThreadExecutionState(0x80000000)
            logger.debug("Windows sleep prevention deactivated.")
        except Exception:
            pass
        
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
