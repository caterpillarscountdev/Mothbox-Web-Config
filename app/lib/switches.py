try:
    import gpiod
except ImportError:
    gpiod = None

class pins:
    off = 16
    debug = 12
    flash = 20
    attract = 21

GPIO_DEVICE = "/dev/gpiochip4"

if gpiod:
    INPUT_LINE_SETTING = gpiod.LineSettings(
        direction=gpiod.line.Direction.INPUT,
        bias=gpiod.line.Bias.PULL_UP,
        active_low=True
    )
    
    RELAY_IN_LINE_SETTING = gpiod.LineSettings(
        direction=gpiod.line.Direction.OUTPUT,
        bias=gpiod.line.Bias.AS_IS,
        active_low=True
    )
    

    RELAY_OUT_LINE_SETTING = gpiod.LineSettings(
        direction=gpiod.line.Direction.OUTPUT,
        bias=gpiod.line.Bias.AS_IS,
        active_low=True
    )
    
def mode():
    if not gpiod:
        return 'NOT_PI_DEVICE'
    mode = "ACTIVE"  # possible modes are OFF or DEBUG or ACTIVE
    if pin_connected_to_ground(pins.debug):
        mode = "DEBUG"
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

def pin_relay_set(pin, value):
    if not gpiod:
        return 'NOT_PI_DEVICE'
    with gpiod.request_lines(
            GPIO_DEVICE,
            config={
                pin: RELAY_OUT_LINE_SETTING
            },
    ) as request:
        return request.set_value(pin, value)
    
