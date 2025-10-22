import os

from .switches import pin_relay_state, pin_relay_set, pins
from . import datasets

def attract_state():
    return pin_relay_state(pins.attract)

def attract_on():
    return pin_relay_set(pins.attract, 1)

def attract_off():
    return pin_relay_set(pins.attract, 0)

def flash_state():
    return pin_relay_state(pins.flash)

def flash_on():
    return pin_relay_set(pins.flash, 1)

def flash_off():
    return pin_relay_set(pins.flash, 0)

def camera_take_photo():
    os.system(" ".join(["sudo", "-u", "pi", "/home/pi/Desktop/Mothbox/TakePhoto.py", "&"]))
    return True

def camera_latest_photo():
    attract_off()
    sets = datasets.get_datasets()
    if sets:
        return sets[-1].photos()[-1]
    return None
