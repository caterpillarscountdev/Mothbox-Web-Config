try:
    import gpiod
except ImportError:
    gpiod = None

off_pin = 16
debug_pin = 12


def mode():
    if not gpiod:
        return 'NOT_PI_DEVICE'
    mode = "ACTIVE"  # possible modes are OFF or DEBUG or ACTIVE
    if pin_connected_to_ground(debug_pin):
        mode = "DEBUG"
    if pin_connected_to_ground(off_pin):
        mode = "OFF"
        # We won't hit this as the device will shutdown
    return mode

# Function to check for connection to ground
def pin_connected_to_ground(pin):
    with gpiod.request_lines(
            "/dev/gpiochip4",
            consumer="mode",
            config={
                pin: gpiod.LineSettings(
                    direction=gpiod.line.Direction.INPUT,
                    bias=gpiiod.line.Bias.PULL_UP,
                    active_low=True
                )
            },
    ) as request:
        return request.get_value(pin)
