# Rice Lake 420 Plus EDP stream simulator for the Raspberry Pi Pico W.
# Frame format: 420 Plus Installation Manual, section 7.3 (Figure 7-1):
#   <STX><POL><wwwwwww><UNIT><G/N><S><CR><LF>
from machine import Pin, ADC, UART, Timer
from time import ticks_ms, ticks_diff, ticks_add, sleep_ms

# ---- Settings -------------------------------------------------------------
BAUD = 9600              # 420 Plus default EDP baud, 8N1
STREAM_MS = 100          # Time between stream frames
CAPACITY_GRADS = 10000   # 500.00 lb / 0.05 lb per grad
GRAD_HUNDREDTHS = 5      # 1 grad = 0.05 lb = 5 hundredths
KG_PER_LB = 0.453592     # 420 Plus default MULT
KG_DIV_HUNDREDTHS = 2    # kg shown in 0.02 kg steps
MOTION_MS = 1000         # Standstill after 1 s without change (MOTBAND = 1)
DEADBAND = 4             # Ignore pot changes smaller than this (grads, 0.20 lb)
ADC_MIN = 300            # Pot reading treated as 0.00 lb
ADC_MAX = 65200          # Pot reading treated as 500.00 lb
SAMPLES = 256            # ADC readings averaged per pot read (~3.5 ms)
DEBOUNCE_MS = 200        # Ignore repeat presses of the same button
DEBUG = True             # Also print each frame to the USB REPL

# ---- Hardware ------------------------------------------------------------
led = Pin("LED", Pin.OUT)
blink_timer = Timer(-1)
blink_timer.init(freq=1, mode=Timer.PERIODIC, callback=lambda _: led.toggle())

# GP20/GP21 are free; UART1's default pins (GP4/GP5) would take the DOWN button.
uart = UART(1, BAUD, bits=8, parity=None, stop=1, tx=Pin(20), rx=Pin(21))
adc = ADC(Pin(26))  # Potentiometer = scale base

# Storm Interface 4-button keypad, active-low. Mapped to 420 Plus front-panel keys.
keys = {
    "TARE": Pin(1, Pin.IN, Pin.PULL_UP),        # UP
    "UNITS": Pin(5, Pin.IN, Pin.PULL_UP),       # DOWN
    "GROSS_NET": Pin(9, Pin.IN, Pin.PULL_UP),   # LEFT
    "ZERO": Pin(13, Pin.IN, Pin.PULL_UP),       # RIGHT
}

# ---- Scale state (all weights in lb grads) ------------------------------
raw = 0             # Pot position in grads, 0..CAPACITY_GRADS
zero_offset = 0     # Set by ZERO
tare = 0            # Set by TARE
net_mode = False    # False = gross, True = net
kg_mode = False     # False = lb, True = kg
last_change = ticks_add(ticks_ms(), -MOTION_MS)  # Start at standstill


def read_pot():
    total = 0
    for _ in range(SAMPLES):
        total += adc.read_u16()
    avg = total // SAMPLES
    grads = (avg - ADC_MIN) * CAPACITY_GRADS // (ADC_MAX - ADC_MIN)
    return max(0, min(CAPACITY_GRADS, grads))


def in_motion():
    return ticks_diff(ticks_ms(), last_change) < MOTION_MS


def format_frame(grads, kg, net, motion):
    hundredths = grads * GRAD_HUNDREDTHS
    if kg:
        hundredths = round(hundredths * KG_PER_LB / KG_DIV_HUNDREDTHS) * KG_DIV_HUNDREDTHS
    pol = "-" if hundredths < 0 else " "
    h = abs(hundredths)
    weight = "{}.{:02d}".format(h // 100, h % 100)
    return "\x02{}{:>7}{}{}{}\r\n".format(
        pol, weight, "K" if kg else "L", "N" if net else "G", "M" if motion else " ")


def press_key(name):
    global zero_offset, tare, net_mode, kg_mode
    gross = raw - zero_offset
    if name == "TARE":
        if in_motion():
            return
        if abs(gross) <= 1:     # Empty scale: remove stored tare
            tare = 0
            net_mode = False
        elif gross > 0:         # Acquire tare
            tare = gross
            net_mode = True
    elif name == "UNITS":
        kg_mode = not kg_mode
    elif name == "GROSS_NET":
        net_mode = (not net_mode) and tare != 0
    elif name == "ZERO":
        if not in_motion():
            zero_offset = raw


# ---- Main loop -----------------------------------------------------------
raw = read_pot()
last_state = {name: 1 for name in keys}
last_press = {name: 0 for name in keys}
last_send = ticks_ms()

while True:
    now = ticks_ms()

    # Pot -> weight, with deadband so ADC noise doesn't fake motion
    new = read_pot()
    if abs(new - raw) >= DEADBAND or (new != raw and new in (0, CAPACITY_GRADS)):
        raw = new
        last_change = now

    # Keys: act on the press edge
    for name, pin in keys.items():
        state = pin.value()
        if state == 0 and last_state[name] == 1 and ticks_diff(now, last_press[name]) > DEBOUNCE_MS:
            last_press[name] = now
            press_key(name)
        last_state[name] = state

    # Stream
    if ticks_diff(now, last_send) >= STREAM_MS:
        last_send = now
        gross = raw - zero_offset
        value = gross - tare if net_mode else gross
        frame = format_frame(value, kg_mode, net_mode, in_motion())
        uart.write(frame)
        if DEBUG:
            print(repr(frame))

    sleep_ms(5)
