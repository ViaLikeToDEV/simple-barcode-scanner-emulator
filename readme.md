# HID Barcode Scanner Emulator

A simple Python tool that emulates a USB HID barcode scanner by sending keystrokes to the currently focused window.

Useful for testing POS systems, inventory software, web forms, ERP applications, or any software that normally receives input from a physical barcode scanner.

---

## Features

* Simulates real barcode scanner behavior
* Types characters one-by-one with configurable delay
* Sends an optional end key after each scan
* Interactive mode
* Single barcode injection from CLI
* Batch mode from a text file
* Configurable startup countdown
* Supports:

  * Enter
  * Tab
  * Space
  * F1–F12
  * No end key

---

## Requirements

Python 3.10+

Install dependencies:

```bash
pip install pynput
```

---

## Installation

Clone or download the project:

```bash
git clone https://github.com/yourusername/hid-barcode-emulator.git
cd hid-barcode-emulator
```

Install dependencies:

```bash
pip install pynput
```

---

## Usage

### Interactive Mode

Launch without arguments:

```bash
python barcode_emulator.py
```

You will be prompted to configure:

* End key
* Character delay
* Startup countdown

Then repeatedly enter barcode values to scan.

Example:

```text
📦 Barcode value: 8851234567890
```

Type:

```text
quit
```

to exit.

---

### Single Scan Mode

Inject a single barcode value:

```bash
python barcode_emulator.py --value "8851234567890"
```

or

```bash
python barcode_emulator.py -v "8851234567890"
```

---

### Custom End Key

Send TAB instead of ENTER:

```bash
python barcode_emulator.py \
    --value "8851234567890" \
    --end tab
```

Available end keys:

```text
enter
tab
space
f1-f12
none
```

---

### Change Typing Speed

Set delay between characters (milliseconds):

```bash
python barcode_emulator.py \
    --value "8851234567890" \
    --delay 5
```

Example:

| Delay  | Description           |
| ------ | --------------------- |
| 5 ms   | Very fast             |
| 20 ms  | Typical scanner speed |
| 50 ms  | Slow                  |
| 100 ms | Human-like typing     |

---

### Startup Countdown

Give yourself time to focus the target application:

```bash
python barcode_emulator.py \
    --value "8851234567890" \
    --wait 10
```

Program waits 10 seconds before injecting keystrokes.

---

## Batch Mode

Create a file:

### `barcodes.txt`

```text
8851234567890
ABC-10001
ABC-10002
ABC-10003
```

Run:

```bash
python barcode_emulator.py \
    --batch barcodes.txt
```

Output:

```text
[1/4] Injecting: '8851234567890'
[2/4] Injecting: 'ABC-10001'
[3/4] Injecting: 'ABC-10002'
[4/4] Injecting: 'ABC-10003'
```

---

### Delay Between Scans

```bash
python barcode_emulator.py \
    --batch barcodes.txt \
    --between 2
```

Waits 2 seconds between scans.

---

## Command-Line Arguments

| Argument    | Short | Description                         |
| ----------- | ----- | ----------------------------------- |
| `--value`   | `-v`  | Barcode value to inject             |
| `--end`     | `-e`  | End key after scan                  |
| `--delay`   | `-d`  | Delay per character (ms)            |
| `--wait`    | `-w`  | Startup countdown (seconds)         |
| `--batch`   | `-b`  | Text file containing barcode values |
| `--between` | -     | Delay between batch scans (seconds) |

---

## Example Commands

### Scan and press ENTER

```bash
python barcode_emulator.py \
    --value "1234567890"
```

### Scan and press TAB

```bash
python barcode_emulator.py \
    --value "1234567890" \
    --end tab
```

### Scan without end key

```bash
python barcode_emulator.py \
    --value "1234567890" \
    --end none
```

### Fast scanner simulation

```bash
python barcode_emulator.py \
    --value "1234567890" \
    --delay 5
```

### Batch mode

```bash
python barcode_emulator.py \
    --batch barcodes.txt \
    --between 1
```

---

## Typical Use Cases

* POS software testing
* Inventory management systems
* ERP/WMS testing
* Barcode workflow automation
* QA testing
* Web application form testing
* Scanner integration validation

---

## Warning

This program injects keyboard input into the currently focused window.

Before the countdown finishes:

1. Click the target application.
2. Place the cursor in the desired input field.
3. Do not switch windows during injection.

The tool behaves similarly to a real USB HID barcode scanner.

---

## License

MIT License
