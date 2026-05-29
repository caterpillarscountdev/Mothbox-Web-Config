import subprocess
import urllib.request

def ifname(primary=True):
    for k, s in current_connections().items():
        if s == 'mothboxwifi' and primary:
            return k

def check_internet(url="https://caterpillarscount.unc.edu", timeout=5):
    try:
        urllib.request.urlopen(url, timeout=timeout)
        return True
    except Exception as e:
        return False


def wifi_devices():
    result = subprocess.check_output(["sudo", "nmcli", "-g", "type,device", "device"], text=True)
    return [y for x,y in [k.split(':') for k in result.splitlines()] if x == 'wifi']

def wifi_device_macs():
    ret = {}
    for y in wifi_devices():
        ret[y] = subprocess.check_output("nmcli dev show " + y + " | awk '/HWADDR/ {print $2}'", shell=True).strip().decode("utf-8")
    return ret



def wifi_networks():
    i = ifname(primary=False)
    try:
        result = subprocess.check_output(["sudo", "nmcli", "--colors", "no", "-g", "ssid,bars", "device", "wifi", "list", "--rescan", "yes", "ifname", i], encoding="utf-8", env={"TERM": "xterm", "LANG": "en_GB.UTF-8"})
        return {s:b for s,b in [k.split(':') for k in result.splitlines() if k] if s}
    except subprocess.CalledProcessError as e:
        print(e)
        return {}

def current_connections():
    result = subprocess.check_output(["sudo", "nmcli", "-g", "device,ssid,active", "device", "wifi"], text=True)
    return {d:s for d,s,active in [k.split(':') for k in result.splitlines() if k] if active == "yes"}
    

def connect(ssid, password):
    i = ifname(primary=False)
    devices = wifi_devices()
    if i in devices:
        cmd = ["sudo", "nmcli", "device", "wifi", "connect", ssid]
        if password:
            cmd.extend(["password", password])
        if i:
            cmd.extend(["ifname", i])
        result = subprocess.run(cmd, text=True, capture_output=True)
        if result.returncode == 0:
            cmd = ["sudo", "nmcli", "con", "modify", ssid, "connection.autoconnect", "yes"]
            result = subprocess.run(cmd, text=True, capture_output=True)
            return True
        else:
            return result.stderr or result.stdout
    else:
        return False

def swap_interfaces():
    primary = ifname(primary=True)
    secondary = ifname(primary=False)

    connections = current_connections()
    
    if primary and secondary:
        primary_conn = connections[primary]
        secondary_conn = connections[secondary]
        
        cmd = ["sudo", "nmcli", "con", "modify", primary_conn, "connection.interface-name", secondary]
        result = subprocess.run(cmd, text=True, capture_output=True)
        if result.returncode == 0:
            cmd = ["sudo", "nmcli", "con", "modify", secondary_conn, "connection.interface-name", primary]
            result = subprocess.run(cmd, text=True, capture_output=True)
            cmd = ["sudo", "nmcli", "con", "up", primary_conn]
            result = subprocess.run(cmd, text=True, capture_output=True)
            
            
    
