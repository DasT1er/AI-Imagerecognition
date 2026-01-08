"""
Keyboard Actions - WASD, Jump, Crouch, etc.
============================================
Bot Bewegungs-Steuerung
"""

import pyautogui
import time
from enum import Enum

class Movement(Enum):
    """Movement Actions"""
    FORWARD = 'w'
    BACKWARD = 's'
    LEFT = 'a'
    RIGHT = 'd'
    JUMP = 'space'
    CROUCH = 'ctrl'
    WALK = 'shift'
    NONE = None

class KeyboardController:
    def __init__(self):
        """Keyboard Controller for CS2"""
        self.pressed_keys = set()
        pyautogui.PAUSE = 0.0  # No delay

    def press(self, key):
        """Press a key"""
        if key and key not in self.pressed_keys:
            pyautogui.keyDown(key)
            self.pressed_keys.add(key)

    def release(self, key):
        """Release a key"""
        if key and key in self.pressed_keys:
            pyautogui.keyUp(key)
            self.pressed_keys.discard(key)

    def release_all(self):
        """Release all keys"""
        for key in list(self.pressed_keys):
            pyautogui.keyUp(key)
        self.pressed_keys.clear()

    def move(self, forward=0.0, strafe=0.0, jump=False, crouch=False, walk=False):
        """
        Move with analog control

        Args:
            forward: -1 (backward) to +1 (forward)
            strafe: -1 (left) to +1 (right)
            jump: bool
            crouch: bool
            walk: bool
        """
        # Release movement keys
        for key in ['w', 's', 'a', 'd']:
            if key in self.pressed_keys:
                self.release(key)

        # Forward/Backward
        if forward > 0.3:
            self.press('w')
        elif forward < -0.3:
            self.press('s')

        # Strafe
        if strafe > 0.3:
            self.press('d')
        elif strafe < -0.3:
            self.press('a')

        # Jump
        if jump:
            self.tap('space')

        # Crouch
        if crouch and 'ctrl' not in self.pressed_keys:
            self.press('ctrl')
        elif not crouch and 'ctrl' in self.pressed_keys:
            self.release('ctrl')

        # Walk
        if walk and 'shift' not in self.pressed_keys:
            self.press('shift')
        elif not walk and 'shift' in self.pressed_keys:
            self.release('shift')

    def tap(self, key, duration=0.05):
        """Quick tap (for jump, reload, etc.)"""
        pyautogui.press(key, _pause=False)

    def reload(self):
        """Reload weapon"""
        self.tap('r')

    def switch_weapon(self, weapon_slot=1):
        """
        Switch weapon

        Args:
            weapon_slot: 1 (primary), 2 (secondary), 3 (knife)
        """
        self.tap(str(weapon_slot))

    def use(self):
        """Use/Plant/Defuse"""
        self.tap('e')

    def drop_weapon(self):
        """Drop current weapon"""
        self.tap('g')


if __name__ == "__main__":
    print("🎮 Testing Keyboard Controller...")

    kb = KeyboardController()

    print("\nTest 1: Move forward")
    kb.move(forward=1.0)
    time.sleep(0.5)

    print("Test 2: Strafe right")
    kb.move(strafe=1.0)
    time.sleep(0.5)

    print("Test 3: Jump")
    kb.move(jump=True)
    time.sleep(0.2)

    print("Test 4: Crouch")
    kb.move(crouch=True)
    time.sleep(0.5)

    print("Test 5: Release all")
    kb.release_all()

    print("\n✅ Keyboard Controller working!")
