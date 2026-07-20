import time
from datetime import datetime
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

class Logger:
    def __init__(self):
        self.last_log_time = None
        self.log_callbacks = []
        
    def add_callback(self, cb):
        self.log_callbacks.append(cb)
                
    def set_config(self, config):
        if "logging" in config:
            self.show_warnings = config["logging"].get("show_warnings", True)
            self.show_debug = config["logging"].get("debug", False)

    def _print(self, level, msg, color):
        now = time.time()
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        if self.last_log_time is not None:
            delta_ms = int((now - self.last_log_time) * 1000)
            if delta_ms < 1:
                duration_str = "<1ms"
            else:
                duration_str = f"{delta_ms}ms"
        else:
            duration_str = "0ms"
            
        self.last_log_time = now
        
        print(f"{Style.DIM}[{timestamp}]{Style.RESET_ALL} {color}[{level}]{Style.RESET_ALL} {Style.DIM}+{duration_str}{Style.RESET_ALL} {msg}")
        
        for cb in getattr(self, "log_callbacks", []):
            try:
                cb({"timestamp": timestamp, "level": level, "msg": msg})
            except Exception:
                pass

    def info(self, msg):
        self._print("INFO", msg, Fore.CYAN)

    def success(self, msg):
        self._print("SUCCESS", msg, Fore.GREEN)

    def warning(self, msg):
        if getattr(self, "show_warnings", True):
            self._print("WARNING", msg, Fore.YELLOW)

    def error(self, msg):
        self._print("ERROR", msg, Fore.RED)

    def debug(self, msg):
        if getattr(self, "show_debug", False):
            self._print("DEBUG", msg, Fore.LIGHTBLACK_EX)

# Global logger instance
logger = Logger()
