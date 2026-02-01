import platform
import sys
import time
from PySide6.QtCore import Qt

def is_windows():
    return platform.system() == "Windows"

def is_macos():
    return platform.system() == "Darwin"

# Platform specific imports
if is_windows():
    try:
        import win32gui
        import win32con
        import ctypes
        from ctypes import wintypes
    except ImportError:
        pass # Handle or log if needed
elif is_macos():
    try:
        from Quartz import CGWindowListCopyWindowInfo, kCGWindowListOptionOnScreenOnly, kCGNullWindowID
        from Quartz import CGEventCreateKeyboardEvent, CGEventPost, kCGHIDEventTap
        import Cocoa
        import objc
    except ImportError:
        print("Warning: pyobjc-framework-Quartz or pyobjc-framework-Cocoa not installed.")

def get_target_window_rect(window_title: str):
    """
    Returns (x, y, width, height) of the window with the given title.
    Returns None if not found.
    """
    if is_windows():
        try:
            hwnd = win32gui.FindWindow(None, window_title)
            if hwnd:
                rect = win32gui.GetWindowRect(hwnd)
                x, y, x2, y2 = rect
                return x, y, x2 - x, y2 - y
        except Exception:
            pass
    elif is_macos():
        try:
            # Use Quartz to find window
            options = kCGWindowListOptionOnScreenOnly
            window_list = CGWindowListCopyWindowInfo(options, kCGNullWindowID)
            for window in window_list:
                name = window.get('kCGWindowName', '')
                if name == window_title:
                    bounds = window['kCGWindowBounds']
                    return int(bounds['X']), int(bounds['Y']), int(bounds['Width']), int(bounds['Height'])
        except Exception as e:
            print(f"Error getting window rect on macOS: {e}")
    
    return None

def set_click_through(widget, enable: bool):
    """
    Sets the window to be transparent to mouse events (click-through).
    This handles both OS-level flags and Qt attributes.
    """
    # Common Qt attribute
    widget.setAttribute(Qt.WA_TransparentForMouseEvents, enable)

    if is_windows():
        try:
            hwnd = widget.winId().__int__()
            styles = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
            if enable:
                new_styles = styles | win32con.WS_EX_TRANSPARENT | win32con.WS_EX_LAYERED
            else:
                new_styles = styles & ~win32con.WS_EX_TRANSPARENT
            win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, new_styles)
        except Exception as e:
            print(f"Error setting click-through on Windows: {e}")
        
    elif is_macos():
        try:
            # On macOS, we rely on Cocoa to set ignoresMouseEvents on the NSWindow
            # widget.winId() returns a pointer to the NSView
            ns_view_ptr = int(widget.winId())
            ns_view = objc.objc_object(c_void_p=ns_view_ptr)
            ns_window = ns_view.window()
            ns_window.setIgnoresMouseEvents_(enable)
        except Exception as e:
            print(f"Error setting click-through on macOS: {e}")

# --- Input Simulation ---

def press_key(key_char: str):
    """
    Simulates a key press and release.
    """
    if is_windows():
        _press_key_windows(key_char)
    elif is_macos():
        _press_key_macos(key_char)
    else:
        print(f"press_key not implemented for {platform.system()}")

def key_down(key_char: str):
    """
    Simulates holding a key down.
    """
    if is_windows():
        _key_down_windows(key_char)
    elif is_macos():
        _key_down_macos(key_char)

def key_up(key_char: str):
    """
    Simulates releasing a key.
    """
    if is_windows():
        _key_up_windows(key_char)
    elif is_macos():
        _key_up_macos(key_char)

# Windows Implementation Details
if is_windows():
    INPUT_KEYBOARD = 1
    KEYEVENTF_KEYUP = 0x0002
    
    # Define structures only if on Windows to avoid ctypes errors on other platforms
    wintypes.ULONG_PTR = wintypes.WPARAM
    
    class MOUSEINPUT(ctypes.Structure):
        _fields_ = (("dx", wintypes.LONG),
                    ("dy", wintypes.LONG),
                    ("mouseData", wintypes.DWORD),
                    ("dwFlags", wintypes.DWORD),
                    ("time", wintypes.DWORD),
                    ("dwExtraInfo", wintypes.ULONG_PTR))

    class KEYBDINPUT(ctypes.Structure):
        _fields_ = (("wVk", wintypes.WORD),
                    ("wScan", wintypes.WORD),
                    ("dwFlags", wintypes.DWORD),
                    ("time", wintypes.DWORD),
                    ("dwExtraInfo", wintypes.ULONG_PTR))

    class HARDWAREINPUT(ctypes.Structure):
        _fields_ = (("uMsg", wintypes.DWORD),
                    ("wParamL", wintypes.WORD),
                    ("wParamH", wintypes.WORD))

    class INPUT(ctypes.Structure):
        class _INPUT(ctypes.Union):
            _fields_ = (("mi", MOUSEINPUT),
                        ("ki", KEYBDINPUT),
                        ("hi", HARDWAREINPUT))
        _anonymous_ = ("_input",)
        _fields_ = (("type", wintypes.DWORD),
                    ("_input", _INPUT))

    def _send_key(hexKeyCode):
        user32 = ctypes.WinDLL('user32', use_last_error=True)
        x = INPUT(type=INPUT_KEYBOARD, ki=KEYBDINPUT(wVk=hexKeyCode))
        user32.SendInput(1, ctypes.byref(x), ctypes.sizeof(x))

    def _send_key_release(hexKeyCode):
        user32 = ctypes.WinDLL('user32', use_last_error=True)
        x = INPUT(type=INPUT_KEYBOARD, ki=KEYBDINPUT(wVk=hexKeyCode, dwFlags=KEYEVENTF_KEYUP))
        user32.SendInput(1, ctypes.byref(x), ctypes.sizeof(x))

    def _get_vk(key_char):
        vk = 0
        key_char = key_char.upper()
        if len(key_char) == 1:
            vk = ord(key_char)
        else:
            mapping = {
                "F1": 0x70, "F2": 0x71, "F3": 0x72, "F4": 0x73, "F5": 0x74, "F6": 0x75,
                "SPACE": 0x20, "ENTER": 0x0D, "SHIFT": 0x10, "CTRL": 0x11, "ALT": 0x12
            }
            vk = mapping.get(key_char, 0)
        return vk

    def _press_key_windows(key_char):
        vk = _get_vk(key_char)
        if vk:
            _send_key(vk)
            time.sleep(0.05)
            _send_key_release(vk)

    def _key_down_windows(key_char):
        vk = _get_vk(key_char)
        if vk:
            _send_key(vk)

    def _key_up_windows(key_char):
        vk = _get_vk(key_char)
        if vk:
            _send_key_release(vk)

else:
    def _press_key_windows(key_char): pass
    def _key_down_windows(key_char): pass
    def _key_up_windows(key_char): pass

# macOS Implementation Details
def _get_macos_vk(key_char):
    # Basic mapping for macOS Virtual Keycodes
    key_map = {
        'A': 0x00, 'S': 0x01, 'D': 0x02, 'F': 0x03, 'H': 0x04, 'G': 0x05, 'Z': 0x06,
        'X': 0x07, 'C': 0x08, 'V': 0x09, 'B': 0x0B, 'Q': 0x0C, 'W': 0x0D, 'E': 0x0E,
        'R': 0x0F, 'Y': 0x10, 'T': 0x11, '1': 0x12, '2': 0x13, '3': 0x14, '4': 0x15,
        '6': 0x16, '5': 0x17, '=': 0x18, '9': 0x19, '7': 0x1A, '-': 0x1B, '8': 0x1C,
        '0': 0x1D, ']': 0x1E, 'O': 0x1F, 'U': 0x20, '[': 0x21, 'I': 0x22, 'P': 0x23,
        'L': 0x25, 'J': 0x26, '\'': 0x27, 'K': 0x28, ';': 0x29, '\\': 0x2A, ',': 0x2B,
        '/': 0x2C, 'N': 0x2D, 'M': 0x2E, '.': 0x2F,
        'SPACE': 0x31, 'ENTER': 0x24,
        'F1': 0x7A, 'F2': 0x78, 'F3': 0x63, 'F4': 0x76, 'F5': 0x60, 'F6': 0x61
    }
    
    key_char = key_char.upper()
    return key_map.get(key_char)

def _press_key_macos(key_char: str):
    try:
        vk = _get_macos_vk(key_char)
        if vk is not None:
            # Create key down event
            down = CGEventCreateKeyboardEvent(None, vk, True)
            CGEventPost(kCGHIDEventTap, down)
            
            time.sleep(0.05)
            
            # Create key up event
            up = CGEventCreateKeyboardEvent(None, vk, False)
            CGEventPost(kCGHIDEventTap, up)
            
    except Exception as e:
        print(f"Error sending key on macOS: {e}")

def _key_down_macos(key_char: str):
    try:
        vk = _get_macos_vk(key_char)
        if vk is not None:
            down = CGEventCreateKeyboardEvent(None, vk, True)
            CGEventPost(kCGHIDEventTap, down)
    except Exception as e:
        print(f"Error sending key down on macOS: {e}")

def _key_up_macos(key_char: str):
    try:
        vk = _get_macos_vk(key_char)
        if vk is not None:
            up = CGEventCreateKeyboardEvent(None, vk, False)
            CGEventPost(kCGHIDEventTap, up)
    except Exception as e:
        print(f"Error sending key up on macOS: {e}")
