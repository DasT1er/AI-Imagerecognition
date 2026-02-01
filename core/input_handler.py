"""
Input handler: mouse movement via win32api, hotkey management.
"""
import ctypes
import ctypes.wintypes
import time

# Windows API constants
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_ABSOLUTE = 0x8000

VK_CODES = {
    "LBUTTON": 0x01, "RBUTTON": 0x02, "MBUTTON": 0x04,
    "XBUTTON1": 0x05, "XBUTTON2": 0x06,
    "SHIFT": 0x10, "CTRL": 0x11, "ALT": 0x12,
    "CAPSLOCK": 0x14,
    "F1": 0x70, "F2": 0x71, "F3": 0x72, "F4": 0x73,
    "F5": 0x74, "F6": 0x75, "F7": 0x76, "F8": 0x77,
    "F9": 0x78, "F10": 0x79, "F11": 0x7A, "F12": 0x7B,
    "INSERT": 0x2D, "DELETE": 0x2E,
    "HOME": 0x24, "END": 0x23,
    "PAGEUP": 0x21, "PAGEDOWN": 0x22,
}

# Add letter/number keys
for i in range(26):
    VK_CODES[chr(65 + i)] = 0x41 + i
for i in range(10):
    VK_CODES[str(i)] = 0x30 + i


class InputHandler:
    """Handles mouse movement and key state detection via Win32 API."""

    def __init__(self):
        self.user32 = ctypes.windll.user32

    def move_mouse_relative(self, dx: int, dy: int):
        """Move mouse by relative offset using mouse_event."""
        if dx == 0 and dy == 0:
            return
        self.user32.mouse_event(MOUSEEVENTF_MOVE, int(dx), int(dy), 0, 0)

    def click(self):
        """Simulate left mouse click."""
        self.user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        time.sleep(0.01)
        self.user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)

    def is_key_pressed(self, key_name: str) -> bool:
        """Check if a key is currently held down."""
        vk = VK_CODES.get(key_name.upper())
        if vk is None:
            return False
        state = self.user32.GetAsyncKeyState(vk)
        return bool(state & 0x8000)

    def is_mouse_left_pressed(self) -> bool:
        """Check if left mouse button is held."""
        return self.is_key_pressed("LBUTTON")

    def is_mouse_right_pressed(self) -> bool:
        """Check if right mouse button is held."""
        return self.is_key_pressed("RBUTTON")

    def get_cursor_pos(self) -> tuple:
        """Get current cursor position."""
        point = ctypes.wintypes.POINT()
        self.user32.GetCursorPos(ctypes.byref(point))
        return (point.x, point.y)

    def get_screen_size(self) -> tuple:
        """Get primary monitor resolution."""
        w = self.user32.GetSystemMetrics(0)
        h = self.user32.GetSystemMetrics(1)
        return (w, h)


class HotkeyManager:
    """Manages toggle hotkeys with debounce."""

    def __init__(self, input_handler: InputHandler):
        self.input = input_handler
        self._key_states: dict = {}
        self._debounce = 0.2  # seconds

    def is_just_pressed(self, key_name: str) -> bool:
        """Returns True only once per key press (rising edge detection)."""
        pressed = self.input.is_key_pressed(key_name)
        now = time.perf_counter()

        prev = self._key_states.get(key_name, {"pressed": False, "time": 0})

        if pressed and not prev["pressed"]:
            if now - prev["time"] > self._debounce:
                self._key_states[key_name] = {"pressed": True, "time": now}
                return True

        if not pressed:
            self._key_states[key_name] = {"pressed": False, "time": prev["time"]}

        return False
