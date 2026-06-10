"""
HID Barcode Scanner Emulator (Windows)
=======================================
จำลอง barcode scanner ที่ส่ง keystrokes เข้า focused window
เหมือน HID device พิมพ์ทีละ character + ส่ง end key

Requirements:
    pip install pynput

Usage:
    python barcode_emulator.py
    python barcode_emulator.py --value "1234567890" --end enter --delay 5
"""

import time
import argparse
import sys
from pynput.keyboard import Controller, Key

# ─────────────────────────────────────────────
# Config
# ─────────────────────────────────────────────

# Mapping ชื่อ end key → pynput Key object หรือ string char
END_KEY_MAP = {
    "enter":  Key.enter,
    "tab":    Key.tab,
    "f1":     Key.f1,
    "f2":     Key.f2,
    "f3":     Key.f3,
    "f4":     Key.f4,
    "f5":     Key.f5,
    "f6":     Key.f6,
    "f7":     Key.f7,
    "f8":     Key.f8,
    "f9":     Key.f9,
    "f10":    Key.f10,
    "f11":    Key.f11,
    "f12":    Key.f12,
    "space":  Key.space,
    "none":   None,   # ไม่ส่ง end key เลย
}

DEFAULT_CHAR_DELAY   = 0.02   # วินาที ระหว่าง character (20ms — realistic scanner speed)
DEFAULT_END_KEY      = "enter"
DEFAULT_STARTUP_WAIT = 3      # วินาที countdown ก่อนเริ่ม inject (เวลาย้าย focus ไป browser)


# ─────────────────────────────────────────────
# Core emulator
# ─────────────────────────────────────────────

def emulate_scan(
    value: str,
    end_key: str = DEFAULT_END_KEY,
    char_delay: float = DEFAULT_CHAR_DELAY,
    startup_wait: int = DEFAULT_STARTUP_WAIT,
    verbose: bool = True,
) -> None:
    """
    จำลองการสแกน barcode โดย inject keystrokes เข้า focused window

    Args:
        value        : ค่าที่จะ "สแกน"
        end_key      : ชื่อ key ที่ส่งท้าย (enter/tab/f1-f12/space/none)
        char_delay   : delay ระหว่าง char (วินาที)
        startup_wait : รอ N วินาที ก่อน inject (เวลา focus ไปที่ target)
        verbose      : แสดง log ใน terminal
    """

    end_key_lower = end_key.lower().strip()
    if end_key_lower not in END_KEY_MAP:
        print(f"[ERROR] ไม่รู้จัก end key: '{end_key}'")
        print(f"        ตัวเลือกที่ใช้ได้: {', '.join(END_KEY_MAP.keys())}")
        sys.exit(1)

    resolved_end_key = END_KEY_MAP[end_key_lower]
    keyboard = Controller()

    # ── Countdown ──
    if verbose:
        print(f"\n[SCAN] Value   : {value!r}")
        print(f"[SCAN] End Key : {end_key_lower}")
        print(f"[SCAN] Char delay: {char_delay * 1000:.0f}ms per char")
        print()

    for i in range(startup_wait, 0, -1):
        print(f"  ⏳ เริ่มใน {i} วินาที... (ย้าย cursor ไปที่ input field ด้วย)", end="\r")
        time.sleep(1)

    print("\n  🔫 กำลัง inject...                          ")

    # ── Type characters ──
    for char in value:
        keyboard.type(char)
        time.sleep(char_delay)

    # ── Send end key ──
    if resolved_end_key is not None:
        keyboard.press(resolved_end_key)
        keyboard.release(resolved_end_key)
        if verbose:
            print(f"  ✅ Done! ส่ง {end_key_lower!r} ท้ายแล้ว")
    else:
        if verbose:
            print("  ✅ Done! (ไม่มี end key)")


# ─────────────────────────────────────────────
# Batch mode — สแกนหลายค่าต่อเนื่อง
# ─────────────────────────────────────────────

def emulate_batch(
    values: list[str],
    end_key: str = DEFAULT_END_KEY,
    char_delay: float = DEFAULT_CHAR_DELAY,
    between_scan_delay: float = 1.0,
    startup_wait: int = DEFAULT_STARTUP_WAIT,
) -> None:
    """
    จำลองการสแกน barcode หลายค่าต่อกัน

    Args:
        values             : list ของค่าที่จะสแกน
        between_scan_delay : delay ระหว่าง scan แต่ละครั้ง (วินาที)
    """

    end_key_lower = end_key.lower().strip()
    if end_key_lower not in END_KEY_MAP:
        print(f"[ERROR] ไม่รู้จัก end key: '{end_key}'")
        sys.exit(1)

    resolved_end_key = END_KEY_MAP[end_key_lower]
    keyboard = Controller()

    print(f"\n[BATCH] {len(values)} scans | end key: {end_key_lower} | delay: {char_delay*1000:.0f}ms/char")

    for i in range(startup_wait, 0, -1):
        print(f"  ⏳ เริ่มใน {i} วินาที...", end="\r")
        time.sleep(1)
    print()

    for idx, value in enumerate(values, 1):
        print(f"  [{idx}/{len(values)}] Injecting: {value!r}")
        for char in value:
            keyboard.type(char)
            time.sleep(char_delay)
        if resolved_end_key is not None:
            keyboard.press(resolved_end_key)
            keyboard.release(resolved_end_key)
        if idx < len(values):
            time.sleep(between_scan_delay)

    print("\n  ✅ Batch complete!")


# ─────────────────────────────────────────────
# Interactive CLI
# ─────────────────────────────────────────────

def interactive_mode() -> None:
    """โหมด interactive — ตั้งค่าแล้วสแกนซ้ำได้เรื่อยๆ"""

    print("=" * 50)
    print("  HID Barcode Scanner Emulator (Interactive)")
    print("=" * 50)

    # ── Config ──
    end_key = input(f"\nEnd key [{DEFAULT_END_KEY}]: ").strip() or DEFAULT_END_KEY
    if end_key.lower() not in END_KEY_MAP:
        print(f"  ⚠️  ไม่รู้จัก '{end_key}' — ใช้ 'enter' แทน")
        end_key = "enter"

    try:
        delay_input = input(f"Char delay ms [{int(DEFAULT_CHAR_DELAY * 1000)}]: ").strip()
        char_delay = float(delay_input) / 1000 if delay_input else DEFAULT_CHAR_DELAY
    except ValueError:
        print("  ⚠️  ค่าไม่ถูกต้อง — ใช้ 20ms แทน")
        char_delay = DEFAULT_CHAR_DELAY

    try:
        wait_input = input(f"Startup wait sec [{DEFAULT_STARTUP_WAIT}]: ").strip()
        startup_wait = int(wait_input) if wait_input else DEFAULT_STARTUP_WAIT
    except ValueError:
        startup_wait = DEFAULT_STARTUP_WAIT

    print(f"\nConfig: end={end_key} | delay={char_delay*1000:.0f}ms | wait={startup_wait}s")
    print("พิมพ์ 'quit' เพื่อออก | 'config' เพื่อตั้งค่าใหม่\n")

    # ── Loop ──
    while True:
        value = input("📦 Barcode value: ").strip()

        if value.lower() == "quit":
            print("Bye 👋")
            break

        if value.lower() == "config":
            interactive_mode()
            return

        if not value:
            print("  ⚠️  ค่าว่าง — ข้าม")
            continue

        emulate_scan(
            value=value,
            end_key=end_key,
            char_delay=char_delay,
            startup_wait=startup_wait,
            verbose=True,
        )
        print()


# ─────────────────────────────────────────────
# CLI Entry point
# ─────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="HID Barcode Scanner Emulator — จำลอง barcode scanner บน Windows",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "--value", "-v",
        type=str,
        default=None,
        help="ค่าที่จะ inject (ถ้าไม่ระบุ = interactive mode)",
    )
    parser.add_argument(
        "--end", "-e",
        type=str,
        default=DEFAULT_END_KEY,
        help=(
            f"End key หลัง inject (default: {DEFAULT_END_KEY})\n"
            f"ตัวเลือก: {', '.join(END_KEY_MAP.keys())}"
        ),
    )
    parser.add_argument(
        "--delay", "-d",
        type=float,
        default=DEFAULT_CHAR_DELAY * 1000,
        help=f"Delay ระหว่าง character (ms, default: {int(DEFAULT_CHAR_DELAY * 1000)})",
    )
    parser.add_argument(
        "--wait", "-w",
        type=int,
        default=DEFAULT_STARTUP_WAIT,
        help=f"Countdown ก่อนเริ่ม inject (วินาที, default: {DEFAULT_STARTUP_WAIT})",
    )
    parser.add_argument(
        "--batch", "-b",
        type=str,
        default=None,
        help="Path ไปยังไฟล์ .txt ที่มีค่า barcode ทีละบรรทัด (batch mode)",
    )
    parser.add_argument(
        "--between",
        type=float,
        default=1.0,
        help="Delay ระหว่าง scan ใน batch mode (วินาที, default: 1.0)",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    # ── Batch mode ──
    if args.batch:
        try:
            with open(args.batch, "r", encoding="utf-8") as f:
                values = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print(f"[ERROR] ไม่พบไฟล์: {args.batch}")
            sys.exit(1)

        emulate_batch(
            values=values,
            end_key=args.end,
            char_delay=args.delay / 1000,
            between_scan_delay=args.between,
            startup_wait=args.wait,
        )
        return

    # ── Single scan ──
    if args.value:
        emulate_scan(
            value=args.value,
            end_key=args.end,
            char_delay=args.delay / 1000,
            startup_wait=args.wait,
            verbose=True,
        )
        return

    # ── Interactive mode (default) ──
    interactive_mode()


if __name__ == "__main__":
    main()