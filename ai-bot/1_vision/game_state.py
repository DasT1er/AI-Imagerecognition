"""
Game State Detector
===================
Extrahiert Game Info vom Screen:
- HP (Health Points)
- Armor
- Ammo (Current/Reserve)
- Money
- Round Time
- Bomb Status

Nutzt Template Matching und OCR für UI-Elemente.
"""

import cv2
import numpy as np
from PIL import Image, ImageGrab
from dataclasses import dataclass

# Try to import tesseract (optional)
try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    print("⚠️  Tesseract OCR nicht installiert - Game State Detection deaktiviert")
    print("   Bot funktioniert trotzdem! (nutzt nur visuelle Infos)")

@dataclass
class GameState:
    """Complete game state"""
    hp: int = 100
    armor: int = 0
    ammo_current: int = 30
    ammo_reserve: int = 90
    money: int = 800
    round_time: float = 115.0
    has_bomb: bool = False
    is_alive: bool = True


class GameStateDetector:
    """
    Detects CS2 game state from screen

    UI Regions (1920x1080):
    - HP: Bottom left (50, 980, 150, 1060)
    - Armor: Bottom left (160, 980, 260, 1060)
    - Ammo: Bottom right (1650, 950, 1870, 1060)
    - Money: Top center (850, 10, 1070, 60)
    """

    def __init__(self, resolution=(1920, 1080)):
        """
        Initialize detector

        Args:
            resolution: Screen resolution (width, height)
        """
        self.width, self.height = resolution

        # UI regions (relative to resolution)
        self.regions = self._calculate_regions()

        # OCR config
        self.tesseract_config = '--psm 7 -c tessedit_char_whitelist=0123456789$'

        print("🎮 Game State Detector initialized")
        print(f"   Resolution: {self.width}x{self.height}")

        if not TESSERACT_AVAILABLE:
            print("   ⚠️  OCR deaktiviert - nutzt Default-Werte")

    def _calculate_regions(self):
        """Calculate UI regions based on resolution"""
        # Scale factors
        sx = self.width / 1920
        sy = self.height / 1080

        return {
            'hp': (
                int(50 * sx), int(980 * sy),
                int(150 * sx), int(1060 * sy)
            ),
            'armor': (
                int(160 * sx), int(980 * sy),
                int(260 * sx), int(1060 * sy)
            ),
            'ammo': (
                int(1650 * sx), int(950 * sy),
                int(1870 * sx), int(1060 * sy)
            ),
            'money': (
                int(850 * sx), int(10 * sy),
                int(1070 * sx), int(60 * sy)
            ),
            'time': (
                int(910 * sx), int(10 * sy),
                int(1010 * sx), int(50 * sy)
            )
        }

    def detect(self, screenshot=None):
        """
        Detect game state from screenshot

        Args:
            screenshot: PIL Image or None (capture new)

        Returns:
            GameState object
        """
        if screenshot is None:
            screenshot = ImageGrab.grab()

        # Convert to cv2 format
        img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

        # Extract each component
        state = GameState()

        try:
            state.hp = self._detect_hp(img)
            state.armor = self._detect_armor(img)
            state.ammo_current, state.ammo_reserve = self._detect_ammo(img)
            state.money = self._detect_money(img)
            state.round_time = self._detect_time(img)
            state.has_bomb = self._detect_bomb(img)
            state.is_alive = self._detect_alive(img)
        except Exception as e:
            print(f"⚠️  Error detecting game state: {e}")

        return state

    def _detect_hp(self, img):
        """Detect HP from bottom left"""
        if not TESSERACT_AVAILABLE:
            return 100  # Default

        x1, y1, x2, y2 = self.regions['hp']
        roi = img[y1:y2, x1:x2]

        # Preprocess for OCR
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)

        # OCR
        text = pytesseract.image_to_string(thresh, config=self.tesseract_config)

        try:
            hp = int(''.join(filter(str.isdigit, text)))
            return max(0, min(100, hp))  # Clamp 0-100
        except:
            return 100  # Default

    def _detect_armor(self, img):
        """Detect armor from bottom left"""
        if not TESSERACT_AVAILABLE:
            return 0  # Default

        x1, y1, x2, y2 = self.regions['armor']
        roi = img[y1:y2, x1:x2]

        # Preprocess
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)

        # OCR
        text = pytesseract.image_to_string(thresh, config=self.tesseract_config)

        try:
            armor = int(''.join(filter(str.isdigit, text)))
            return max(0, min(100, armor))
        except:
            return 0

    def _detect_ammo(self, img):
        """Detect ammo from bottom right"""
        if not TESSERACT_AVAILABLE:
            return 30, 90  # Default

        x1, y1, x2, y2 = self.regions['ammo']
        roi = img[y1:y2, x1:x2]

        # Preprocess
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)

        # OCR
        text = pytesseract.image_to_string(thresh, config=self.tesseract_config)

        try:
            # Format: "30 / 90" or "30/90"
            numbers = [int(x) for x in text.split() if x.isdigit()]
            if len(numbers) >= 2:
                return numbers[0], numbers[1]
            elif len(numbers) == 1:
                return numbers[0], 90
        except:
            pass

        return 30, 90  # Default

    def _detect_money(self, img):
        """Detect money from top center"""
        if not TESSERACT_AVAILABLE:
            return 800  # Default starting money

        x1, y1, x2, y2 = self.regions['money']
        roi = img[y1:y2, x1:x2]

        # Preprocess
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

        # OCR
        text = pytesseract.image_to_string(thresh, config=self.tesseract_config)

        try:
            # Remove $ and spaces
            money_str = ''.join(filter(str.isdigit, text))
            money = int(money_str)
            return max(0, min(16000, money))
        except:
            return 800  # Default starting money

    def _detect_time(self, img):
        """Detect round time from top center"""
        if not TESSERACT_AVAILABLE:
            return 115.0  # Default round time

        x1, y1, x2, y2 = self.regions['time']
        roi = img[y1:y2, x1:x2]

        # Preprocess
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

        # OCR (time format: "1:55")
        text = pytesseract.image_to_string(thresh, config='--psm 7')

        try:
            if ':' in text:
                parts = text.split(':')
                minutes = int(''.join(filter(str.isdigit, parts[0])))
                seconds = int(''.join(filter(str.isdigit, parts[1])))
                return minutes * 60 + seconds
        except:
            pass

        return 115.0  # Default round time

    def _detect_bomb(self, img):
        """Detect if player has bomb (C4 icon visible)"""
        # Check for C4 icon in inventory (simplified)
        # In real implementation, use template matching
        return False  # TODO: Implement template matching

    def _detect_alive(self, img):
        """Detect if player is alive (no spectator UI)"""
        # Check for spectator UI elements (simplified)
        # Gray screen indicates death
        center_region = img[
            self.height//2 - 100:self.height//2 + 100,
            self.width//2 - 100:self.width//2 + 100
        ]

        # If screen is very gray, probably dead
        gray = cv2.cvtColor(center_region, cv2.COLOR_BGR2GRAY)
        mean_brightness = gray.mean()

        return mean_brightness > 50  # Alive if not too dark

    def get_state_vector(self, state):
        """
        Convert GameState to normalized vector for neural network

        Returns:
            numpy array of shape (7,)
        """
        return np.array([
            state.hp / 100.0,           # 0-1
            state.armor / 100.0,         # 0-1
            state.ammo_current / 30.0,   # 0-1 (normalized to AK capacity)
            state.ammo_reserve / 90.0,   # 0-1
            state.money / 16000.0,       # 0-1
            state.round_time / 115.0,    # 0-1
            1.0 if state.is_alive else 0.0  # Binary
        ], dtype=np.float32)


if __name__ == "__main__":
    """Test game state detection"""
    print("\n" + "="*60)
    print("  GAME STATE DETECTOR TEST")
    print("="*60 + "\n")
    print("Instructions:")
    print("  1. Starte CS2")
    print("  2. Gehe ins Spiel")
    print("  3. Dieses Script zeigt dann erkannte Werte\n")

    detector = GameStateDetector()

    print("\nDruecke Ctrl+C zum Beenden\n")

    try:
        import time
        while True:
            state = detector.detect()

            print("\r" + " "*100, end='')  # Clear line
            print(f"\rHP: {state.hp:3d} | Armor: {state.armor:3d} | "
                  f"Ammo: {state.ammo_current:2d}/{state.ammo_reserve:3d} | "
                  f"Money: ${state.money:5d} | "
                  f"Time: {state.round_time:.0f}s | "
                  f"Alive: {'✓' if state.is_alive else '✗'}", end='')

            time.sleep(0.5)  # Update every 0.5s

    except KeyboardInterrupt:
        print("\n\n✅ Test beendet!")
