import subprocess

from .switches import pin_relay_state, pin_relay_set, pins
from . import datasets

def attract_state():
    return pin_relay_state(pins.attract)

def attract_on():
    return pin_relay_set(pins.attract, 1)

def attract_off():
    return pin_relay_set(pins.attract, 0)

def attracttwo_state():
    return pin_relay_state(pins.attracttwo)

def attracttwo_on():
    return pin_relay_set(pins.attracttwo, 1)

def attracttwo_off():
    return pin_relay_set(pins.attracttwo, 0)

def flash_state():
    return pin_relay_state(pins.flash)

def flash_on():
    return pin_relay_set(pins.flash, 1)

def flash_off():
    return pin_relay_set(pins.flash, 0)

def camera_take_photo():
    subprocess.Popen(["sudo", "-u", "pi", "/home/pi/Desktop/Mothbox/TakePhoto.py"], stdout=None, stderr=None, cwd="/tmp")
    return True

def camera_latest_photo():
    #attract_off()
    sets = datasets.get_datasets()
    if sets:
        return sets[0].photos()[-1]
    return None
