"""
HID Barcode Scanner Emulator (Windows)
=======================================
จำลอง barcode scanner ที่ส่ง keystrokes เข้า focused window
เหมือน HID device พิมพ์ทีละ character + ส่ง end key

Requirements:
    pip install pynput

Usage:
    python barcode_emulator.py                                 # interactive mode
    python barcode_emulator.py --value "1234567890"            # single scan
    python barcode_emulator.py --continuous                    # continuous mode (F9 to fire)
    python barcode_emulator.py --continuous --hotkey f8        # custom hotkey
    python barcode_emulator.py --batch "list.txt"              # run batch file directly
"""

import time
import argparse
import sys
import os
import threading
from pynput.keyboard import Controller, Key, GlobalHotKeys

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
    """จำลองการสแกน barcode โดย inject keystrokes เข้า focused window"""

    end_key_lower = end_key.lower().strip()
    if end_key_lower not in END_KEY_MAP:
        print(f"[ERROR] ไม่รู้จัก end key: '{end_key}'")
        print(f"        ตัวเลือกที่ใช้ได้: {', '.join(END_KEY_MAP.keys())}")
        sys.exit(1)

    resolved_end_key = END_KEY_MAP[end_key_lower]
    keyboard = Controller()

    if verbose:
        print(f"\n[SCAN] Value   : {value!r}")
        print(f"[SCAN] End Key : {end_key_lower}")
        print(f"[SCAN] Char delay: {char_delay * 1000:.0f}ms per char")
        print()

    for i in range(startup_wait, 0, -1):
        print(f"  ⏳ เริ่มใน {i} วินาที... (ย้าย cursor ไปที่ input field ด้วย)", end="\r")
        time.sleep(1)

    print("\n  🔫 กำลัง inject...                          ")

    for char in value:
        keyboard.type(char)
        time.sleep(char_delay)

    if resolved_end_key is not None:
        keyboard.press(resolved_end_key)
        keyboard.release(resolved_end_key)
        if verbose:
            print(f"  ✅ Done! ส่ง {end_key_lower!r} ท้ายแล้ว")
    else:
        if verbose:
            print("  ✅ Done! (ไม่มี end key)")


# ─────────────────────────────────────────────
# Batch mode — รองรับ Inline !DELAY คำสั่งแทรกในไฟล์
# ─────────────────────────────────────────────

def emulate_batch(
    lines: list[str],
    end_key: str = DEFAULT_END_KEY,
    char_delay: float = DEFAULT_CHAR_DELAY,
    between_scan_delay: float = 1.0,
    startup_wait: int = DEFAULT_STARTUP_WAIT,
) -> None:
    """จำลองการสแกน barcode หลายค่าต่อกัน โดยอ่าน Inline !DELAY ได้"""

    end_key_lower = end_key.lower().strip()
    if end_key_lower not in END_KEY_MAP:
        print(f"[ERROR] ไม่รู้จัก end key: '{end_key}'")
        sys.exit(1)

    resolved_end_key = END_KEY_MAP[end_key_lower]
    keyboard = Controller()

    print(f"\n[BATCH] Processing {len(lines)} lines | end key: {end_key_lower} | char delay: {char_delay*1000:.0f}ms")

    for i in range(startup_wait, 0, -1):
        print(f"  ⏳ เริ่มใน {i} วินาที...", end="\r")
        time.sleep(1)
    print()

    current_between_delay = between_scan_delay
    total_barcodes = sum(1 for l in lines if not l.upper().startswith("!DELAY "))
    current_idx = 0

    for idx, line in enumerate(lines):
        if line.upper().startswith("!DELAY "):
            try:
                current_between_delay = float(line[7:].strip())
                print(f"  [BATCH CONFIG] เปลี่ยนระหว่างสแกน delay -> {current_between_delay} วิ")
            except ValueError:
                print(f"  [BATCH WARN] Syntax !DELAY ผิดพลาด: {line}")
            continue

        current_idx += 1
        print(f"  [{current_idx}/{total_barcodes}] Injecting: {line!r}")
        for char in line:
            keyboard.type(char)
            time.sleep(char_delay)
            
        if resolved_end_key is not None:
            keyboard.press(resolved_end_key)
            keyboard.release(resolved_end_key)

        # เช็กว่ายังมีบาร์โค้ดเหลือข้างหลังอีกไหม ถ้ามีค่อย delay
        has_more_barcodes = any(not l.upper().startswith("!DELAY ") for l in lines[idx+1:])
        if has_more_barcodes:
            time.sleep(current_between_delay)

    print("\n  ✅ Batch complete!")


# ─────────────────────────────────────────────
# Interactive CLI
# ─────────────────────────────────────────────

def interactive_mode() -> None:
    """โหมด interactive — ตั้งค่าแล้วสแกนซ้ำได้เรื่อยๆ"""
    print("=" * 50)
    print("  HID Barcode Scanner Emulator (Interactive)")
    print("=" * 50)

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
# Continuous Mode — รองรับการสลับโหมดผ่าน Terminal แบบ Real-time
# ─────────────────────────────────────────────

HOTKEY_KEY_MAP = {
    "f1": "<f1>", "f2": "<f2>", "f3": "<f3>", "f4": "<f4>",
    "f5": "<f5>", "f6": "<f6>", "f7": "<f7>", "f8": "<f8>",
    "f9": "<f9>", "f10": "<f10>", "f11": "<f11>", "f12": "<f12>",
}
DEFAULT_HOTKEY = "f9"


def _inject_current(state: dict, lock: threading.Lock) -> None:
    """ฟังก์ชันทำงานเมื่อกด Hotkey (รันแบบ Thread-safe + Non-blocking ลิสเนอร์)"""
    with lock:
        mode = state["mode"]
        value = state["value"]
        batch_file = state["batch_file"]
        end_key = state["end_key"]
        char_delay = state["char_delay"]
        injecting = state["injecting"]
        between_delay = state["between_scan_delay"]

    if injecting:
        _print_status("[SKIP] งานเก่ายังรันไม่เสร็จ — รอแป๊บใจเย็นวัยรุ่น")
        return

    if mode == "single" and not value:
        _print_status("[SKIP] ไม่มีบาร์โค้ดให้ยิง — พิมพ์ค่าใน terminal ก่อน")
        return

    # ล็อคสถานะป้องกันการกดซ้อน
    with lock:
        state["injecting"] = True

    # แยก Worker Thread ออกมาเพื่อไม่ให้ตัวดักปุ่มค้าง
    def worker():
        try:
            keyboard = Controller()
            resolved_end = END_KEY_MAP.get(end_key.lower())

            if mode == "single":
                _print_status(f"[FIRE SINGLE] ยิงบาร์โค้ดเดี่ยว: {value!r} (+{end_key})")
                for char in value:
                    keyboard.type(char)
                    time.sleep(char_delay)
                if resolved_end is not None:
                    keyboard.press(resolved_end)
                    keyboard.release(resolved_end)
                _print_status(f"[DONE] ยิงสำเร็จ: {value!r}")

            elif mode == "batch":
                _print_status(f"[FIRE BATCH] เริ่มอ่านและยิงจากไฟล์: {batch_file!r}")
                try:
                    with open(batch_file, "r", encoding="utf-8") as f:
                        lines = [line.strip() for line in f if line.strip()]
                except Exception as e:
                    _print_status(f"[ERROR] เปิดไฟล์แบทช์ไม่ได้: {e}")
                    return

                current_between_delay = between_delay
                for idx, line in enumerate(lines):
                    if line.upper().startswith("!DELAY "):
                        try:
                            current_between_delay = float(line[7:].strip())
                            _print_status(f"[BATCH CONFIG] ปรับ Delay ระหว่างรอบ -> {current_between_delay} วิ")
                        except ValueError:
                            _print_status(f"[BATCH WARN] ค่า !DELAY เพี้ยน: {line}")
                        continue

                    _print_status(f"[BATCH RUNNING] กำลังยิง: {line!r}")
                    for char in line:
                        keyboard.type(char)
                        time.sleep(char_delay)
                    if resolved_end is not None:
                        keyboard.press(resolved_end)
                        keyboard.release(resolved_end)

                    has_more_barcodes = any(not l.upper().startswith("!DELAY ") for l in lines[idx+1:])
                    if has_more_barcodes:
                        time.sleep(current_between_delay)

                _print_status(f"[DONE] ยิง Batch จากไฟล์ {batch_file!r} ครบถ้วนแล้ว!")
        finally:
            with lock:
                state["injecting"] = False

    t = threading.Thread(target=worker)
    t.daemon = True
    t.start()


def _print_status(msg: str) -> None:
    print(f"\r{msg}\n> ", end="", flush=True)


def continuous_mode(
    initial_value: str = "",
    end_key: str       = DEFAULT_END_KEY,
    hotkey: str        = DEFAULT_HOTKEY,
    char_delay: float  = DEFAULT_CHAR_DELAY,
) -> None:
    """โหมดต่อเนื่อง ยิงเดี่ยว/สลับแบทช์ได้ในที่เดียว"""

    hotkey_lower = hotkey.lower().strip()
    if hotkey_lower not in HOTKEY_KEY_MAP:
        print(f"[ERROR] hotkey ไม่รองรับ: '{hotkey}'")
        sys.exit(1)

    end_key_lower = end_key.lower().strip()
    if end_key_lower not in END_KEY_MAP:
        print(f"[ERROR] end key ไม่รองรับ: '{end_key}'")
        sys.exit(1)

    hotkey_str = HOTKEY_KEY_MAP[hotkey_lower]

    lock  = threading.Lock()
    state = {
        "mode":               "single",  # "single" หรือ "batch"
        "value":              initial_value,
        "batch_file":         None,
        "end_key":            end_key_lower,
        "char_delay":         char_delay,
        "injecting":          False,
        "running":            True,
        "between_scan_delay": 1.0,
    }

    print("\n" + "=" * 56)
    print("  🔫 HID Emulator — Continuous Mode (Hybrid)")
    print("=" * 56)
    print(f"  Hotkey Trigger : {hotkey_lower.upper()} (กดจากหน้าต่างไหนก็ได้)")
    print(f"  End key        : {end_key_lower}  |  Char delay: {char_delay * 1000:.0f}ms")
    print("-" * 56)
    print("  💡 วิธีการสลับโหมดใช้งานใน Terminal:")
    print("    • พิมพ์บาร์โค้ดตรงๆ     -> สลับเป็น Single Trigger (เช่น ยิงเดี่ยว)")
    print("    • พิมพ์ batch:ชื่อไฟล์  -> สลับเป็น Batch Trigger ยิงยกไฟล์ .txt")
    print("-" * 56)
    print(f"  กด {hotkey_lower.upper()} เพื่อยิง  |  Ctrl+C เพื่อออกปิดสคริปต์")
    print("=" * 56 + "\n")

    def on_hotkey():
        _inject_current(state, lock)

    listener = GlobalHotKeys({hotkey_str: on_hotkey})
    listener.daemon = True
    listener.start()

    try:
        while True:
            try:
                raw = input("> ").strip()
            except EOFError:
                break

            if not raw:
                with lock:
                    md = state["mode"]
                    val = state["value"] if md == "single" else state["batch_file"]
                print(f"  [INFO] โหมดปัจจุบัน: {md.upper()} | Target: {val!r}")
                continue

            if raw.lower() == "status":
                with lock:
                    print(f"  [STATUS] mode={state['mode']} | value={state['value']!r} | batch_file={state['batch_file']!r} | end={state['end_key']} | delay={state['char_delay']*1000:.0f}ms")
                continue

            if raw.lower().startswith("end "):
                new_end = raw[4:].strip().lower()
                if new_end in END_KEY_MAP:
                    with lock: state["end_key"] = new_end
                    print(f"  [OK] เปลี่ยน end key -> {new_end!r}")
                continue

            if raw.lower().startswith("delay "):
                try:
                    new_delay = float(raw[6:].strip()) / 1000
                    with lock: state["char_delay"] = new_delay
                    print(f"  [OK] เปลี่ยน char delay -> {new_delay * 1000:.0f}ms")
                except ValueError: pass
                continue

            # ── สลับเป็น BATCH MODE ด้วย Prefix ──
            if raw.lower().startswith("batch:"):
                filename = raw[6:].strip()
                if os.path.exists(filename):
                    with lock:
                        state["mode"] = "batch"
                        state["batch_file"] = filename
                    print(f"  🔄 [MODE] เปลี่ยนเป็น BATCH TRIGGER -> ไฟล์ '{filename}' (กด {hotkey_lower.upper()} เพื่อสแกนยกแผง)")
                else:
                    print(f"  ❌ [ERROR] ไม่พบไฟล์ '{filename}' (ยังใช้โหมดเดิมอยู่)")
                continue

            # ── สลับกลับมาเป็น SINGLE MODE (พิมพ์บาร์โค้ดปกติ) ──
            with lock:
                state["mode"] = "single"
                state["value"] = raw
            print(f"  🔄 [MODE] เปลี่ยนเป็น SINGLE TRIGGER -> บาร์โค้ด = {raw!r} (กด {hotkey_lower.upper()} เพื่อยิงตัวนี้)")

    except KeyboardInterrupt:
        pass
    finally:
        with lock:
            state["running"] = False
        listener.stop()
        print("\n\n  👋 ปิดระบบ Continuous mode")


# ─────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="HID Barcode Scanner Emulator",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("--value", "-v", type=str, default=None)
    parser.add_argument("--end", "-e", type=str, default=DEFAULT_END_KEY)
    parser.add_argument("--delay", "-d", type=float, default=DEFAULT_CHAR_DELAY * 1000)
    parser.add_argument("--wait", "-w", type=int, default=DEFAULT_STARTUP_WAIT)
    parser.add_argument("--batch", "-b", type=str, default=None)
    parser.add_argument("--between", type=float, default=1.0)
    parser.add_argument("--continuous", "-c", action="store_true", default=False)
    parser.add_argument("--hotkey", type=str, default=DEFAULT_HOTKEY)
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.continuous:
        continuous_mode(
            initial_value=args.value or "",
            end_key=args.end,
            hotkey=args.hotkey,
            char_delay=args.delay / 1000,
        )
        return

    if args.batch:
        try:
            with open(args.batch, "r", encoding="utf-8") as f:
                lines = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print(f"[ERROR] ไม่พบไฟล์: {args.batch}")
            sys.exit(1)

        emulate_batch(
            lines=lines,
            end_key=args.end,
            char_delay=args.delay / 1000,
            between_scan_delay=args.between,
            startup_wait=args.wait,
        )
        return

    if args.value:
        emulate_scan(
            value=args.value,
            end_key=args.end,
            char_delay=args.delay / 1000,
            startup_wait=args.wait,
        )
        return

    interactive_mode()


if __name__ == "__main__":
    main()