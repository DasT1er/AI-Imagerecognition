"""
Test Bot
========
Testet den trainierten Bot in CS2!

Der Bot:
- Lädt das trainierte Model
- Macht Screenshots
- Entscheidet Actions
- Spielt CS2!

Drücke F9 zum Stoppen.
"""

import torch
import numpy as np
from PIL import Image, ImageGrab
import time
import sys
import os
from pynput import keyboard as pynput_keyboard

# Add to path
base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(base_dir)
sys.path.append(os.path.join(base_dir, '3_learning', 'imitation'))
sys.path.append(os.path.join(base_dir, '2_actions'))
sys.path.append(os.path.join(base_dir, '1_vision'))

from train_imitation import ImitationNetwork
from keyboard import KeyboardController
from mouse import MouseController
from detector import EnemyDetector


class CS2Bot:
    """
    CS2 Bot that plays using trained model
    """

    def __init__(self, model_path, my_team='CT', screen_size=(84, 84), device=None):
        """
        Initialize bot

        Args:
            model_path: Path to trained model (.pt file)
            my_team: 'CT' or 'T'
            screen_size: Image size for model
            device: 'cuda' or 'cpu'
        """
        self.my_team = my_team
        self.screen_size = screen_size

        # Device
        if device is None:
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        else:
            self.device = torch.device(device)

        print(f"🤖 CS2 Bot initializing...")
        print(f"   Team: {my_team}")
        print(f"   Device: {self.device}")
        print(f"   Model: {model_path}\n")

        # Load model
        try:
            self.model = ImitationNetwork(num_actions=20, screen_size=screen_size)
            checkpoint = torch.load(model_path, map_location=self.device)
            self.model.load_state_dict(checkpoint['model_state_dict'])
            self.model.to(self.device)
            self.model.eval()
            print("✅ Model loaded successfully!\n")
        except Exception as e:
            print(f"❌ FEHLER beim Model-Laden: {e}\n")
            print("Das Model ist möglicherweise beschädigt!")
            print("Bitte trainiere das Model neu:\n")
            print("  START_BOT.bat → Option [2] - Model trainieren\n")
            input("Drücke Enter zum Beenden...")
            sys.exit(1)

        # Controllers
        self.keyboard_ctrl = KeyboardController()
        self.mouse_ctrl = MouseController()

        # Enemy detector (optional - used for visual info only)
        try:
            self.enemy_detector = EnemyDetector()
            print("✅ Enemy Detector loaded (optional)\n")
        except Exception as e:
            print(f"⚠️  Enemy Detector nicht verfügbar: {e}")
            print("   Bot funktioniert trotzdem!\n")
            self.enemy_detector = None

        # State
        self.running = False
        self.frame_count = 0
        self.action_counts = [0] * 20

        # Keyboard listener for F9 stop
        self.keyboard_listener = None

        # Action names for display
        self.action_names = [
            "Idle", "Forward", "Back", "Left", "Right",
            "Forward-Left", "Forward-Right", "Back-Left", "Back-Right",
            "Jump", "Crouch", "Walk", "Shoot", "Reload",
            "Weapon 1", "Weapon 2", "Weapon 3",
            "Buy Rifle", "Buy Armor", "Buy Defuse", "Use/Plant"
        ]

    def preprocess_image(self, image):
        """
        Preprocess screenshot for model

        Args:
            image: PIL Image

        Returns:
            torch.Tensor of shape [1, 3, H, W]
        """
        # Resize
        img = image.resize(self.screen_size, Image.Resampling.LANCZOS)

        # To tensor
        img_array = np.array(img, dtype=np.float32) / 255.0
        img_tensor = torch.from_numpy(img_array).permute(2, 0, 1)  # HWC -> CHW

        # Add batch dimension
        img_tensor = img_tensor.unsqueeze(0)

        return img_tensor.to(self.device)

    def predict_action(self, image):
        """
        Predict action from image

        Args:
            image: PIL Image

        Returns:
            int: Action ID (0-19)
        """
        # Preprocess
        img_tensor = self.preprocess_image(image)

        # Predict
        with torch.no_grad():
            logits = self.model(img_tensor)
            action = logits.argmax(dim=1).item()

        return action

    def execute_action(self, action, screenshot=None):
        """
        Execute action in game

        Args:
            action: int (0-19)
            screenshot: PIL Image (for enemy detection)
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

        # Special actions
        elif action == 8:
            self.keyboard_ctrl.move(jump=True)
        elif action == 9:
            self.keyboard_ctrl.move(crouch=True)
        elif action == 10:
            self.keyboard_ctrl.move(walk=True)

        # Shoot (with enemy detection)
        elif action == 11:
            if screenshot:
                # Detect enemies
                screenshot_np = np.array(screenshot)
                detections = self.enemy_detector.detect(screenshot_np, my_team=self.my_team)
                closest = self.enemy_detector.get_closest_enemy(detections)

                if closest:
                    # Aim at enemy
                    target_pos = closest['center']
                    self.mouse_ctrl.aim_at_target(target_pos, smooth=True)

            # Shoot
            self.mouse_ctrl.shoot()

        # Reload
        elif action == 12:
            self.keyboard_ctrl.reload()

        # Switch weapon
        elif action == 13:
            self.keyboard_ctrl.switch_weapon(1)
        elif action == 14:
            self.keyboard_ctrl.switch_weapon(2)
        elif action == 15:
            self.keyboard_ctrl.switch_weapon(3)

        # Economy (simplified)
        elif action == 16:
            # Buy rifle
            self.keyboard_ctrl.press('b')
            time.sleep(0.1)
            self.keyboard_ctrl.press('4')
            time.sleep(0.1)
            self.keyboard_ctrl.press('2')
        elif action == 17:
            # Buy armor
            self.keyboard_ctrl.press('b')
            time.sleep(0.1)
            self.keyboard_ctrl.press('6')
        elif action == 18:
            # Buy defuse kit
            if self.my_team == 'CT':
                self.keyboard_ctrl.press('b')
                time.sleep(0.1)
                self.keyboard_ctrl.press('8')
        elif action == 19:
            # Use/Plant
            self.keyboard_ctrl.use()

        # Track action
        self.action_counts[action] += 1

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
        print("  CS2 BOT ACTIVE")
        print("="*60 + "\n")
        print("Instructions:")
        print("  1. Starte CS2 (Offline Bots)")
        print("  2. Bot spielt automatisch!")
        print("  3. Druecke F9 zum Stoppen\n")
        print("Starte in 3 Sekunden...\n")

        time.sleep(3)

        self.running = True
        self.frame_count = 0

        # Start keyboard listener
        self.keyboard_listener = pynput_keyboard.Listener(on_press=self.on_key_press)
        self.keyboard_listener.start()

        frame_time = 1.0 / fps

        print("🤖 BOT GESTARTET!\n")

        try:
            while self.running:
                start_time = time.time()

                # Capture screenshot
                screenshot = ImageGrab.grab()

                # Predict action
                action = self.predict_action(screenshot)

                # Execute action
                self.execute_action(action, screenshot)

                # Print status
                self.frame_count += 1
                if self.frame_count % 100 == 0:
                    self._print_status()

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

    def _print_status(self):
        """Print current status"""
        # Get last action
        last_action = np.argmax(self.action_counts)
        action_name = self.action_names[last_action]

        print(f"🤖 Frame {self.frame_count}: Last action = {action_name}")


if __name__ == "__main__":
    """Test bot"""
    print("\n" + "="*60)
    print("  CS2 BOT - IMITATION LEARNING")
    print("="*60 + "\n")

    # Get absolute path to model (parent_dir/models/)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)  # Go one level up from ai-bot/
    model_path = os.path.join(parent_dir, 'models', 'best_model.pt')

    print(f"📂 Looking for model: {model_path}\n")

    if not os.path.exists(model_path):
        print(f"❌ Model nicht gefunden: {model_path}\n")
        print("Bitte zuerst Model trainieren:")
        print("  1. START_BOT.bat → Option [1] - Gameplay aufnehmen")
        print("  2. START_BOT.bat → Option [2] - Model trainieren")
        print("  3. START_BOT.bat → Option [3] - Bot testen\n")
        print("FEHLER: Kein trainiertes Model vorhanden!\n")
        input("Drücke Enter zum Beenden...")
        sys.exit(1)

    # Get team
    print("Welches Team?")
    print("  [1] CT (Counter-Terrorists)")
    print("  [2] T (Terrorists)")

    choice = input("\nWähle (1 oder 2): ").strip()

    if choice == '2':
        my_team = 'T'
    else:
        my_team = 'CT'

    print(f"\n✅ Team gewählt: {my_team}\n")

    # Create bot
    bot = CS2Bot(
        model_path=model_path,
        my_team=my_team,
        screen_size=(84, 84)
    )

    # Start
    bot.start(fps=20)
