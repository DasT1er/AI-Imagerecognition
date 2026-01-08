"""
Visual Overlay System
=====================
Zeigt LIVE was der Bot sieht und denkt!

Features:
- Enemy Detection Boxes (wie Aimbot)
- Threat Level Indicator
- Next Action Display
- Game State Info (HP, Ammo, etc.)
- Action Probabilities
- FPS Counter

User sieht GENAU was der Bot macht!
"""

import cv2
import numpy as np
from typing import List, Dict, Any, Tuple
import time


class VisualOverlay:
    """
    Creates visual overlay for bot vision

    Shows:
    - Enemy bounding boxes (RED = body, YELLOW = head)
    - Crosshair with target lock
    - Game state (HP, armor, ammo, money)
    - Threat level bar
    - Next action
    - Action probabilities
    - FPS
    """

    def __init__(self, window_name="CS2 Bot Vision"):
        """
        Initialize overlay

        Args:
            window_name: OpenCV window name
        """
        self.window_name = window_name
        self.last_frame_time = time.time()
        self.fps = 0

        # Action names
        self.action_names = [
            "Idle", "Forward", "Back", "Left", "Right",
            "Fwd-Left", "Fwd-Right", "Back-Left", "Back-Right",
            "Jump", "Crouch", "Walk", "SHOOT", "Reload",
            "Weapon 1", "Weapon 2", "Weapon 3",
            "Buy Rifle", "Buy Armor", "Buy Kit", "Use/Plant"
        ]

        # Colors
        self.COLOR_HEAD = (0, 255, 255)      # Yellow
        self.COLOR_BODY = (0, 0, 255)        # Red
        self.COLOR_LEGS = (255, 0, 0)        # Blue
        self.COLOR_CROSSHAIR = (0, 255, 0)   # Green
        self.COLOR_TARGET = (0, 0, 255)      # Red (target lock)
        self.COLOR_TEXT = (255, 255, 255)    # White
        self.COLOR_BG = (0, 0, 0)            # Black

        print(f"👁️  Visual Overlay initialized: {window_name}")

    def draw(
        self,
        screenshot: np.ndarray,
        detections: List[Dict],
        game_state: Any,
        action: int,
        action_probs: np.ndarray = None,
        target_pos: Tuple[int, int] = None
    ) -> np.ndarray:
        """
        Draw overlay on screenshot

        Args:
            screenshot: Screenshot image (BGR)
            detections: Enemy detections from YOLO
            game_state: Game state object
            action: Current action
            action_probs: Action probabilities (optional)
            target_pos: Target position for crosshair

        Returns:
            Image with overlay
        """
        # Copy image
        overlay = screenshot.copy()

        # Draw enemy boxes
        overlay = self._draw_detections(overlay, detections)

        # Draw crosshair
        overlay = self._draw_crosshair(overlay, target_pos)

        # Draw HUD
        overlay = self._draw_hud(overlay, game_state, action, action_probs, detections)

        # Calculate FPS
        current_time = time.time()
        self.fps = 1.0 / (current_time - self.last_frame_time + 1e-6)
        self.last_frame_time = current_time

        return overlay

    def _draw_detections(self, img: np.ndarray, detections: List[Dict]) -> np.ndarray:
        """Draw enemy detection boxes"""
        for det in detections:
            bbox = det['bbox']
            x1, y1, x2, y2 = map(int, bbox)

            class_name = det['class']
            conf = det['conf']
            is_head = det['is_head']

            # Color based on body part
            if 'head' in class_name.lower():
                color = self.COLOR_HEAD
                thickness = 3  # Heads are important!
            elif 'body' in class_name.lower():
                color = self.COLOR_BODY
                thickness = 2
            else:  # Legs
                color = self.COLOR_LEGS
                thickness = 2

            # Draw box
            cv2.rectangle(img, (x1, y1), (x2, y2), color, thickness)

            # Draw label
            label = f"{class_name} {conf:.2f}"
            (label_w, label_h), _ = cv2.getTextSize(
                label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1
            )

            # Background for label
            cv2.rectangle(
                img,
                (x1, y1 - label_h - 5),
                (x1 + label_w + 5, y1),
                color,
                -1
            )

            # Label text
            cv2.putText(
                img,
                label,
                (x1 + 2, y1 - 3),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 0, 0),
                1
            )

            # Draw center dot
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2
            cv2.circle(img, (center_x, center_y), 3, color, -1)

        return img

    def _draw_crosshair(self, img: np.ndarray, target_pos: Tuple[int, int] = None) -> np.ndarray:
        """Draw crosshair with target lock"""
        h, w = img.shape[:2]
        center_x, center_y = w // 2, h // 2

        # Default crosshair (green)
        color = self.COLOR_CROSSHAIR
        size = 20

        # Draw crosshair
        cv2.line(img, (center_x - size, center_y), (center_x + size, center_y), color, 2)
        cv2.line(img, (center_x, center_y - size), (center_x, center_y + size), color, 2)
        cv2.circle(img, (center_x, center_y), 3, color, -1)

        # Target lock indicator
        if target_pos is not None:
            target_x, target_y = target_pos

            # Draw line to target
            cv2.line(img, (center_x, center_y), (target_x, target_y), self.COLOR_TARGET, 2)

            # Draw target marker
            cv2.circle(img, (target_x, target_y), 10, self.COLOR_TARGET, 2)
            cv2.line(img, (target_x - 15, target_y), (target_x + 15, target_y), self.COLOR_TARGET, 2)
            cv2.line(img, (target_x, target_y - 15), (target_x, target_y + 15), self.COLOR_TARGET, 2)

            # Distance to target
            dist = np.sqrt((target_x - center_x)**2 + (target_y - center_y)**2)
            cv2.putText(
                img,
                f"{dist:.0f}px",
                (target_x + 15, target_y - 15),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                self.COLOR_TARGET,
                2
            )

        return img

    def _draw_hud(
        self,
        img: np.ndarray,
        game_state: Any,
        action: int,
        action_probs: np.ndarray,
        detections: List[Dict]
    ) -> np.ndarray:
        """Draw HUD overlay"""
        h, w = img.shape[:2]

        # Top-left: Game State
        y_offset = 30
        self._draw_text_with_bg(img, "GAME STATE", 10, y_offset, self.COLOR_TEXT, scale=0.6, thickness=2)
        y_offset += 30

        self._draw_text_with_bg(img, f"HP: {int(game_state.hp)}", 10, y_offset, (0, 255, 0) if game_state.hp > 50 else (0, 0, 255))
        y_offset += 25

        self._draw_text_with_bg(img, f"Armor: {int(game_state.armor)}", 10, y_offset, self.COLOR_TEXT)
        y_offset += 25

        self._draw_text_with_bg(img, f"Ammo: {game_state.ammo_current}/{game_state.ammo_reserve}", 10, y_offset, self.COLOR_TEXT)
        y_offset += 25

        self._draw_text_with_bg(img, f"Money: ${game_state.money}", 10, y_offset, (0, 255, 0))
        y_offset += 25

        self._draw_text_with_bg(img, f"Time: {game_state.round_time:.0f}s", 10, y_offset, self.COLOR_TEXT)
        y_offset += 25

        alive_text = "ALIVE" if game_state.is_alive else "DEAD"
        alive_color = (0, 255, 0) if game_state.is_alive else (0, 0, 255)
        self._draw_text_with_bg(img, alive_text, 10, y_offset, alive_color, thickness=2)

        # Top-right: Enemy Info
        y_offset = 30
        enemy_count = len(detections)

        self._draw_text_with_bg(img, "ENEMIES", w - 200, y_offset, self.COLOR_TEXT, scale=0.6, thickness=2)
        y_offset += 30

        self._draw_text_with_bg(img, f"Visible: {enemy_count}", w - 200, y_offset, (0, 0, 255) if enemy_count > 0 else (100, 100, 100))
        y_offset += 25

        # Threat level bar
        threat_level = min(enemy_count * 2, 10)  # 0-10
        self._draw_threat_bar(img, w - 200, y_offset, threat_level)

        # Bottom-left: Current Action
        action_name = self.action_names[action] if action < len(self.action_names) else f"Action {action}"
        action_color = (0, 0, 255) if action == 12 else self.COLOR_TEXT  # Highlight SHOOT

        self._draw_text_with_bg(
            img,
            f"ACTION: {action_name}",
            10,
            h - 60,
            action_color,
            scale=0.7,
            thickness=2
        )

        # Bottom-right: FPS
        self._draw_text_with_bg(
            img,
            f"FPS: {self.fps:.1f}",
            w - 150,
            h - 30,
            self.COLOR_TEXT,
            scale=0.6
        )

        # Action probabilities (if available)
        if action_probs is not None and len(action_probs) > 0:
            self._draw_action_probs(img, action_probs, action)

        return img

    def _draw_text_with_bg(
        self,
        img: np.ndarray,
        text: str,
        x: int,
        y: int,
        color: Tuple[int, int, int],
        scale: float = 0.5,
        thickness: int = 1
    ):
        """Draw text with background"""
        # Get text size
        (text_w, text_h), baseline = cv2.getTextSize(
            text, cv2.FONT_HERSHEY_SIMPLEX, scale, thickness
        )

        # Draw background
        cv2.rectangle(
            img,
            (x - 2, y - text_h - 2),
            (x + text_w + 2, y + baseline),
            (0, 0, 0),
            -1
        )

        # Draw text
        cv2.putText(
            img,
            text,
            (x, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            scale,
            color,
            thickness
        )

    def _draw_threat_bar(self, img: np.ndarray, x: int, y: int, threat: int):
        """Draw threat level bar (0-10)"""
        bar_width = 150
        bar_height = 20

        # Background
        cv2.rectangle(img, (x, y), (x + bar_width, y + bar_height), (50, 50, 50), -1)

        # Filled part
        fill_width = int((threat / 10.0) * bar_width)

        # Color: Green → Yellow → Red
        if threat < 3:
            color = (0, 255, 0)  # Green
        elif threat < 7:
            color = (0, 255, 255)  # Yellow
        else:
            color = (0, 0, 255)  # Red

        cv2.rectangle(img, (x, y), (x + fill_width, y + bar_height), color, -1)

        # Border
        cv2.rectangle(img, (x, y), (x + bar_width, y + bar_height), (255, 255, 255), 1)

        # Text
        cv2.putText(
            img,
            f"Threat: {threat}/10",
            (x, y - 5),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.4,
            (255, 255, 255),
            1
        )

    def _draw_action_probs(self, img: np.ndarray, probs: np.ndarray, current_action: int):
        """Draw top 5 action probabilities"""
        h, w = img.shape[:2]

        # Sort by probability
        top_indices = np.argsort(probs)[-5:][::-1]

        # Draw
        x = 10
        y = h - 200

        self._draw_text_with_bg(img, "TOP ACTIONS:", x, y, self.COLOR_TEXT, scale=0.5)
        y += 25

        for i, idx in enumerate(top_indices):
            prob = probs[idx]
            action_name = self.action_names[idx] if idx < len(self.action_names) else f"Act{idx}"

            # Highlight current action
            color = (0, 255, 0) if idx == current_action else (200, 200, 200)

            text = f"{i+1}. {action_name}: {prob:.1%}"
            self._draw_text_with_bg(img, text, x, y, color, scale=0.4)
            y += 20

    def show(self, img: np.ndarray, wait_key: int = 1):
        """
        Show overlay in window

        Args:
            img: Image to show
            wait_key: OpenCV waitKey time (ms)

        Returns:
            Key pressed (or -1)
        """
        cv2.imshow(self.window_name, img)
        return cv2.waitKey(wait_key)

    def close(self):
        """Close window"""
        cv2.destroyWindow(self.window_name)


if __name__ == "__main__":
    """Test visual overlay"""
    print("\n" + "="*60)
    print("  VISUAL OVERLAY TEST")
    print("="*60 + "\n")

    # Create dummy data
    from dataclasses import dataclass

    @dataclass
    class DummyGameState:
        hp: int = 87
        armor: int = 100
        ammo_current: int = 25
        ammo_reserve: int = 75
        money: int = 3500
        round_time: float = 95.0
        is_alive: bool = True

    # Create test image
    test_img = np.zeros((1080, 1920, 3), dtype=np.uint8)

    # Dummy detections
    detections = [
        {'bbox': [800, 400, 900, 600], 'class': 'CT_Head', 'conf': 0.95, 'is_head': True},
        {'bbox': [1200, 500, 1300, 750], 'class': 'T_Body', 'conf': 0.87, 'is_head': False}
    ]

    # Create overlay
    overlay = VisualOverlay()

    # Draw
    game_state = DummyGameState()
    action = 12  # SHOOT
    action_probs = np.random.rand(20)
    action_probs /= action_probs.sum()
    target_pos = (850, 450)  # Aiming at head

    result = overlay.draw(
        test_img,
        detections,
        game_state,
        action,
        action_probs,
        target_pos
    )

    print("Showing overlay... Press any key to close")
    overlay.show(result, wait_key=0)
    overlay.close()

    print("\n✅ Test complete!")