"""
Screenshot Methods Test
========================
Testet verschiedene Screenshot-Methoden um die beste für CS2 zu finden!

Methoden:
1. MSS (aktuell) - Schnell aber Farbprofil-Probleme
2. PIL ImageGrab - Bessere Farbgenauigkeit
3. PyAutoGUI - Alternative mit guter Kompatibilität
4. Win32 API - Direkte Windows API (beste Qualität)
"""

import time
import os
from datetime import datetime
from colorama import Fore, init
import numpy as np
import cv2

init(autoreset=True)

def test_mss():
    """MSS Methode (aktuell)"""
    try:
        import mss
        from PIL import Image

        with mss.mss() as sct:
            monitor = sct.monitors[1]
            screenshot = sct.grab(monitor)
            img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
            return np.array(img)
    except Exception as e:
        print(f"{Fore.RED}MSS Fehler: {e}")
        return None

def test_pil_imagegrab():
    """PIL ImageGrab Methode - Bessere Farbprofile"""
    try:
        from PIL import ImageGrab

        img = ImageGrab.grab(all_screens=False)
        return np.array(img)
    except Exception as e:
        print(f"{Fore.RED}PIL ImageGrab Fehler: {e}")
        return None

def test_pyautogui():
    """PyAutoGUI Methode"""
    try:
        import pyautogui

        img = pyautogui.screenshot()
        return np.array(img)
    except Exception as e:
        print(f"{Fore.RED}PyAutoGUI Fehler: {e}")
        return None

def test_win32():
    """Win32 API Methode - Beste Qualität"""
    try:
        import win32gui
        import win32ui
        import win32con
        import win32api
        from PIL import Image

        # Desktop DC
        hdesktop = win32gui.GetDesktopWindow()
        width = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
        height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
        left = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
        top = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)

        desktop_dc = win32gui.GetWindowDC(hdesktop)
        img_dc = win32ui.CreateDCFromHandle(desktop_dc)
        mem_dc = img_dc.CreateCompatibleDC()

        screenshot = win32ui.CreateBitmap()
        screenshot.CreateCompatibleBitmap(img_dc, width, height)
        mem_dc.SelectObject(screenshot)
        mem_dc.BitBlt((0, 0), (width, height), img_dc, (left, top), win32con.SRCCOPY)

        bmpinfo = screenshot.GetInfo()
        bmpstr = screenshot.GetBitmapBits(True)

        img = Image.frombuffer(
            'RGB',
            (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
            bmpstr, 'raw', 'BGRX', 0, 1
        )

        # Cleanup
        mem_dc.DeleteDC()
        win32gui.DeleteObject(screenshot.GetHandle())
        win32gui.ReleaseDC(hdesktop, desktop_dc)

        return np.array(img)
    except Exception as e:
        print(f"{Fore.RED}Win32 Fehler: {e}")
        return None

def main():
    print(f"{Fore.GREEN}{'='*70}")
    print(f"{Fore.CYAN}Screenshot Methods Test - Welche Methode ist am besten?")
    print(f"{Fore.GREEN}{'='*70}\n")

    print(f"{Fore.YELLOW}Teste 4 verschiedene Screenshot-Methoden...\n")

    methods = [
        ("MSS (aktuell)", test_mss),
        ("PIL ImageGrab", test_pil_imagegrab),
        ("PyAutoGUI", test_pyautogui),
        ("Win32 API", test_win32),
    ]

    results = []

    for name, method in methods:
        print(f"{Fore.CYAN}Teste {name}...", end=" ")
        start = time.time()
        img = method()
        elapsed = time.time() - start

        if img is not None:
            print(f"{Fore.GREEN}✓ ({elapsed*1000:.1f}ms)")
            results.append((name, img, elapsed))
        else:
            print(f"{Fore.RED}✗ Fehlgeschlagen")

    if not results:
        print(f"\n{Fore.RED}Keine Methode funktioniert!")
        return

    print(f"\n{Fore.GREEN}{'='*70}")
    print(f"{Fore.CYAN}Vergleich wird angezeigt...\n")

    # Erstelle Vergleichsbild
    comparison_rows = []

    for name, img, elapsed in results:
        # Resize für Anzeige
        img_rgb = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        h, w = img_rgb.shape[:2]
        new_w = 640
        new_h = int(h * (new_w / w))
        img_resized = cv2.resize(img_rgb, (new_w, new_h))

        # Label hinzufügen
        cv2.putText(img_resized, name, (10, 30),
                   cv2.FONT_HERSHEY_DUPLEX, 0.8, (0, 255, 255), 2)
        cv2.putText(img_resized, f"Speed: {elapsed*1000:.1f}ms", (10, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

        # Helligkeit berechnen
        gray = cv2.cvtColor(img_resized, cv2.COLOR_BGR2GRAY)
        brightness = np.mean(gray)
        cv2.putText(img_resized, f"Avg Brightness: {brightness:.0f}", (10, 85),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

        comparison_rows.append(img_resized)

    # Kombiniere alle Bilder
    if len(comparison_rows) == 1:
        grid = comparison_rows[0]
    elif len(comparison_rows) == 2:
        grid = np.vstack(comparison_rows)
    elif len(comparison_rows) == 3:
        # 3 in einer Spalte
        grid = np.vstack(comparison_rows)
    else:
        # 2x2 Grid
        row1 = np.hstack(comparison_rows[:2])
        row2 = np.hstack(comparison_rows[2:4])
        grid = np.vstack([row1, row2])

    print(f"{Fore.YELLOW}Vergleiche die Methoden:")
    print(f"  • Schau auf 'Avg Brightness' (niedrig = besser für ueberbelichtete Bilder)")
    print(f"  • Schau auf Farbgenauigkeit")
    print(f"  • Speed ist auch wichtig (schneller = besser)\n")

    print(f"{Fore.CYAN}Empfehlungen:")
    print(f"  • PIL ImageGrab: Beste Farbgenauigkeit")
    print(f"  • MSS: Am schnellsten")
    print(f"  • Win32 API: Beste Qualität (wenn verfuegbar)\n")

    print(f"{Fore.WHITE}Drücke eine Taste zum Beenden...\n")

    cv2.imshow('Screenshot Methods Comparison', grid)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    print(f"\n{Fore.GREEN}{'='*70}")
    print(f"{Fore.CYAN}Ergebnisse:\n")

    for name, img, elapsed in results:
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        brightness = np.mean(gray)
        print(f"{Fore.YELLOW}{name}:")
        print(f"  Speed: {elapsed*1000:.1f}ms")
        print(f"  Brightness: {brightness:.0f}")
        print()

    # Empfehlung basierend auf Brightness
    brightest = max(results, key=lambda x: np.mean(cv2.cvtColor(x[1], cv2.COLOR_RGB2GRAY)))
    darkest = min(results, key=lambda x: np.mean(cv2.cvtColor(x[1], cv2.COLOR_RGB2GRAY)))

    print(f"{Fore.GREEN}Empfehlung:")
    print(f"  Dunkelste (beste bei Ueberbelichtung): {Fore.CYAN}{darkest[0]}")
    print(f"  Hellste (am nächsten zum Original): {Fore.YELLOW}{brightest[0]}\n")

    print(f"{Fore.WHITE}Um eine andere Methode zu nutzen, erstelle ich ein neues Tool!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Abgebrochen.")
    except Exception as e:
        print(f"\n{Fore.RED}Fehler: {e}")
        import traceback
        traceback.print_exc()
