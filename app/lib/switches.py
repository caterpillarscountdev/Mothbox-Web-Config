try:
    import gpiod
except ImportError:
    gpiod = None

import os

class pins:
    off = 16
    debug = 12
    flash = 20
    attract = 21
    attracttwo = 26

GPIO_DEVICE = None
for dev in ["/dev/gpiochip4", "/dev/gpiochip15"]:
    try:
        if os.stat(dev):
            GPIO_DEVICE = dev
            break
    except FileNotFoundError:
        continue

if gpiod:
    INPUT_LINE_SETTING = gpiod.LineSettings(
        direction=gpiod.line.Direction.INPUT,
        bias=gpiod.line.Bias.PULL_UP,
        active_low=True
    )
    
    RELAY_IN_LINE_SETTING = gpiod.LineSettings(
        direction=gpiod.line.Direction.AS_IS,
        active_low=True
    )
    

    RELAY_OUT_LINE_SETTING = gpiod.LineSettings(
        direction=gpiod.line.Direction.OUTPUT,
        active_low=True
    )
    
def mode():
    if not gpiod or not GPIO_DEVICE:
        return 'NOT_PI_DEVICE'
    mode = "FIELD"  # possible modes are OFF or ONLINE or FIELD/ACTIVE
    if pin_connected_to_ground(pins.debug):
        mode = "ONLINE"
    if pin_connected_to_ground(pins.off):
        mode = "OFF"
        # We won't hit this as the device will shutdown
    return mode

# Function to check for connection to ground
def pin_connected_to_ground(pin):
    with gpiod.request_lines(
            GPIO_DEVICE,
            config={
                pin: INPUT_LINE_SETTING
            },
    ) as request:
        return request.get_value(pin)

def pin_relay_state(pin):
    if not gpiod:
        return 'NOT_PI_DEVICE'
    with gpiod.request_lines(
            GPIO_DEVICE,
            config={
                pin: RELAY_IN_LINE_SETTING
            },
    ) as request:
        return request.get_value(pin)

def pin_relay_set(pin, on):
    if not gpiod:
        return 'NOT_PI_DEVICE'
    with gpiod.request_lines(
            GPIO_DEVICE,
            config={
                pin: RELAY_OUT_LINE_SETTING
            },
    ) as request:
        if on:
            value = gpiod.line.Value.ACTIVE
        else:
            value = gpiod.line.Value.INACTIVE
        return request.set_value(pin, value)
    
