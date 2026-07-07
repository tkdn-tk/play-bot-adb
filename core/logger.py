import os
import json
import time
import math
from datetime import datetime
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

class Logger:
    def __init__(self, log_file="logs/reroll_log.json"):
        self.log_file = log_file
        self.session_data = []
        self.last_log_time = None
        
        # Ensure log directory exists
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        
        # Load existing if available
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, "r") as f:
                    self.session_data = json.load(f)
            except Exception:
                self.session_data = []
                
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
            
    def treasure(self, msg):
        self._print("TREASURE", msg, Fore.LIGHTMAGENTA_EX)
        
    def pet(self, msg):
        self._print("PET", msg, Fore.LIGHTMAGENTA_EX)

    def rainbow(self, msg):
        """Prints a message with a full RGB rainbow gradient."""
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
        
        prefix = f"{Style.DIM}[{timestamp}]{Style.RESET_ALL}"
        
        # Build rainbow MATCH tag
        level = "MATCH"
        rainbow_tag = ""
        for i, char in enumerate(level):
            r = int(math.sin(0.3 * i + 0) * 127 + 128)
            g = int(math.sin(0.3 * i + 2) * 127 + 128)
            b = int(math.sin(0.3 * i + 4) * 127 + 128)
            rainbow_tag += f"\x1b[38;2;{r};{g};{b}m{char}"
        rainbow_tag += "\x1b[0m"
        
        # Build rainbow message
        rainbow_msg = ""
        for i, char in enumerate(msg):
            # Slow down the gradient slightly for the long message text
            r = int(math.sin(0.1 * (i + len(level)) + 0) * 127 + 128)
            g = int(math.sin(0.1 * (i + len(level)) + 2) * 127 + 128)
            b = int(math.sin(0.1 * (i + len(level)) + 4) * 127 + 128)
            rainbow_msg += f"\x1b[38;2;{r};{g};{b}m{char}"
        rainbow_msg += "\x1b[0m"
        
        print(f"{prefix} [{rainbow_tag}] {Style.DIM}+{duration_str}{Style.RESET_ALL} {rainbow_msg}")

    def log_session(self, session_num, items_found, result, all_drawn_items=None, duration=0.0):
        """Log a completed reroll session to JSON and create an individual text log."""
        timestamp_iso = datetime.now().isoformat()
        date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        is_good = str(result).lower() == "keep"
        good_bad_str = "good" if is_good else "bad"
        
        # 1. Update the master JSON file
        entry = {
            "session": session_num,
            "timestamp": timestamp_iso,
            "duration_seconds": round(duration, 2),
            "items_found": items_found,
            "all_drawn": all_drawn_items or [],
            "result": result  # "keep" or "reroll"
        }
        self.session_data.append(entry)
        self._save()
        
        # 2. Generate the individual summary text file
        folder = "sessions"
        os.makedirs(folder, exist_ok=True)
        
        filename = f"{good_bad_str}_session_{session_num:03d}_{date_str}.txt"
        filepath = os.path.join(folder, filename)
        
        # Format duration: 02m 05s (125s)
        mins = int(duration // 60)
        secs = int(duration % 60)
        duration_str = f"{mins:02d}m {secs:02d}s ({int(duration)}s)"
        
        summary_lines = [
            "====================================",
            f"Session:  {session_num:03d}",
            f"Date:     {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Duration: {duration_str}",
            f"Result:   {result.upper()} ({'Good' if is_good else 'Bad'})",
            "====================================",
            "",
            "--- Target Items Found ---"
        ]
        
        if items_found:
            for item, count in items_found.items():
                summary_lines.append(f"- {item}: {count}")
        else:
            summary_lines.append("- None")
            
        summary_lines.extend(["", "--- All Items Drawn ---"])
        if all_drawn_items:
            for tag, name in all_drawn_items:
                summary_lines.append(f"[{tag}] {name}")
        else:
            summary_lines.append("- None parsed (check OCR)")
            
        summary_text = "\n".join(summary_lines)
        
        with open(filepath, "w") as f:
            f.write(summary_text)
            
        # 3. Print the summary to console immediately
        self.print_session_summary(summary_text)

    def print_session_summary(self, summary_text):
        """Print the generated text summary to the console in a clear box."""
        print(f"\n{Fore.LIGHTMAGENTA_EX}--- SESSION SUMMARY ---{Style.RESET_ALL}")
        # Colorize specific parts if desired, but printing the raw text is usually cleanest
        print(summary_text)
        print(f"{Fore.LIGHTMAGENTA_EX}-----------------------{Style.RESET_ALL}\n")
        
    def _save(self):
        with open(self.log_file, "w") as f:
            json.dump(self.session_data, f, indent=4)

# Global logger instance
logger = Logger()
