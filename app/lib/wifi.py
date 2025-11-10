import subprocess
import urllib.request

def check_internet(url="https://caterpillarscount.unc.edu", timeout=5):
    try:
        urllib.request.urlopen(url, timeout=timeout)
        return True
    except Exception as e:
        return False


def wifi_devices():
    result = subprocess.check_output(["nmcli", "-g", "type,device", "device"], text=True)
    return [y for x,y in [k.split(':') for k in result.splitlines()] if x == 'wifi']

def wifi_networks(ifname="wlan1"):
    try:
        result = subprocess.check_output(["sudo", "nmcli", "--colors", "no", "-g", "ssid,bars", "device", "wifi", "list", "--rescan", "yes", "ifname", ifname], text=True)
        return {s:b for s,b in [k.split(':') for k in result.splitlines() if k] if s}
    except subprocess.CalledProcessError as e:
        print(e)
        return {}

def current_connections():
    result = subprocess.check_output(["nmcli", "-g", "device,ssid,active", "device", "wifi"], text=True)
    return {d:s for d,s,active in [k.split(':') for k in result.splitlines() if k] if active == "yes"}
    

def connect(ssid, password, ifname="wlan1"):
    devices = wifi_devices()
    if ifname in devices:
        result = subprocess.run(["sudo", "nmcli", "device", "connect", ssid, "password", password, "ifname", ifname], text=True)
        if result.returncode == 0:
            return True
        else:
            return result.stderr
    else:
        return False
