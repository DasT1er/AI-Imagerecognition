"""
CS2 AI Aimbot - Main Entry Point

Hotkeys:
  F1      - Toggle aimbot on/off
  INSERT  - Toggle settings menu
  F12     - Panic key (kill everything)

Usage:
  1. Place your trained YOLO model as models/best.pt
  2. Run: python main.py
  3. Press F1 to enable
"""
import sys
import os
import time
import pygame

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config
from core.capture import ScreenCapture
from core.detector import YOLODetector
from core.aim import AimEngine
from core.input_handler import InputHandler, HotkeyManager
from core.overlay import Overlay
from core.menu import Menu
from core.triggerbot import Triggerbot


def main():
    print("=" * 50)
    print("  CS2 AI AIMBOT")
    print("=" * 50)
    print()

    # Load config
    config = Config()
    print(f"[+] Config loaded")

    # Resolve model path
    model_path = config["model_path"]
    if not os.path.isabs(model_path):
        model_path = os.path.join(os.path.dirname(__file__), model_path)

    if not os.path.exists(model_path):
        print(f"[!] Model not found: {model_path}")
        print(f"    Place your YOLO .pt model at: {model_path}")
        print(f"    Or update 'model_path' in settings.json")
        input("Press Enter to exit...")
        return

    # Initialize components
    print(f"[+] Loading YOLO model: {model_path}")
    print(f"    Device: {config['device']}  |  FP16: {config['half_precision']}")

    detector = YOLODetector(
        model_path=model_path,
        device=config["device"],
        conf=config["confidence_threshold"],
        imgsz=config["imgsz"],
        half=config["half_precision"],
        verbose=config["verbose"],
    )
    print(f"[+] Model loaded and warmed up")

    capture = ScreenCapture(
        width=config["detection_region_width"],
        height=config["detection_region_height"],
    )
    print(f"[+] Screen capture ready ({capture.screen_width}x{capture.screen_height})")

    input_handler = InputHandler()
    hotkeys = HotkeyManager(input_handler)
    aim_engine = AimEngine(config)
    triggerbot = Triggerbot(config)

    overlay = Overlay(config)
    overlay.init()
    print(f"[+] Overlay initialized")

    menu = Menu(config)
    menu.init_fonts()

    print()
    print(f"  F1     = Toggle aimbot")
    print(f"  INSERT = Settings menu")
    print(f"  F12    = Panic / Exit")
    print()
    print(f"[*] Running... (aimbot is {'ON' if config['enabled'] else 'OFF'})")

    # Main loop
    fps = 0.0
    frame_count = 0
    fps_timer = time.perf_counter()
    running = True

    try:
        while running:
            loop_start = time.perf_counter()

            # --- Process overlay events ---
            if not overlay.process_events():
                break

            # Process menu keyboard events
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    result = menu.handle_input(event.key)
                    if result == "saved":
                        print("[+] Config saved")
                    elif result == "reset":
                        print("[+] Config reset to defaults")

            # --- Hotkeys ---
            if hotkeys.is_just_pressed(config["panic_key"]):
                print("[!] Panic key pressed - shutting down")
                break

            if hotkeys.is_just_pressed(config["toggle_key"]):
                config["enabled"] = not config["enabled"]
                status = "ON" if config["enabled"] else "OFF"
                print(f"[*] Aimbot: {status}")
                if not config["enabled"]:
                    aim_engine.reset()

            if hotkeys.is_just_pressed(config["menu_key"]):
                menu.toggle()

            # --- Screen capture ---
            frame = capture.grab()
            screen_center = (capture.center_x, capture.center_y)
            offset = capture.offset

            # --- Detection ---
            detections = detector.detect(frame, config["target_classes"])

            # Update confidence threshold if changed from menu
            detector.set_confidence(config["confidence_threshold"])
            capture.set_region_size(
                config["detection_region_width"],
                config["detection_region_height"],
            )

            # --- Aim logic ---
            target = None
            if config["enabled"]:
                target = aim_engine.select_target(
                    detections, screen_center, offset
                )

                should_aim = False
                aim_mode = config["aim_mode"]

                if aim_mode == "trigger":
                    should_aim = input_handler.is_mouse_left_pressed()
                elif aim_mode == "hold":
                    aim_key = config["aim_key"]
                    if aim_key:
                        should_aim = input_handler.is_key_pressed(aim_key)
                    else:
                        should_aim = input_handler.is_mouse_left_pressed()
                elif aim_mode == "always":
                    should_aim = True

                if should_aim and target is not None and not menu.visible:
                    dx, dy = aim_engine.compute_move(target, screen_center)
                    input_handler.move_mouse_relative(dx, dy)

                # Triggerbot
                if config["triggerbot_enabled"] and not menu.visible:
                    trig_key = config["triggerbot_key"]
                    if trig_key and input_handler.is_key_pressed(trig_key):
                        if triggerbot.check_trigger(detections, screen_center, offset):
                            input_handler.click()

            # --- Overlay render ---
            overlay.render(
                detections=detections,
                capture_offset=offset,
                screen_center=screen_center,
                target=target,
                fps=fps,
                inference_ms=detector.inference_time,
                enabled=config["enabled"],
            )

            # Render menu on top
            if menu.visible:
                menu.render(overlay.surface)
                pygame.display.flip()

            # --- FPS tracking ---
            frame_count += 1
            elapsed = time.perf_counter() - fps_timer
            if elapsed >= 1.0:
                fps = frame_count / elapsed
                frame_count = 0
                fps_timer = time.perf_counter()

            # FPS limit
            if config["fps_limit"] > 0:
                target_frame_time = 1.0 / config["fps_limit"]
                frame_time = time.perf_counter() - loop_start
                if frame_time < target_frame_time:
                    time.sleep(target_frame_time - frame_time)

    except KeyboardInterrupt:
        print("\n[!] Interrupted")
    finally:
        overlay.destroy()
        config.save()
        print("[+] Cleanup complete. Goodbye.")


if __name__ == "__main__":
    main()
