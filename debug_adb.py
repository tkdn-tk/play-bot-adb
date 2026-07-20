import subprocess
import os
import time
import sys
import traceback
from adbutils._utils import get_adb_exe

print("ADB Exe path:", get_adb_exe())
adb = get_adb_exe()
serial = "127.0.0.1:16384"

# try to connect first
print("Connecting...")
try:
    print(subprocess.check_output([adb, "connect", serial]))
except Exception as e:
    print("Connect failed:", e)

time.sleep(1)

print("Running screencap...")
try:
    out = subprocess.check_output([adb, "-s", serial, "exec-out", "screencap", "-p"], stderr=subprocess.STDOUT)
    print("Screencap returned", len(out), "bytes")
    if out.startswith(b'\x89PNG'):
        print("Starts with PNG header")
    else:
        print("Does NOT start with PNG header")
except subprocess.CalledProcessError as e:
    print(f"Command failed with exit status {e.returncode}")
    print("Output:", e.output)
except Exception as e:
    print("Other exception:")
    traceback.print_exc()

print("Running alternative screencap (shell screencap -p)...")
try:
    out = subprocess.check_output([adb, "-s", serial, "shell", "screencap", "-p"], stderr=subprocess.STDOUT)
    print("Screencap returned", len(out), "bytes")
    if out.startswith(b'\x89PNG'):
        print("Starts with PNG header")
    else:
        print("Does NOT start with PNG header")
except subprocess.CalledProcessError as e:
    print(f"Command failed with exit status {e.returncode}")
    print("Output:", e.output)
except Exception as e:
    print("Other exception:")
    traceback.print_exc()
