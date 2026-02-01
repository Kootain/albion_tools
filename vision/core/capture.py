import abc
import numpy as np
import win32gui
import win32ui
import win32con
import win32api
import ctypes
from typing import Optional, Tuple

class BaseCapture(abc.ABC):
    @abc.abstractmethod
    def capture(self) -> Optional[np.ndarray]:
        """
        Capture an image.
        Returns:
            np.ndarray: The captured image in BGR format, or None if capture failed.
        """
        pass

class WindowCapture(BaseCapture):
    def __init__(self, window_title: str = None):
        self.window_title = window_title
        self.hwnd = None
        if window_title:
            self.hwnd = win32gui.FindWindow(None, window_title)
            if not self.hwnd:
                print(f"Window not found: {window_title}")

    def capture(self) -> Optional[np.ndarray]:
        if not self.hwnd:
            if self.window_title:
                 self.hwnd = win32gui.FindWindow(None, self.window_title)
            
            if not self.hwnd:
                return None

        # Get window dimensions
        try:
            left, top, right, bottom = win32gui.GetWindowRect(self.hwnd)
            w = right - left
            h = bottom - top
            
            # Handle minimized or invalid window
            if w <= 0 or h <= 0:
                return None

            # Get device context
            wDC = win32gui.GetWindowDC(self.hwnd)
            dcObj = win32ui.CreateDCFromHandle(wDC)
            cDC = dcObj.CreateCompatibleDC()
            
            # Create bitmap object
            dataBitMap = win32ui.CreateBitmap()
            dataBitMap.CreateCompatibleBitmap(dcObj, w, h)
            
            cDC.SelectObject(dataBitMap)
            
            # Try to capture
            success = False
            
            # Method 1: PrintWindow (Good for background, but might be slower or missing in some pywin32 versions)
            # We use ctypes to avoid 'AttributeError' if win32gui is missing it
            try:
                # PW_RENDERFULLCONTENT = 2
                result = ctypes.windll.user32.PrintWindow(self.hwnd, cDC.GetSafeHdc(), 2)
                if result != 0:
                    success = True
            except Exception:
                pass
            
            # Method 2: BitBlt (Faster, but requires window to be visible/not fully obscured usually)
            if not success:
                try:
                    cDC.BitBlt((0, 0), (w, h), dcObj, (0, 0), win32con.SRCCOPY)
                    success = True
                except Exception as e:
                    print(f"BitBlt failed: {e}")

            if not success:
                # Cleanup if both failed
                dcObj.DeleteDC()
                cDC.DeleteDC()
                win32gui.ReleaseDC(self.hwnd, wDC)
                win32gui.DeleteObject(dataBitMap.GetHandle())
                return None

            # Convert to numpy array
            signedIntsArray = dataBitMap.GetBitmapBits(True)
            img = np.frombuffer(signedIntsArray, dtype='uint8')
            img.shape = (h, w, 4)

            # Free resources
            dcObj.DeleteDC()
            cDC.DeleteDC()
            win32gui.ReleaseDC(self.hwnd, wDC)
            win32gui.DeleteObject(dataBitMap.GetHandle())

            # Drop alpha channel and return
            return img[..., :3]
            
        except Exception as e:
            print(f"Capture failed: {e}")
            return None
