import win32api
import win32con
import time
import math

class KeyboardController:
    """
    Simulates keyboard input for character movement based on configurable keys.
    """
    def __init__(self, up: str = 'E', down: str = 'D', left: str = 'S', right: str = 'F', duration_scale: float = 1.0, rotation_angle: float = 0):
        # Convert characters to virtual key codes
        self.up = ord(up.upper())
        self.down = ord(down.upper())
        self.left = ord(left.upper())
        self.right = ord(right.upper())
        
        self.duration_scale = duration_scale
        self.rotation_radians = math.radians(rotation_angle)
        
        # Track currently pressed keys to avoid redundant API calls
        self.pressed_keys = set()

    def _press_key(self, hex_key_code):
        if hex_key_code not in self.pressed_keys:
            win32api.keybd_event(hex_key_code, 0, 0, 0)
            self.pressed_keys.add(hex_key_code)

    def _release_key(self, hex_key_code):
        if hex_key_code in self.pressed_keys:
            win32api.keybd_event(hex_key_code, 0, win32con.KEYEVENTF_KEYUP, 0)
            self.pressed_keys.remove(hex_key_code)

    def move(self, x: float, y: float, threshold: float = 0.01):
        """
        Moves based on direction vector (x, y) for a duration determined by values and duration_scale.
        
        Args:
            x: Horizontal direction
            y: Vertical direction
            threshold: Deadzone threshold
        
        Logic:
            1. Apply rotation to input vector (x, y).
            2. Duration = abs(rotated_value) * duration_scale
            3. Presses keys simultaneously if both x and y are non-zero.
            4. Releases keys at appropriate times.
        """
        # Apply rotation
        # x' = x cos(theta) - y sin(theta)
        # y' = x sin(theta) + y cos(theta)
        rot_x = x * math.cos(self.rotation_radians) - y * math.sin(self.rotation_radians)
        rot_y = x * math.sin(self.rotation_radians) + y * math.cos(self.rotation_radians)

        dur_x = abs(rot_x) * self.duration_scale if abs(rot_x) > threshold else 0
        dur_y = abs(rot_y) * self.duration_scale if abs(rot_y) > threshold else 0
        
        key_x = self.right if rot_x > threshold else (self.left if rot_x < -threshold else None)
        key_y = self.up if rot_y > threshold else (self.down if rot_y < -threshold else None)
        
        if key_x: self._press_key(key_x)
        if key_y: self._press_key(key_y)
        
        if dur_x > 0 and dur_y > 0:
            # Both keys pressed
            if dur_x < dur_y:
                time.sleep(dur_x)
                self._release_key(key_x)
                time.sleep(dur_y - dur_x)
                self._release_key(key_y)
            else:
                time.sleep(dur_y)
                self._release_key(key_y)
                time.sleep(dur_x - dur_y)
                self._release_key(key_x)
        elif dur_x > 0:
            time.sleep(dur_x)
            self._release_key(key_x)
        elif dur_y > 0:
            time.sleep(dur_y)
            self._release_key(key_y)
            
    def release_all(self):
        """Releases all currently pressed keys managed by this controller."""
        # Create a copy to iterate while modifying the set
        for key in list(self.pressed_keys):
            self._release_key(key)

if __name__ == "__main__":
    print("Testing KeyboardController (Time-based)...")
    print("Please focus on a text editor or a game window.")
    print("Starting in 3 seconds...")
    time.sleep(2)
    
    # Default WASD, scale=0.1s per unit, 45 degree rotation
    controller = KeyboardController(duration_scale=0.23, rotation_angle=315)
    
    try:
        print("Moving X=10 (Rotated 45 -> Right + Up)")
        controller.move(0, 1)
        time.sleep(1) # Wait a bit between moves

        print("Stopping")
        
    except KeyboardInterrupt:
        pass
    finally:
        controller.release_all()
