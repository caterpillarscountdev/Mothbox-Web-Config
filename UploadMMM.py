#!/usr/bin/python3

import requests

from app.lib import settings, datasets

MMM_ENDPOINT = "https://mothmonitor-dev-dept-caterpillars-count.apps.cloudapps.unc.edu/"

metadata_path = settings.find_settings('site_metadata.csv')


def find_next_dir():
    for d in datasets.get_datasets():
        if not d.is_uploaded():
            return d
    return None


def run_upload(device_key, device_name):
    dataset = find_next_dir()
    if not dataset:
        return None

    manifest = dataset.manifest()
    remaining = []
    check = requests.post(MMM_ENDPOINT + "upload/check_manifest",
                          params = {"key": device_key},
                          json={
                              "deviceName": device_name,
                              "night": dataset.dir,
                              "files": manifest
                          })
    if check.status_code >= 400:
        print(f"Error checking manifest for {dataset.dir}: {check.status_code}")
        print(f" with text: {check.text}")
        return
    
    resp = check.json()
    for f in resp["files"]:
        if f["missing"]:
            remaining.append(f)
    dataset.set_upload_remaining(remaining)

    total = len(remaining)
    print(f"Starting upload of {total} files for {dataset.dir}.")
    while len(remaining) > 0:
        f = remaining.pop()
        up = requests.put(f["upload_url"], data = dataset.file_contents(f["filename"]))
        if up.status_code >= 400:
            print(f"Error uploading for {dataset.dir} {f["filename"]}: {check.status_code}")
            print(f" with text: {check.text}")
            break
        dataset.set_upload_remaining(remaining)
        
    dataset.set_uploaded(True)
    print(f"Uploaded {total} files for {d.dir}.")
    return dataset, total


if __name__ == "__main__":
    metadata = settings.load_settings(metadata_path)
    controls = settings.load_control_values()
    device_key = metadata["DeviceKey"]
    d, total = run_upload(device_key, controls["name"])


