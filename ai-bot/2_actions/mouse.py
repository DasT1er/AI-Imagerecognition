"""
Mouse Actions - Aiming, Shooting
=================================
Bot Aim Control
"""

import pyautogui
import win32api
import win32con
import time

class MouseController:
    def __init__(self, sensitivity=1.0, screen_center=(960, 540)):
        """
        Mouse Controller for CS2

        Args:
            sensitivity: Mouse sensitivity multiplier
            screen_center: Crosshair position (usually screen center)
        """
        self.sensitivity = sensitivity
        self.screen_center = screen_center
        self.shooting = False

        pyautogui.PAUSE = 0.0

    def move_to(self, x, y, smooth=True, speed=0.1):
        """
        Move crosshair to position

        Args:
            x, y: Target position
            smooth: Use smooth movement
            speed: Movement speed (0-1)
        """
        if smooth:
            pyautogui.moveTo(x, y, duration=speed, _pause=False)
        else:
            pyautogui.moveTo(x, y, _pause=False)

    def move_relative(self, dx, dy):
        """
        Move mouse relative

        Args:
            dx, dy: Pixels to move
        """
        dx = int(dx * self.sensitivity)
        dy = int(dy * self.sensitivity)

        # Windows API für präzises Movement
        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, dx, dy, 0, 0)

    def aim_at_target(self, target_pos, smooth=True):
        """
        Aim at target

        Args:
            target_pos: (x, y) position to aim at
            smooth: Smooth or instant aim

        Returns:
            distance: Distance moved
        """
        target_x, target_y = target_pos

        # Berechne Delta
        dx = target_x - self.screen_center[0]
        dy = target_y - self.screen_center[1]

        distance = (dx**2 + dy**2) ** 0.5

        if smooth:
            # Smooth aim (realistischer)
            steps = max(1, int(distance / 20))
            for i in range(steps):
                self.move_relative(dx / steps, dy / steps)
                time.sleep(0.001)
        else:
            # Instant aim (für testing)
            self.move_relative(dx, dy)

        return distance

    def shoot(self, duration=0.05):
        """
        Single shot

        Args:
            duration: How long to hold mouse button
        """
        pyautogui.mouseDown(button='left', _pause=False)
        time.sleep(duration)
        pyautogui.mouseUp(button='left', _pause=False)

    def burst(self, shots=3, delay=0.1):
        """
        Burst fire

        Args:
            shots: Number of shots
            delay: Delay between shots
        """
        for _ in range(shots):
            self.shoot(duration=0.05)
            time.sleep(delay)

    def spray(self, duration=1.0, control_pattern=None):
        """
        Spray (hold down)

        Args:
            duration: How long to spray
            control_pattern: Optional recoil control pattern [(dx, dy), ...]
        """
        pyautogui.mouseDown(button='left', _pause=False)
        self.shooting = True

        start = time.time()
        pattern_idx = 0

        while time.time() - start < duration and self.shooting:
            # Recoil control
            if control_pattern and pattern_idx < len(control_pattern):
                dx, dy = control_pattern[pattern_idx]
                self.move_relative(dx, dy)
                pattern_idx += 1

            time.sleep(0.01)

        pyautogui.mouseUp(button='left', _pause=False)
        self.shooting = False

    def stop_shooting(self):
        """Stop shooting immediately"""
        self.shooting = False
        pyautogui.mouseUp(button='left', _pause=False)

    def right_click(self):
        """Right click (zoom, alt fire)"""
        pyautogui.click(button='right', _pause=False)


# AK-47 Recoil Pattern (simplified)
AK47_PATTERN = [
    (0, 5), (0, 6), (0, 7), (0, 8),  # Up
    (-2, 5), (-3, 4), (-4, 3),        # Left
    (3, 2), (4, 2), (5, 1),           # Right
    (-2, 0), (-2, 0), (-2, 0)         # Back left
]

# M4A4 Recoil Pattern (simplified)
M4A4_PATTERN = [
    (0, 4), (0, 5), (0, 5), (0, 6),   # Up
    (-1, 4), (-2, 3), (-2, 2),         # Slight left
    (1, 2), (2, 1), (2, 1),            # Right
    (-1, 0), (-1, 0), (-1, 0)          # Back
]


if __name__ == "__main__":
    print("🎯 Testing Mouse Controller...")

    mouse = MouseController()

    print("\nTest 1: Move to center")
    mouse.move_to(960, 540)
    time.sleep(0.5)

    print("Test 2: Aim at target (1100, 600)")
    distance = mouse.aim_at_target((1100, 600), smooth=True)
    print(f"  Moved {distance:.1f} pixels")
    time.sleep(0.5)

    print("Test 3: Single shot")
    mouse.shoot()
    time.sleep(0.5)

    print("Test 4: Burst (3 shots)")
    mouse.burst(shots=3)
    time.sleep(0.5)

    print("\n✅ Mouse Controller working!")
    print("\n⚠️  Make sure CS2 is NOT active during testing!")
