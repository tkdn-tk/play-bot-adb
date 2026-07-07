import win32gui

def enum_windows():
    windows = []
    def callback(hwnd, extra):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title:
                windows.append(title)
    win32gui.EnumWindows(callback, None)
    
    print("Visible Windows:")
    for w in sorted(windows):
        try:
            print(f" - '{w}'")
        except UnicodeEncodeError:
            print(f" - {w.encode('utf-8', 'ignore')}")
        
if __name__ == "__main__":
    enum_windows()
