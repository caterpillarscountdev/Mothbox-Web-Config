from flask import Flask, request, flash, render_template, stream_template, url_for, redirect, abort, send_from_directory
from flask_thumbnails import Thumbnail

from werkzeug.datastructures import MultiDict

import subprocess
import os.path
from datetime import datetime


from app.lib import settings, switches, testing, datasets, wifi
from app import forms

app = Flask(__name__)
app.secret_key = 'notverysecretindev'


here = os.path.dirname(os.path.realpath(__file__))

metadata_path = settings.find_settings('site_metadata.csv')
camera_path = settings.find_settings('camera_settings.csv')
schedule_path = settings.find_settings()

thumbs = Thumbnail(app)
app.config['THUMBNAIL_MEDIA_ROOT'] = datasets.PHOTOS_ROOT
app.config['THUMBNAIL_MEDIA_URL'] = '/media/'
app.config['THUMBNAIL_MEDIA_THUMBNAIL_ROOT'] = datasets.THUMBS_ROOT
app.config['THUMBNAIL_MEDIA_THUMBNAIL_URL'] = '/media/thumbnails/'


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
                     {"url": url_for("config_operation"), "title": "Wifi"},
                     {"url": url_for("config_camera"), "title": "Camera"},
                     {"url": url_for("logs"), "title": "Logs"}
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
    internet = wifi.check_internet()
    updates = check_for_updates()
    versions = check_for_versions()
    
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
            testing.camera_take_photo()
            return "Camera is taking a photo if lights and flash turn on soon."
        case "photo":
            photo = testing.camera_latest_photo()
            if photo:
                return render_template("hx/latest_photo.html", photo=photo)
            else:
                return "No photos"
        case None:
            return render_template("test_device.html", site=site())
        case _:
            return "OK"

@app.route('/logs', defaults={"log": None})
@app.route('/logs/<log>', methods=["POST"])
def logs(log):
    if log:
        return f'<pre>{log_tail(log)}</pre>'
    lognames = [
        "Attract_On",
        "Backup",
        "Scheduler",
        "TakePhoto"
    ]
    logs = {}
    for log in lognames:
        try:
            mtime = datetime.fromtimestamp(os.path.getmtime(log_get_path(log)))
        except FileNotFoundError:
            mtime = None
        logs[log] = mtime
    return render_template("view_logs.html", site=site(), logs=logs)
        
@app.route('/data')
def data():
    sets = datasets.get_datasets()
    return render_template("data_upload.html", site=site(), data=locals())

@app.route('/data/gallery/<dir>')
def data_gallery(dir):
    set = datasets.Dataset(dir)
    return stream_template("hx/data_gallery.html", photos = set.photos(), width='200')


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
    schedule_for_form = MultiDict()

    form = forms.OperationForm(request.form or schedule_for_form)

    if request.method == 'POST':
        if form.validate():
            d = dict(form.data)
            new_wifi = (d["ssid"], d["wifipass"])
            if new_wifi != old_wifi:
                attempt = wifi.connect(*new_wifi)
                if attempt == True:
                    success = wifi.check_internet() and " and connected" or " but without internet so far"
                    flash(f'Added wifi for: {d["ssid"]}{success}', "ok")
                elif attempt == False:
                    flash(f'Added wifi for: {d["ssid"]}. You will need to restart the device.', "ok")
                    settings.write_settings(schedule_path, d)
                else:
                    flash(f'Error adding wifi: {attempt}', "error")
        else:
            flash("Validation error", "error")
    return render_template("config_operation.html", site=site(), form=form,
                           current_connections=wifi.current_connections(),
                           wifi_networks=wifi.wifi_networks(ifname="wlp58s0"))

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
        result = subprocess.run(["sudo", "-u", "pi", "/home/pi/Desktop/Mothbox/Web/gitupdate.sh", "pull"], capture_output=True)
    except FileNotFoundError as e:
        flash(f"Code update failed: {e}", "error")
    else:
        if result.returncode == 0:
            flash(f"Code updated", "ok")
        else:
            flash(f"Code update failed: {result.stderr.strip().decode('utf-8')}", "error")
    return redirect(url_for('status'))

@app.route("/media/<path:name>")
def serve_photo_media(name):
    folder = app.config['THUMBNAIL_MEDIA_ROOT']
    if name.startswith("thumbnails/"):
        name = name.replace("thumbnails/", "")
        folder = app.config['THUMBNAIL_MEDIA_THUMBNAIL_ROOT']
    return send_from_directory(folder, name)


def prepare_form(request, form, source):
    for_form = MultiDict(source)
    return form(request.form or for_form)


    
def check_for_updates():
    uptodate = os.path.normpath(os.path.join(here, "../", "gitupdate.sh"))
    output = subprocess.run(["sudo", "-u", "pi", uptodate, "uptodate"], capture_output=True)
    return output.stdout.strip().decode("utf-8")

def check_for_versions():
    uptodate = os.path.normpath(os.path.join(here, "../", "gitupdate.sh"))
    output = subprocess.run(["sudo", "-u", "pi", uptodate, "versions"], capture_output=True)
    return output.stdout.strip().decode("utf-8")

def log_tail(log):
    # basename to sanitize input to intended directory
    path = log_get_path(log)
    output = subprocess.run(["tail", "-100", path], capture_output=True)
    return output.stdout.strip().decode("utf-8")
    
def log_get_path(log):
    return os.path.normpath(os.path.join(here, "../../logs/", os.path.basename(log)+"_log.txt"))
