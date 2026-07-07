import psutil
import win32gui
import win32process
from .logger import logger

def resolve_adb_serial(config):
    adb_config = config.get("adb", {})
    serial = adb_config.get("serial")
    
    # If explicit serial is provided and not empty, use it directly
    if serial and serial.strip():
        return serial.strip()
        
    window_title = config.get("emulator_window_title")
    if not window_title:
        logger.warning("No ADB serial or emulator_window_title provided in config. Defaulting to 127.0.0.1:7555")
        return "127.0.0.1:7555"
        
    # Check manual instances mapping first
    instances = adb_config.get("instances") or {}
    if window_title in instances:
        logger.info(f"Found manual mapping for '{window_title}': {instances[window_title]}")
        return instances[window_title]
        
    logger.info(f"Attempting to automatically extract ADB port for window: '{window_title}'")
    
    # 1. Find the window and its PID
    hwnd = win32gui.FindWindow(None, window_title)
    if not hwnd:
        # Try partial match if exact match fails
        found_hwnd = None
        def callback(h, extra):
            nonlocal found_hwnd
            if win32gui.IsWindowVisible(h) and window_title.lower() in win32gui.GetWindowText(h).lower():
                found_hwnd = h
        win32gui.EnumWindows(callback, None)
        hwnd = found_hwnd

    if not hwnd:
        logger.error(f"Could not find any window matching title '{window_title}'")
        return "127.0.0.1:7555" # Fallback
        
    _, pid = win32process.GetWindowThreadProcessId(hwnd)
    
    # 2. Get the UI process command line to find the VM instance ID
    try:
        player_proc = psutil.Process(pid)
        cmdline = player_proc.cmdline()
        
        vm_id = "0" # Default to 0 for MuMu 12 if no -v is passed
        for i, arg in enumerate(cmdline):
            if arg == "-v" and i + 1 < len(cmdline):
                vm_id = cmdline[i+1]
                break
            elif arg.startswith("-v="):
                vm_id = arg[3:]
                break
                
        # 3. Find the corresponding Headless process
        headless_proc = None
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            name = proc.info.get('name', '').lower()
            if 'headless' in name:
                p_cmdline = proc.info.get('cmdline') or []
                is_match = False
                
                # Check for MuMu 12 --comment argument matching
                for i, arg in enumerate(p_cmdline):
                    if arg == '--comment' and i + 1 < len(p_cmdline):
                        if p_cmdline[i+1].endswith(f"-{vm_id}"):
                            is_match = True
                            break
                            
                # Fallback to old Nemu logic (exact match of vm_id string)
                if not is_match and vm_id and vm_id in p_cmdline:
                    is_match = True
                    
                # If nothing else works and it's the old nemu, just grab it
                if not is_match and not vm_id and 'nemu' in name:
                    is_match = True
                    
                if is_match:
                    headless_proc = proc
                    break
                    
        if headless_proc:
            # 4. Check its listening TCP ports
            ports = []
            try:
                conns = headless_proc.connections(kind='tcp')
                for conn in conns:
                    if conn.status == 'LISTEN':
                        ports.append(conn.laddr.port)
            except Exception as e:
                logger.debug(f"psutil connections() failed: {e}")
                
            if not ports:
                # Fallback to netstat
                try:
                    import subprocess
                    output = subprocess.check_output(f'netstat -ano | findstr {headless_proc.pid}', shell=True).decode()
                    for line in output.splitlines():
                        if 'LISTENING' in line:
                            parts = line.split()
                            if len(parts) >= 2:
                                local_addr = parts[1]
                                if ':' in local_addr:
                                    port_str = local_addr.split(':')[-1]
                                    if port_str.isdigit():
                                        ports.append(int(port_str))
                except Exception as e:
                    logger.debug(f"Netstat fallback failed: {e}")

            # Sort ports descending so we check 16xxx before 7555
            ports.sort(reverse=True)
            for port in ports:
                if (16300 <= port <= 16500) or (7555 <= port <= 7600):
                    serial = f"127.0.0.1:{port}"
                    logger.success(f"Successfully extracted ADB port {port} for '{window_title}'")
                    return serial
                    
            logger.error("Found VM process but could not find its ADB listening port.")
        else:
            logger.error("Could not find the associated Headless VM process.")
            
    except Exception as e:
        logger.error(f"Error during automatic ADB port extraction: {e}")
        
    logger.warning("Automatic extraction failed. Defaulting to 127.0.0.1:7555")
    return "127.0.0.1:7555"
