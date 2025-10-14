from flask import Flask, request, flash, render_template, url_for, redirect, abort

from werkzeug.datastructures import MultiDict

import subprocess
import os.path
import urllib.request


from app.lib import settings, switches, testing
from app import forms

app = Flask(__name__)
app.secret_key = 'notverysecretindev'


here = os.path.dirname(os.path.realpath(__file__))

metadata_path = settings.find_settings('site_metadata.csv')
camera_path = settings.find_settings('camera_settings.csv')
schedule_path = settings.find_settings()


def site():
    with app.app_context():
        return {
            "title": "Mothbox Setup",
            "logo": "/assets/images/logos/",
            "nav_pages": [
                {"url": url_for("status"), "title": "Status"},
                {"url": url_for("test_device"), "title": "Testing"},
                {"url": url_for("data"), "title": "Data Upload"},
                {"category": "Config",
                 "pages": [
                     {"url": url_for("config_site"), "title": "Site"},
                     {"url": url_for("config_schedule"), "title": "Schedule"},
                     {"url": url_for("config_operation"), "title": "Operation"},
                     {"url": url_for("config_camera"), "title": "Camera"}
                ]}
            ]
        }


@app.route("/")
def index():
    return redirect(url_for('status'))

@app.route('/status')
def status():
    controls = settings.load_control_values()
    metadata = settings.load_settings(metadata_path)
    schedule = settings.load_settings(schedule_path)

    schedule["days"] = [forms.days_of_week[int(x)-1] for x in schedule["weekday"].split(";")]
    schedule["hours"] = [f'{int(x):02}:{schedule["minute"]:02}' for x in schedule["hour"].split(";")]

    device_mode = switches.mode()
    internet = check_internet()
    updates = check_for_updates()
    
    return render_template("status.html", site=site(), status=locals())

@app.route('/debug-mode', methods=["POST"])
def debug_mode():
    try:
        subprocess.run(["/home/pi/Desktop/DebugMode.py"])
    except FileNotFoundError as e:
        flash(f"Debug Mode failed: {e}", "error")
    else:
        flash("Debug mode enabled", "ok")
    return redirect(url_for('status'))

@app.route('/testing', defaults={"device": None})
@app.route('/testing/<device>', methods=["POST"])
def test_device(device):
    match device:
        case "attract":
            if testing.attract_state():
                testing.attract_off()
                return "Turned off."
            else:
                testing.attract_on()
                return "Did the UV light turn on? Click again to turn off."
        case "flash":
            if testing.flash_state():
                testing.flash_off()
                return "Turned off."
            else:
                testing.flash_on()
                return "Did Flash turn on? Click again to turn off."
        case "camera":
            pass
        case None:
            return render_template("test_device.html", site=site())
        case _:
            return "OK"

@app.route('/data')
def data():
    return render_template("data_upload.html", site=site())

@app.route("/config/site", methods=["GET", "POST"])
def config_site():
    metadata = settings.load_settings(metadata_path)

    metadata_for_form = MultiDict(metadata)

    form = forms.SiteForm(request.form or metadata_for_form)

    if request.method == 'POST':
        if form.validate():
            settings.write_settings(metadata_path, form.data)
            flash("Saved configuration", "ok")
        else:
            flash("Validation error", "error")
    return render_template("config_site.html", site=site(), form=form)


@app.route("/config/schedule", methods=["GET", "POST"])
def config_schedule():
    schedule = settings.load_settings(schedule_path)

    schedule_for_form = MultiDict(schedule)
    schedule_for_form.setlist("hour", schedule_for_form["hour"].split(";"))
    schedule_for_form.setlist("weekday", schedule_for_form["weekday"].split(";"))

    form = forms.ScheduleForm(request.form or schedule_for_form)

    if request.method == 'POST':
        if form.validate():
            d = dict(form.data)
            d["hour"] = ";".join(str(x) for x in d["hour"])
            d["weekday"] = ";".join(str(x) for x in d["weekday"])
            
            settings.write_settings(schedule_path, d)
            
            flash("Saved configuration", "ok")
        else:
            flash("Validation error", "error")
    return render_template("config_schedule.html", site=site(), form=form)

@app.route("/config/operation", methods=["GET", "POST"])
def config_operation():
    schedule_path = settings.find_settings()
    schedule = settings.load_settings(schedule_path)
    old_wifi = (schedule["ssid"], schedule["wifipass"])
    schedule_for_form = MultiDict(schedule)

    form = forms.OperationForm(request.form or schedule_for_form)

    if request.method == 'POST':
        if form.validate():
            d = dict(form.data)
            d["onlyflash"] = int(d["onlyflash"])
            new_wifi = (d["ssid"], d["wifipass"])
            if new_wifi != old_wifi:
                flash(f'Added wifi for: {d["ssid"]}. You will need to restart the device.', "ok")
            settings.write_settings(schedule_path, d)
            flash("Saved configuration", "ok")
        else:
            flash("Validation error", "error")
    return render_template("config_operation.html", site=site(), form=form)

@app.route("/config/camera", methods=["GET", "POST"])
def config_camera():
    camera = settings.load_settings(camera_path)
    
    camera_for_form = MultiDict(camera)

    form = forms.CameraForm(request.form or camera_for_form)

    if request.method == 'POST':
        if form.validate():
            d = dict(form.data)
            d["AwbEnable"] = int(d["AwbEnable"])
            d["AutoCalibration"] = int(d["AutoCalibration"])
            d["VerticalFlip"] = int(d["VerticalFlip"])
            
            settings.write_settings(camera_path, d)
            flash("Saved configuration", "ok")
        else:
            flash("Validation error", "error")
    return render_template("config_camera.html", site=site(), form=form)


@app.route("/update-code", methods=["POST"])
def update_code():
    try:
        result = subprocess.run(["sudo", "-u", "pi", "/home/pi/Desktop/Mothbox/Web/gitupdate.sh"], capture_output=True)
    except FileNotFoundError as e:
        flash(f"Code update failed: {e}", "error")
    else:
        if result.returncode == 0:
            flash(f"Code updated", "ok")
        else:
            flash(f"Code update failed: {result.stderr.strip().decode('utf-8')}", "error")
    return redirect(url_for('status'))
    


def prepare_form(request, form, source):
    for_form = MultiDict(source)
    return form(request.form or for_form)

def check_internet(url="https://caterpillarscount.unc.edu", timeout=5):
    try:
        urllib.request.urlopen(url, timeout=timeout)
        return True
    except Exception as e:
        return False

    
def check_for_updates():
    uptodate = os.path.normpath(os.path.join(here, "../", "uptodate.sh"))
    output = subprocess.run(["sudo", "-u", "pi", uptodate], capture_output=True)
    return output.stdout.strip().decode("utf-8")

