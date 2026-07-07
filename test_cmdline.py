import psutil

print("Dumping command lines for MuMu processes...\n")
for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
    try:
        name = proc.info.get('name', '').lower()
        if 'mumu' in name:
            print(f"PID: {proc.info['pid']} | Name: {name}")
            print(f"Cmdline: {proc.info.get('cmdline')}\n")
    except Exception as e:
        pass
