"""
Human Data Collector
=====================
Zeichnet DICH beim Spielen auf!

Sammelt:
- Screenshots
- Tastatur Inputs (WASD, Crouch, Jump, etc.)
- Maus Movements
- Maus Clicks (Shooting)

Der Bot lernt dann VON DIR!
"""

import time
import os
from datetime import datetime
from pynput import keyboard, mouse
from PIL import ImageGrab
import json
import numpy as np

class HumanDataCollector:
    def __init__(self, output_dir="../../data/human_gameplay"):
        """
        Collect human gameplay data

        Args:
            output_dir: Where to save data
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(f"{output_dir}/screenshots", exist_ok=True)

        # Session ID
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_dir = f"{output_dir}/session_{self.session_id}"
        os.makedirs(self.session_dir, exist_ok=True)
        os.makedirs(f"{self.session_dir}/images", exist_ok=True)

        # State
        self.recording = False
        self.frame_count = 0
        self.data = []

        # Current inputs
        self.keys_pressed = set()
        self.mouse_pos = (0, 0)
        self.mouse_buttons = {'left': False, 'right': False}

        # Listeners
        self.keyboard_listener = None
        self.mouse_listener = None

        print(f"📁 Session: {self.session_id}")
        print(f"💾 Saving to: {self.session_dir}")

    def on_key_press(self, key):
        """Keyboard press callback"""
        try:
            k = key.char
        except AttributeError:
            k = str(key).replace('Key.', '')

        self.keys_pressed.add(k)

        # F9 = Start/Stop recording
        if k == 'f9':
            if self.recording:
                self.stop_recording()
            else:
                self.start_recording()

    def on_key_release(self, key):
        """Keyboard release callback"""
        try:
            k = key.char
        except AttributeError:
            k = str(key).replace('Key.', '')

        self.keys_pressed.discard(k)

    def on_mouse_move(self, x, y):
        """Mouse move callback"""
        self.mouse_pos = (x, y)

    def on_mouse_click(self, x, y, button, pressed):
        """Mouse click callback"""
        button_name = str(button).replace('Button.', '')
        self.mouse_buttons[button_name] = pressed

    def start_recording(self):
        """Start recording"""
        if not self.recording:
            self.recording = True
            self.frame_count = 0
            print(f"\n🔴 RECORDING STARTED!")
            print(f"Spiele jetzt CS2...")
            print(f"Druecke F9 zum Stoppen\n")

    def stop_recording(self):
        """Stop recording"""
        if self.recording:
            self.recording = False
            self.save_session()
            print(f"\n⏹️  RECORDING STOPPED!")
            print(f"✅ {self.frame_count} Frames aufgezeichnet")
            print(f"💾 Gespeichert in: {self.session_dir}\n")

    def capture_frame(self):
        """Capture one frame of data"""
        if not self.recording:
            return

        timestamp = time.time()

        # Screenshot
        screenshot = ImageGrab.grab()
        img_filename = f"frame_{self.frame_count:06d}.png"
        img_path = f"{self.session_dir}/images/{img_filename}"
        screenshot.save(img_path)

        # Input state
        frame_data = {
            'frame': self.frame_count,
            'timestamp': timestamp,
            'image': img_filename,

            # Keyboard
            'keys': {
                'w': 'w' in self.keys_pressed,
                's': 's' in self.keys_pressed,
                'a': 'a' in self.keys_pressed,
                'd': 'd' in self.keys_pressed,
                'space': 'space' in self.keys_pressed,
                'ctrl': 'ctrl' in self.keys_pressed,
                'shift': 'shift' in self.keys_pressed,
                'r': 'r' in self.keys_pressed,
                'e': 'e' in self.keys_pressed,
                '1': '1' in self.keys_pressed,
                '2': '2' in self.keys_pressed,
                '3': '3' in self.keys_pressed,
            },

            # Mouse
            'mouse': {
                'x': self.mouse_pos[0],
                'y': self.mouse_pos[1],
                'left_click': self.mouse_buttons['left'],
                'right_click': self.mouse_buttons.get('right', False),
            }
        }

        self.data.append(frame_data)
        self.frame_count += 1

        # Print progress every 100 frames
        if self.frame_count % 100 == 0:
            print(f"📸 {self.frame_count} frames captured...")

    def save_session(self):
        """Save session data"""
        data_file = f"{self.session_dir}/session_data.json"

        with open(data_file, 'w') as f:
            json.dump({
                'session_id': self.session_id,
                'total_frames': self.frame_count,
                'fps': 10,  # Target FPS
                'data': self.data
            }, f, indent=2)

        print(f"💾 Data saved: {data_file}")

    def run(self, fps=10):
        """
        Run data collection

        Args:
            fps: Frames per second to capture
        """
        print(f"\n{'='*60}")
        print(f"  HUMAN GAMEPLAY DATA COLLECTOR")
        print(f"{'='*60}\n")
        print(f"Instructions:")
        print(f"  1. Starte CS2 (Offline Bots)")
        print(f"  2. Druecke F9 zum Starten der Aufnahme")
        print(f"  3. Spiele 1-2 Runden normal")
        print(f"  4. Druecke F9 zum Stoppen")
        print(f"  5. Wiederhole fuer mehrere Sessions\n")
        print(f"Target: ~10-20 Runden (5000-20000 Frames)\n")
        print(f"Warte auf F9...\n")

        # Start listeners
        self.keyboard_listener = keyboard.Listener(
            on_press=self.on_key_press,
            on_release=self.on_key_release
        )
        self.mouse_listener = mouse.Listener(
            on_move=self.on_mouse_move,
            on_click=self.on_mouse_click
        )

        self.keyboard_listener.start()
        self.mouse_listener.start()

        # Main loop
        frame_time = 1.0 / fps

        try:
            while True:
                start = time.time()

                if self.recording:
                    self.capture_frame()

                # Sleep to maintain FPS
                elapsed = time.time() - start
                sleep_time = max(0, frame_time - elapsed)
                time.sleep(sleep_time)

        except KeyboardInterrupt:
            print(f"\n⚠️  Abgebrochen!")
            if self.recording:
                self.stop_recording()

        finally:
            self.keyboard_listener.stop()
            self.mouse_listener.stop()


if __name__ == "__main__":
    # Get absolute path to data directory (ai-bot/data/human_gameplay)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ai_bot_dir = os.path.abspath(os.path.join(script_dir, '..', '..'))
    output_dir = os.path.join(ai_bot_dir, 'data', 'human_gameplay')

    print(f"\n📂 Saving data to: {output_dir}\n")

    collector = HumanDataCollector(output_dir=output_dir)
    collector.run(fps=10)
