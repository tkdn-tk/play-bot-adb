import subprocess
import psutil

print("Scanning for MuMu ADB Ports...")

try:
    output = subprocess.check_output("netstat -ano", shell=True).decode()
    found = False
    for line in output.splitlines():
        if "LISTENING" in line:
            parts = line.split()
            if len(parts) >= 5:
                local_addr = parts[1]
                pid = parts[-1]
                if ":" in local_addr:
                    port = local_addr.split(":")[-1]
                    if port.isdigit():
                        port = int(port)
                        # Check typical ADB ports
                        if (7555 <= port <= 7600) or (16300 <= port <= 16500) or (5555 <= port <= 5560):
                            try:
                                proc = psutil.Process(int(pid))
                                name = proc.name()
                            except:
                                name = "Unknown"
                            print(f"Found Port: {port}, PID: {pid}, Process: {name}")
                            found = True
    if not found:
        print("Could not find any typical ADB ports listening.")
except Exception as e:
    print(f"Error: {e}")
