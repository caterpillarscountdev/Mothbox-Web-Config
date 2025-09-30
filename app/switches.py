try:
    import RPi.GPIO as GPIO
except ImportError:
    GPIO = None

off_pin = 16
debug_pin = 12

    
def mode():
    if not GPIO:
        return 'NOT_PI_DEVICE'

    GPIO.setmode(GPIO.BCM)
    # Define GPIO pin for checking
    mode = "ACTIVE"  # possible modes are OFF or DEBUG or ACTIVE
    if pin_connected_to_ground(debug_pin):
        mode = "DEBUG"
    if pin_connected_to_ground(off_pin):
        mode = "OFF"
        # We won't hit this as the device will shutdown
    return mode
    
# Function to check for connection to ground
def pin_connected_to_ground(pin):
    # Set an internal pull-up resistor (optional, some circuits might have one already)
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    # Read the pin value
    pin_value = GPIO.input(pin)

    # If pin value is LOW (0), then it's connected to ground
    return pin_value == 0
