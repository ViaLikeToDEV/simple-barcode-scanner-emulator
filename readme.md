# HID Barcode Scanner Emulator (Windows)

A lightweight HID barcode scanner emulator for Windows that injects keystrokes into the currently focused window, simulating a real USB barcode scanner.

## Features

* Single barcode injection
* Interactive mode
* Batch execution from text files
* Global hotkey support
* Continuous trigger mode
* Real-time mode switching
* Inline batch commands (`!DELAY`)
* Configurable end key
* Configurable character delay

---

## Requirements

```bash
pip install pynput
```

---

## Quick Start

### Interactive Mode

```bash
python barcode_emulator.py
```

### Single Scan

```bash
python barcode_emulator.py --value "1234567890"
```

### Continuous Mode

```bash
python barcode_emulator.py --continuous
```

### Batch Mode

```bash
python barcode_emulator.py --batch list.txt
```

---

## Batch File Format

Simple batch file:

```txt
12345
67890
ABCDE
```

Batch file with inline delay commands:

```txt
12345

!DELAY 0.5

67890
ABCDE

!DELAY 2

FGHIJ
```

### Supported Commands

#### `!DELAY`

Changes the delay between subsequent barcode scans.

Example:

```txt
!DELAY 0.5
```

Meaning:

```txt
Wait 0.5 seconds after each subsequent scan
until another !DELAY command is encountered.
```

---

## Continuous Mode

Continuous mode allows barcode injection using a global hotkey.

Default hotkey:

```txt
F9
```

Custom hotkey:

```bash
python barcode_emulator.py --continuous --hotkey f8
```

---

## Continuous Mode Commands

### Single Trigger

Switch to single barcode mode:

```txt
123456789
```

Press the hotkey to inject the configured barcode.

---

### Batch Trigger

Switch to batch mode:

```txt
batch:list.txt
```

Press the hotkey to execute the entire batch file.

---

### Show Status

```txt
status
```

---

### Change End Key

```txt
end enter
end tab
end none
```

---

### Change Character Delay

Delay is specified in milliseconds.

```txt
delay 10
```

---

## Example Workflow

```txt
> 123456789
[MODE] SINGLE

Press F9

Barcode injected

> batch:test.txt
[MODE] BATCH

Press F9

Batch file executed
```

---

## Notes

* The target application must be focused before injection.
* Global hotkeys work system-wide.
* Continuous mode prevents overlapping executions.
* Batch mode supports inline commands such as `!DELAY`.
* Empty lines are ignored automatically.