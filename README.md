# PyScale Simulator

**A Rice Lake 420 Plus scale indicator simulator for the Raspberry Pi Pico W, written in MicroPython.**

The Pico W sends the 420 Plus **continuous (stream) EDP output** over serial, so you can develop and test software that reads a 420 without a real scale, load cell or test weights.

- A **potentiometer** stands in for the scale base: 0.00–500.00 lb in 0.05 lb steps.
- A **4-button keypad** acts as the 420 front-panel keys: TARE, UNITS, GROSS/NET and ZERO.
- The **motion flag** is set while the pot is turning and clears 1 s after it stops, the same as the real indicator.
- The frames match the 420 byte for byte: 9600 8N1, 14 bytes, 10 frames per second.

The format comes from §7.3 of the [*420 Plus Installation Manual* (PDF)](https://cms-prod.ricelake.com//media/3ewalrag/m_85127_420plus_install_enus_revc.pdf).

> [!NOTE]
> This is an independent hobby project. It is not affiliated with or endorsed by Rice Lake Weighing Systems. "420 Plus" is used only to describe the protocol being emulated.

## Contents

- [Hardware](#hardware)
- [Quick start](#quick-start)
- [Stream format](#stream-format)
- [GPIO pin map](#gpio-pin-map)
- [Serial wiring](#serial-wiring)
- [Behavior](#behavior)
- [Configuration](#configuration)
- [Reading the stream from a PC](#reading-the-stream-from-a-pc)
- [License](#license)

## Hardware

| Part | Notes |
| --- | --- |
| Raspberry Pi Pico W | The plain Pico also works if you change `Pin("LED")` to `Pin(25)` |
| Potentiometer (10 kΩ linear) | The scale base |
| 4-button keypad | Any four momentary buttons to GND work. This build uses a Storm Interface 4-button switch keypad ([datasheet](https://www.storm-interface.com/pub/media/productattachments/files/File-1396359302.pdf)) |
| 3.3 V USB-TTL adapter **or** MAX3232 RS-232 module | To connect the serial output to a PC or device. See [Serial wiring](#serial-wiring) |

## Quick start

1. Flash the latest **RPI_PICO_W** MicroPython firmware from <https://micropython.org/download/RPI_PICO_W/>. Hold BOOTSEL while plugging in USB, then drag the `.uf2` onto the `RPI-RP2` drive. No extra packages are needed.
2. Wire the potentiometer, keypad and serial adapter as shown in the [GPIO pin map](#gpio-pin-map).
3. Copy `main.py` to the board:
   - **VS Code:** open this folder with the [MicroPico](https://marketplace.visualstudio.com/items?itemName=paulober.pico-w-go) extension and run *MicroPico: Upload project to Pico*. Non-code files are excluded through `micropico.pyIgnore` in `.vscode/settings.json`.
   - **Command line:** `mpremote cp main.py : && mpremote reset`
4. Reset the board. The onboard LED blinks at 1 Hz, and with `DEBUG = True` the USB REPL prints every frame, e.g. `'\x02    0.00LG \r\n'`.

## Stream format

```text
<STX><POL><wwwwwww><UNIT><G/N><S><CR><LF>
```

| Field | Bytes | Values |
| --- | --- | --- |
| STX | 1 | `0x02` |
| POL | 1 | space = positive, `-` = negative |
| Weight | 7 | Right-justified, with decimal point, no leading zeros (e.g. `  12.35`) |
| UNIT | 1 | `L` = lb, `K` = kg |
| G/N | 1 | `G` = gross, `N` = net |
| Status | 1 | space = stable, `M` = motion |
| Term | 2 | `CR LF` (`0x0D 0x0A`) |

Each frame is 14 bytes, sent every 100 ms. Example: `<STX>  123.45LG <CR><LF>`.

**Serial settings:** 9600 baud, 8 data bits, no parity, 1 stop bit. These are the 420 Plus EDP defaults.

## GPIO pin map

| GPIO | Physical pin | Use | Configuration |
| --- | --- | --- | --- |
| GP20 | 26 | Serial **TX** (stream out) | UART1 TX, 9600 8N1 |
| GP21 | 27 | Serial RX | UART1 RX (wired, not used yet) |
| GP1 | 2 | Keypad UP → **TARE** | Input, internal pull-up, active-low |
| GP5 | 7 | Keypad DOWN → **UNITS** | Input, internal pull-up, active-low |
| GP9 | 12 | Keypad LEFT → **GROSS/NET** | Input, internal pull-up, active-low |
| GP13 | 17 | Keypad RIGHT → **ZERO** | Input, internal pull-up, active-low |
| GP26 / ADC0 | 31 | Potentiometer wiper (scale base) | Average of 256 `read_u16()` readings |
| 3V3(OUT) | 36 | Potentiometer high end | — |
| AGND | 33 | Potentiometer low end | — |
| GND | 38 (any GND) | Keypad common, serial ground | — |
| `"LED"` (CYW43) | — | Onboard activity LED | Blinks at 1 Hz |

GP23, GP24, GP25 and GP29 are used by the Pico W's Wi-Fi chip. Don't use them. UART1 is put on GP20/GP21 because its default pins (GP4/GP5) would take the DOWN button.

## Serial wiring

> [!WARNING]
> The Pico outputs **3.3 V TTL**, not RS-232 levels. Never connect GP20/GP21 directly to a ±12 V RS-232 port, because it will damage the Pico.

**Option A: 3.3 V USB-TTL adapter** (FTDI, CP2102 etc., set to 3.3 V)

| Pico | Adapter |
| --- | --- |
| GP20 (TX) | RX |
| GP21 (RX) | TX (optional) |
| GND | GND |

**Option B: real RS-232 through a MAX3232 module** (powered from the Pico's 3V3)

| Pico | MAX3232 | DB9 (to PC / device) |
| --- | --- | --- |
| GP20 (TX) | T1IN → T1OUT | pin 2 (RxD) |
| GP21 (RX) | R1OUT ← R1IN | pin 3 (TxD, optional) |
| GND | GND | pin 5 (GND) |

The 420 Plus EDP port (J3) is just TxD/RxD/GND, so these three wires are all you need.

## Behavior

| Key | Action |
| --- | --- |
| **TARE** | Takes the current gross as the tare and switches to net. With the scale empty (gross 0.00), it clears the stored tare and goes back to gross. Ignored during motion. |
| **UNITS** | Toggles lb ↔ kg. kg = lb × 0.453592 (the 420's default MULT), rounded to 0.02 kg. |
| **GROSS/NET** | Toggles gross/net. Net is only available while a tare is stored. |
| **ZERO** | Makes the current reading 0.00 gross. Ignored during motion. |

**Net = gross − tare**, so net goes negative when the container is removed. Example with a 50 lb drum:

| Action | Frame |
| --- | --- |
| Drum placed (pot to 50.00) | `   50.00LG ` |
| Press TARE | `    0.00LN ` |
| Fill to 120.00 gross | `   70.00LN ` |
| Remove everything (pot to 0) | `-  50.00LN ` |
| Press TARE on the empty scale | `    0.00LG ` |

**Motion:** `M` is sent while the weight is changing and clears after 1 s without change. To keep potentiometer noise from triggering it, changes smaller than 4 grads (0.20 lb) are ignored.

## Configuration

All settings are constants at the top of [`main.py`](main.py).

| Constant | Default | Purpose |
| --- | --- | --- |
| `BAUD` | 9600 | Serial speed |
| `STREAM_MS` | 100 | Time between frames |
| `CAPACITY_GRADS` | 10000 | Full scale in grads (10000 × 0.05 lb = 500.00 lb) |
| `MOTION_MS` | 1000 | Standstill delay |
| `DEADBAND` | 4 | Noise filter in grads. Raise it if `M` flickers while the pot is still. |
| `ADC_MIN` / `ADC_MAX` | 300 / 65200 | Pot end points. Adjust if you can't reach 0.00 or 500.00. |
| `DEBOUNCE_MS` | 200 | Ignore repeat presses of the same key within this time |
| `DEBUG` | True | Also print each frame to the USB REPL |

## Reading the stream from a PC

With a USB-TTL adapter on `/dev/ttyUSB0` (`COM3` etc. on Windows):

```bash
python3 -m serial.tools.miniterm /dev/ttyUSB0 9600
# or, to see the raw bytes:
stty -F /dev/ttyUSB0 9600 raw && cat /dev/ttyUSB0 | xxd
```

A minimal parser using [pyserial](https://pypi.org/project/pyserial/) (`pip install pyserial`):

```python
import serial

with serial.Serial("/dev/ttyUSB0", 9600, timeout=1) as port:
    while True:
        frame = port.read_until(b"\r\n")
        if len(frame) != 14 or frame[0] != 0x02:
            continue  # partial frame at startup
        text = frame[1:12].decode("ascii")
        weight = float(text[0:8].replace(" ", ""))  # sign + 7 digits
        unit = "kg" if text[8] == "K" else "lb"
        mode = "net" if text[9] == "N" else "gross"
        stable = text[10] != "M"
        print(f"{weight:8.2f} {unit} {mode} {'stable' if stable else 'motion'}")
```

## License

[MIT](LICENSE)
