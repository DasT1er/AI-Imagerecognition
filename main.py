"""
CS2 AI Aimbot - Main Entry Point

Usage:
  1. Place your trained YOLO model as models/best.pt
  2. Run: python main.py
  3. Select monitor, adjust settings in GUI
  4. Click Start

Hotkeys (while running):
  F1   - Toggle aimbot on/off
  F12  - Panic key (stop bot)
"""
import sys
import os
import time
import threading

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config
from core.capture import ScreenCapture
from core.detector import YOLODetector
from core.aim import AimEngine
from core.input_handler import InputHandler, HotkeyManager
from core.triggerbot import Triggerbot
from gui.app import AimbotGUI


def bot_loop(config, gui: AimbotGUI, stop_event: threading.Event):
    """
    Main bot loop. Runs in a background thread.
    Captures screen, detects, aims, and sends preview frames to GUI.
    """
    # Resolve model path
    model_path = config["model_path"]
    if not os.path.isabs(model_path):
        model_path = os.path.join(os.path.dirname(__file__), model_path)

    if not os.path.exists(model_path):
        print(f"[!] Model not found: {model_path}")
        gui.after(0, lambda: gui._on_stop())
        gui.after(0, lambda: gui._flash_status(
            f"Model not found: {model_path}", "#ff5555"))
        return

    # Init detector
    print(f"[+] Loading model: {model_path} (device={config['device']})")
    gui.after(0, lambda: gui._update_status("Loading model...", "#ffaa55"))

    try:
        detector = YOLODetector(
            model_path=model_path,
            device=config["device"],
            conf=config["confidence_threshold"],
            imgsz=config["imgsz"],
            half=config["half_precision"],
            verbose=config["verbose"],
        )
    except Exception as e:
        print(f"[!] Failed to load model: {e}")
        gui.after(0, lambda: gui._on_stop())
        gui.after(0, lambda: gui._flash_status(f"Model error: {e}", "#ff5555"))
        return

    print(f"[+] Model loaded")

    # Init capture
    capture = ScreenCapture(
        width=config["detection_region_width"],
        height=config["detection_region_height"],
        monitor_index=config.get("monitor_index", 1),
    )

    input_handler = InputHandler()
    hotkeys = HotkeyManager(input_handler)
    aim_engine = AimEngine(config)
    triggerbot = Triggerbot(config)

    # Optional: in-game overlay
    overlay = None
    if config["overlay_enabled"]:
        try:
            from core.overlay import Overlay
            overlay = Overlay(config)
            overlay.init()
            print("[+] In-game overlay initialized")
        except Exception as e:
            print(f"[!] Overlay failed (non-critical): {e}")
            overlay = None

    gui.after(0, lambda: gui._update_status("Running", "#55ff55"))
    print("[+] Bot running")

    fps = 0.0
    frame_count = 0
    fps_timer = time.perf_counter()

    try:
        while not stop_event.is_set():
            loop_start = time.perf_counter()

            # --- Hotkeys ---
            if hotkeys.is_just_pressed(config["panic_key"]):
                print("[!] Panic key - stopping")
                gui.after(0, lambda: gui._on_stop())
                break

            if hotkeys.is_just_pressed(config["toggle_key"]):
                config["enabled"] = not config["enabled"]
                new_val = config["enabled"]
                gui.after(0, lambda v=new_val: gui.aim_enabled_var.set(v))
                status = "ON" if config["enabled"] else "OFF"
                print(f"[*] Aimbot: {status}")
                if not config["enabled"]:
                    aim_engine.reset()

            # --- Update capture settings from GUI ---
            capture.set_monitor(config.get("monitor_index", 1))
            capture.set_region_size(
                config["detection_region_width"],
                config["detection_region_height"],
            )
            detector.set_confidence(config["confidence_threshold"])

            # --- Screen capture ---
            frame = capture.grab()
            screen_center = (capture.center_x, capture.center_y)
            offset = capture.offset

            # --- Detection ---
            detections = detector.detect(frame, config["target_classes"])

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

                if should_aim and target is not None:
                    dx, dy = aim_engine.compute_move(target, screen_center)
                    input_handler.move_mouse_relative(dx, dy)

                # Triggerbot
                if config["triggerbot_enabled"]:
                    trig_key = config["triggerbot_key"]
                    if trig_key and input_handler.is_key_pressed(trig_key):
                        if triggerbot.check_trigger(
                                detections, screen_center, offset):
                            input_handler.click()

            # --- Update GUI preview ---
            gui.update_preview(
                frame=frame,
                detections=detections,
                fps=fps,
                inference_ms=detector.inference_time,
                capture_offset=offset,
                screen_center=screen_center,
                target=target,
            )

            # --- In-game overlay ---
            if overlay is not None and config["overlay_enabled"]:
                try:
                    overlay.process_events()
                    overlay.render(
                        detections=detections,
                        capture_offset=offset,
                        screen_center=screen_center,
                        target=target,
                        fps=fps,
                        inference_ms=detector.inference_time,
                        enabled=config["enabled"],
                    )
                except Exception:
                    pass

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

    except Exception as e:
        print(f"[!] Bot error: {e}")
    finally:
        if overlay is not None:
            try:
                overlay.destroy()
            except Exception:
                pass
        print("[+] Bot stopped")


def main():
    print("=" * 50)
    print("  CS2 AI AIMBOT")
    print("=" * 50)
    print()

    config = Config()
    print("[+] Config loaded")

    # Create GUI
    gui = AimbotGUI(config)
    gui.protocol("WM_DELETE_WINDOW", gui.on_close)

    # Set callbacks
    def on_start(stop_event):
        bot_loop(config, gui, stop_event)

    gui.on_start = on_start
    gui.on_stop = lambda: None  # Stop is handled via stop_event

    print("[+] GUI ready")
    print()

    # Run GUI main loop (blocks until window closes)
    gui.mainloop()

    config.save()
    print("[+] Goodbye.")


if __name__ == "__main__":
    main()
