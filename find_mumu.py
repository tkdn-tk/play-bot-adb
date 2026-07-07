import win32gui
import win32process

def get_mumu_windows():
    print("Searching for MuMu windows...")
    
    def callback(hwnd, extra):
        if not win32gui.IsWindowVisible(hwnd):
            return
            
        title = win32gui.GetWindowText(hwnd)
        class_name = win32gui.GetClassName(hwnd)
        
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        rect = win32gui.GetWindowRect(hwnd)
        w = rect[2] - rect[0]
        h = rect[3] - rect[1]
        
        # Only care about reasonably large windows (e.g. at least 500x500)
        # And make sure it's not minimized (-32000)
        if w > 500 and h > 500 and rect[0] > -10000:
            print(f"Large Window Found:")
            print(f"  Title: '{title.encode('ascii', 'replace').decode()}'")
            print(f"  Class: '{class_name}'")
            print(f"  Size:  {w}x{h}")
            print(f"  Pos:   ({rect[0]}, {rect[1]})")
            print("-" * 40)
            
    win32gui.EnumWindows(callback, None)

if __name__ == "__main__":
    get_mumu_windows()
