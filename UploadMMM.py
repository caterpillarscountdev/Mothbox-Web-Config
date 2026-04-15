#!/usr/bin/env python3

import runpy
import os

LOCAL_DEV = os.environ.get("LOCAL_DEV")
DEVICE_KEY = os.environ.get("DEVICE_KEY")

if not LOCAL_DEV:
    runpy.run_path(".venv/bin/activate_this.py")

import requests
import subprocess
import os

from app.lib import settings, datasets, switches
from datetime import datetime

now = datetime.now()
formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")  # Adjust the format as needed

MMM_ENDPOINT = os.environ.get("MMM_ENDPOINT", "https://mothmonitor-dev-dept-caterpillars-count.apps.cloudapps.unc.edu/")


def check_for_updates():
    here = os.path.dirname(os.path.realpath(__file__))
    uptodate = os.path.normpath(os.path.join(here, "gitupdate.sh"))
    output = subprocess.run(["sudo", "-u", "pi", uptodate, "uptodate"], capture_output=True)
    return output.stdout.strip().decode("utf-8")

def check_for_versions():
    uptodate = os.path.normpath(os.path.join(here, "../", "gitupdate.sh"))
    output = subprocess.run(["sudo", "-u", "pi", uptodate, "versions"], capture_output=True)
    return output.stdout.strip().decode("utf-8")


def update_code():
    try:
        result = subprocess.run(["sudo", "-u", "pi", "/home/pi/Desktop/Mothbox/Web/gitupdate.sh", "pull"], capture_output=True)
    except FileNotFoundError as e:
        print(f"Code update failed: {e}")
    else:
        if result.returncode == 0:
            print(f"Code updated {result.stdout.strip().decode('utf-8')}")
        else:
            print(f"Code update failed: {result.stderr.strip().decode('utf-8')}")
    


def find_next_dir():
    for d in datasets.get_datasets():
        if not d.is_uploaded():
            return d
    return None


def run_upload(device_key, device_name):
    dataset = find_next_dir()
    if not dataset:
        print(f"No datasets need upload, exiting")
        return None, None

    manifest = dataset.manifest()
    remaining = []
    check = requests.post(MMM_ENDPOINT + "upload/check_manifest",
                          params = {"key": device_key},
                          json={
                              "deviceName": device_name,
                              "night": dataset.dir,
                              "files": manifest
                          })
    if not check.ok:
        print(f"Error checking manifest for {dataset.dir}: {check.status_code} {check.reason}")
        return dataset, False
    
    resp = check.json()
    for f in resp["files"]:
        if f["missing"]:
            remaining.append(f)
    dataset.set_upload_remaining(remaining)

    total = len(remaining)
    print(f"Starting upload of {total} files for {dataset.dir}.")
    while len(remaining) > 0:
        f = remaining.pop()
        headers = {'Content-type': f["type"]}
        up = requests.put(f["upload_url"], headers=headers, data = dataset.file_contents(f["filename"]))
        if not up.ok:
            print(f"Error uploading for {dataset.dir} {f['filename']}: {check.status_code} {check.reason}")
            break
        dataset.set_upload_remaining(remaining)
        
    dataset.set_uploaded(True)
    print(f"Uploaded {total} files for {dataset.dir}.")
    return dataset, total

def do_config_post(devie_key, setts, version=None, logs=None):
    body = {"config": setts.to_json()}
    if version:
        body["code_version"] = version
    if logs:
        body["recent_logs"] = logs
    check = requests.post(MMM_ENDPOINT + "devices/check_config",
                          params = {"key": device_key},
                          json = body)
    if not check.ok:
        print(f"Error checking MMM config: {check.status_code} {check.reason}")
        return False
    return check.json()

def config_post(device_key, setts, version=None, logs=None):
    resp = do_config_post(device_key, setts, version, logs)
    if resp and resp.get("updated_config", None):
        #Update config from server changes
        setts.update(resp["updated_config"])
        # and notify
        do_config_post(device_key, setts)
        
        


if __name__ == "__main__":
    version = "LOCAL"
    if not LOCAL_DEV:
        if switches.mode() != "ONLINE":
            exit()
        if check_for_updates() == "Update Available":
            update_code()
        version = check_for_versions()
            
    print(f"{formatted_time} Upload\n")
    with settings.Settings() as setts:
        device_key = DEVICE_KEY or setts.metadata.get("DeviceKey")
        # Update MMM config record
        config_post(device_key, setts, version, {})
        # Run an upload
        d, total = run_upload(device_key, setts.controls["name"])


