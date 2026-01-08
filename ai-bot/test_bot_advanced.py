"""
Advanced CS2 Bot with Aimbot + Visual Overlay
==============================================
PHASE 2 BOT - Mit allen Features!

Features:
- PPO oder Imitation Learning Model
- AIMBOT IMMER AKTIV (perfektes Zielen!)
- VISUAL OVERLAY (siehst was Bot sieht!)
- Gegner-Boxen
- Game State HUD
- Action Display
- Threat Level

Du siehst GENAU was der Bot macht!
"""

import torch
import numpy as np
from PIL import Image, ImageGrab
import time
import sys
import os
from pynput import keyboard
import cv2

# Add to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from learning.imitation.train_imitation import ImitationNetwork
from actions.keyboard import KeyboardController
from actions.mouse import MouseController
from vision.detector import EnemyDetector
from vision.game_state import GameStateDetector
from utils.visual_overlay import VisualOverlay


class AdvancedCS2Bot:
    """
    Advanced CS2 Bot with:
    - AI Model (PPO or Imitation)
    - Integrated Aimbot (ALWAYS ON)
    - Visual Overlay (see what bot sees)
    """

    def __init__(
        self,
        model_path,
        my_team='CT',
        screen_size=(84, 84),
        use_aimbot=True,
        show_overlay=True,
        device=None
    ):
        """
        Initialize advanced bot

        Args:
            model_path: Path to model (.pt or .zip)
            my_team: 'CT' or 'T'
            screen_size: Image size for model
            use_aimbot: Use aimbot for shooting (HIGHLY RECOMMENDED!)
            show_overlay: Show visual overlay
            device: 'cuda' or 'cpu'
        """
        self.my_team = my_team
        self.screen_size = screen_size
        self.use_aimbot = use_aimbot
        self.show_overlay = show_overlay

        # Device
        if device is None:
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        else:
            self.device = torch.device(device)

        print("\n" + "="*60)
        print("  ADVANCED CS2 BOT - Phase 2")
        print("="*60 + "\n")
        print(f"   Team: {my_team}")
        print(f"   Device: {self.device}")
        print(f"   Aimbot: {'ON ✓' if use_aimbot else 'OFF'}")
        print(f"   Visual Overlay: {'ON ✓' if show_overlay else 'OFF'}")
        print(f"   Model: {model_path}\n")

        # Load model
        self.model_type = self._detect_model_type(model_path)
        self.model = self._load_model(model_path)

        print(f"✅ {self.model_type} model loaded!\n")

        # Controllers
        self.keyboard_ctrl = KeyboardController()
        self.mouse_ctrl = MouseController()
        self.enemy_detector = EnemyDetector(my_team=my_team)
        self.game_state_detector = GameStateDetector()

        # Visual overlay
        if show_overlay:
            self.overlay = VisualOverlay(window_name="CS2 Bot Vision")
        else:
            self.overlay = None

        # State
        self.running = False
        self.frame_count = 0
        self.action_counts = [0] * 20
        self.last_action = None
        self.last_action_probs = None

        # Keyboard listener for F9 stop
        self.keyboard_listener = None

        # Action names
        self.action_names = [
            "Idle", "Forward", "Back", "Left", "Right",
            "Forward-Left", "Forward-Right", "Back-Left", "Back-Right",
            "Jump", "Crouch", "Walk", "Shoot", "Reload",
            "Weapon 1", "Weapon 2", "Weapon 3",
            "Buy Rifle", "Buy Armor", "Buy Defuse", "Use/Plant"
        ]

    def _detect_model_type(self, model_path):
        """Detect if PPO or Imitation model"""
        if model_path.endswith('.zip'):
            return "PPO"
        elif model_path.endswith('.pt'):
            return "Imitation"
        else:
            raise ValueError(f"Unknown model type: {model_path}")

    def _load_model(self, model_path):
        """Load model (PPO or Imitation)"""
        if self.model_type == "PPO":
            # Load PPO model
            from stable_baselines3 import PPO
            model = PPO.load(model_path, device=self.device)
            return model

        else:  # Imitation
            # Load imitation model
            model = ImitationNetwork(num_actions=20, screen_size=self.screen_size)
            checkpoint = torch.load(model_path, map_location=self.device)
            model.load_state_dict(checkpoint['model_state_dict'])
            model.to(self.device)
            model.eval()
            return model

    def preprocess_image(self, image):
        """Preprocess screenshot for model"""
        # Resize
        img = image.resize(self.screen_size, Image.Resampling.LANCZOS)

        # To tensor
        img_array = np.array(img, dtype=np.float32) / 255.0
        img_tensor = torch.from_numpy(img_array).permute(2, 0, 1)  # HWC -> CHW

        # Add batch dimension
        img_tensor = img_tensor.unsqueeze(0)

        return img_tensor.to(self.device)

    def predict_action(self, screenshot, game_state, enemies_info):
        """
        Predict action from observations

        Args:
            screenshot: PIL Image
            game_state: GameState object
            enemies_info: Enemy detection info

        Returns:
            action: int
            action_probs: np.ndarray (optional)
        """
        if self.model_type == "PPO":
            # PPO expects Dict observation
            game_state_vector = self.game_state_detector.get_state_vector(game_state)

            obs = {
                'visual': self.preprocess_image(screenshot).cpu().numpy(),
                'game_state': game_state_vector.reshape(1, -1),
                'enemies': enemies_info.reshape(1, -1)
            }

            action, _ = self.model.predict(obs, deterministic=True)
            return int(action), None

        else:  # Imitation
            img_tensor = self.preprocess_image(screenshot)

            with torch.no_grad():
                logits = self.model(img_tensor)
                probs = torch.softmax(logits, dim=1).cpu().numpy()[0]
                action = logits.argmax(dim=1).item()

            return action, probs

    def execute_action(self, action, detections, screenshot=None):
        """
        Execute action with AIMBOT integration

        Args:
            action: int (0-19)
            detections: Enemy detections
            screenshot: PIL Image (for overlay)
        """
        # Release previous keys
        self.keyboard_ctrl.release_all()

        # Movement (0-7)
        if action == 0:
            # Idle
            pass
        elif action == 1:
            self.keyboard_ctrl.move(forward=1.0)
        elif action == 2:
            self.keyboard_ctrl.move(forward=-1.0)
        elif action == 3:
            self.keyboard_ctrl.move(strafe=-1.0)
        elif action == 4:
            self.keyboard_ctrl.move(strafe=1.0)
        elif action == 5:
            self.keyboard_ctrl.move(forward=1.0, strafe=-1.0)
        elif action == 6:
            self.keyboard_ctrl.move(forward=1.0, strafe=1.0)
        elif action == 7:
            self.keyboard_ctrl.move(forward=-1.0, strafe=-1.0)
        elif action == 8:
            self.keyboard_ctrl.move(forward=-1.0, strafe=1.0)  # Back-right

        # Special actions
        elif action == 9:
            self.keyboard_ctrl.move(jump=True)
        elif action == 10:
            self.keyboard_ctrl.move(crouch=True)
        elif action == 11:
            self.keyboard_ctrl.move(walk=True)

        # SHOOT with AIMBOT (most important!)
        elif action == 12:
            if self.use_aimbot and len(detections) > 0:
                # AIMBOT: Aim at closest enemy (prioritize heads!)
                closest = self.enemy_detector.get_closest_enemy(detections)

                if closest:
                    target_pos = closest['center']
                    self.mouse_ctrl.aim_at_target(target_pos, smooth=True)
                    self.current_target = target_pos  # For overlay
                else:
                    self.current_target = None
            else:
                self.current_target = None

            # Shoot
            self.mouse_ctrl.shoot()

        # Reload
        elif action == 13:
            self.keyboard_ctrl.reload()

        # Switch weapon
        elif action == 14:
            self.keyboard_ctrl.switch_weapon(1)
        elif action == 15:
            self.keyboard_ctrl.switch_weapon(2)
        elif action == 16:
            self.keyboard_ctrl.switch_weapon(3)

        # Economy
        elif action == 17:
            # Buy rifle
            self.keyboard_ctrl.press('b')
            time.sleep(0.1)
            self.keyboard_ctrl.press('4')
            time.sleep(0.1)
            self.keyboard_ctrl.press('2')
        elif action == 18:
            # Buy armor
            self.keyboard_ctrl.press('b')
            time.sleep(0.1)
            self.keyboard_ctrl.press('6')
        elif action == 19:
            # Buy defuse kit
            if self.my_team == 'CT':
                self.keyboard_ctrl.press('b')
                time.sleep(0.1)
                self.keyboard_ctrl.press('8')
        elif action == 20:
            # Use/Plant
            self.keyboard_ctrl.use()

        # Track action
        self.action_counts[action] += 1
        self.last_action = action

    def on_key_press(self, key):
        """Keyboard callback"""
        try:
            k = key.char
        except AttributeError:
            k = str(key).replace('Key.', '')

        # F9 = Stop
        if k == 'f9':
            self.stop()

    def start(self, fps=20):
        """
        Start bot

        Args:
            fps: Actions per second
        """
        print("\n" + "="*60)
        print("  ADVANCED BOT ACTIVE")
        print("="*60 + "\n")
        print("Instructions:")
        print("  1. Starte CS2 (Offline Bots)")
        print("  2. Bot spielt mit AIMBOT!")
        print("  3. Sieh Visual Overlay für Bot-Vision")
        print("  4. Druecke F9 zum Stoppen\n")
        print("Starte in 3 Sekunden...\n")

        time.sleep(3)

        self.running = True
        self.frame_count = 0
        self.current_target = None

        # Start keyboard listener
        self.keyboard_listener = keyboard.Listener(on_press=self.on_key_press)
        self.keyboard_listener.start()

        frame_time = 1.0 / fps

        print("🤖 ADVANCED BOT GESTARTET!\n")

        try:
            while self.running:
                start_time = time.time()

                # Capture screenshot
                screenshot = ImageGrab.grab()
                screenshot_np = np.array(screenshot)

                # Detect game state
                game_state = self.game_state_detector.detect(screenshot)

                # Detect enemies
                detections = self.enemy_detector.detect(screenshot_np, my_team=self.my_team)

                # Enemy info vector
                enemy_count = min(len(detections), 5)
                closest = self.enemy_detector.get_closest_enemy(detections)
                threat = self.enemy_detector.get_threat_level(detections) / 10.0

                if closest:
                    dist = np.linalg.norm(
                        np.array(closest['center']) - np.array([960, 540])
                    ) / 1000.0
                    is_head = 1.0 if closest['is_head'] else 0.0
                else:
                    dist = 1.0
                    is_head = 0.0

                enemies_info = np.array([
                    enemy_count / 5.0,
                    dist,
                    is_head,
                    threat,
                    1.0 if enemy_count > 0 else 0.0
                ], dtype=np.float32)

                # Predict action
                action, action_probs = self.predict_action(screenshot, game_state, enemies_info)
                self.last_action_probs = action_probs

                # Execute action
                self.execute_action(action, detections, screenshot)

                # Visual overlay
                if self.overlay:
                    overlay_img = self.overlay.draw(
                        cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR),
                        detections,
                        game_state,
                        action,
                        action_probs,
                        self.current_target
                    )

                    # Show overlay
                    key = self.overlay.show(overlay_img, wait_key=1)

                    # ESC to stop
                    if key == 27:
                        self.stop()

                # Print status
                self.frame_count += 1
                if self.frame_count % 100 == 0:
                    self._print_status(detections, game_state)

                # Maintain FPS
                elapsed = time.time() - start_time
                sleep_time = max(0, frame_time - elapsed)
                time.sleep(sleep_time)

        except KeyboardInterrupt:
            print("\n⚠️  Abgebrochen!")

        finally:
            self.stop()

    def stop(self):
        """Stop bot"""
        if not self.running:
            return

        self.running = False
        self.keyboard_ctrl.release_all()

        if self.keyboard_listener:
            self.keyboard_listener.stop()

        if self.overlay:
            self.overlay.close()

        print("\n\n" + "="*60)
        print("  BOT GESTOPPT")
        print("="*60 + "\n")
        print(f"Total Frames: {self.frame_count}")
        print(f"\nAction Statistics:")

        # Print action distribution
        for i, count in enumerate(self.action_counts):
            if count > 0:
                percentage = 100.0 * count / self.frame_count
                print(f"  [{i:2d}] {self.action_names[i]:15s}: {count:5d} ({percentage:5.1f}%)")

        print("\n✅ Bot beendet!")

    def _print_status(self, detections, game_state):
        """Print current status"""
        action_name = self.action_names[self.last_action] if self.last_action is not None else "None"

        print(f"🤖 Frame {self.frame_count}:")
        print(f"   Action: {action_name}")
        print(f"   Enemies: {len(detections)}")
        print(f"   HP: {game_state.hp} | Ammo: {game_state.ammo_current}/{game_state.ammo_reserve}")


if __name__ == "__main__":
    """Test advanced bot"""
    print("\n" + "="*60)
    print("  ADVANCED CS2 BOT - WITH AIMBOT + VISUALS")
    print("="*60 + "\n")

    # Check for models
    ppo_path = "models/ppo_final.zip"
    imitation_path = "models/best_model.pt"

    print("Available models:")
    if os.path.exists(ppo_path):
        print(f"  [1] PPO Model (Phase 2): {ppo_path} ✓")
    if os.path.exists(imitation_path):
        print(f"  [2] Imitation Model (Phase 1): {imitation_path} ✓")

    # Select model
    model_path = None

    if os.path.exists(ppo_path):
        use_ppo = input("\nUse PPO model? (y/n): ").strip().lower()
        if use_ppo == 'y':
            model_path = ppo_path

    if model_path is None and os.path.exists(imitation_path):
        model_path = imitation_path

    if model_path is None:
        print("\n❌ No model found!")
        print("Please train a model first:")
        print("  Phase 1: python 3_learning/imitation/train_imitation.py")
        print("  Phase 2: python 3_learning/reinforcement/train_ppo_hybrid.py\n")
        sys.exit(1)

    print(f"\n✅ Using model: {model_path}\n")

    # Team selection
    print("Welches Team?")
    print("  [1] CT (Counter-Terrorists)")
    print("  [2] T (Terrorists)")

    choice = input("\nWähle (1 oder 2): ").strip()
    my_team = 'T' if choice == '2' else 'CT'

    print(f"\n✅ Team: {my_team}\n")

    # Aimbot option
    use_aimbot = input("Aimbot aktivieren? (y/n) [EMPFOHLEN]: ").strip().lower()
    use_aimbot = use_aimbot != 'n'  # Default yes

    # Visual overlay option
    show_overlay = input("Visual Overlay zeigen? (y/n) [EMPFOHLEN]: ").strip().lower()
    show_overlay = show_overlay != 'n'  # Default yes

    # Create bot
    bot = AdvancedCS2Bot(
        model_path=model_path,
        my_team=my_team,
        screen_size=(84, 84),
        use_aimbot=use_aimbot,
        show_overlay=show_overlay
    )

    # Start
    bot.start(fps=20)
