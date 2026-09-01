from flask import Flask, request, flash, render_template, stream_template, url_for, redirect, abort, send_from_directory, current_app, make_response
from flask_thumbnails import Thumbnail

from werkzeug.datastructures import MultiDict

import subprocess
import os.path
from datetime import datetime
import pytz
import requests


from app.lib import settings, switches, testing, datasets, wifi
from app import forms

app = Flask(__name__)
app.secret_key = 'notverysecretindev'


here = os.path.dirname(os.path.realpath(__file__))

thumbs = Thumbnail(app)
app.config['THUMBNAIL_MEDIA_ROOT'] = os.path.normpath(os.path.join(datasets.PHOTOS_ROOT, ".."))
app.config['THUMBNAIL_MEDIA_URL'] = '/media/'
app.config['THUMBNAIL_MEDIA_THUMBNAIL_ROOT'] = datasets.THUMBS_ROOT
app.config['THUMBNAIL_MEDIA_THUMBNAIL_URL'] = '/media/thumbnails/'

app.config['MMM_ENDPOINT'] = os.environ.get("MMM_ENDPOINT", "https://mothmonitor-dev-dept-caterpillars-count.apps.cloudapps.unc.edu/")


@app.template_filter()
def format_datetime(value, format='date'):
    if not value:
        return ""
    if format == 'date':
        format="%b %d, %Y"
    elif format == 'datetime':
        format="%b %d, %Y %I:%M %p"
    elif format == 'daytime':
        format="%A %H:%M"
    return value.strftime(format)

def site():
    with app.app_context():
        return {
            "title": "Mothbox Setup",
            "logo": "/assets/images/logos/",
            "nav_pages": [
                {"url": url_for("status"), "title": "Status"},
                {"url": url_for("setup"), "title": "Setup"},
                {"url": url_for("test_device"), "title": "Testing"},
                {"url": url_for("data"), "title": "Data Upload"},
                {"category": "Config",
                 "pages": [
                     {"url": url_for("config_site"), "title": "Site"},
                     {"url": url_for("config_schedule"), "title": "Schedule"},
                     {"url": url_for("config_operation"), "title": "Wifi"},
                     {"url": url_for("config_camera"), "title": "Camera"},
                     {"url": url_for("config_device"), "title": "Device"},
                     {"url": url_for("logs"), "title": "Logs"}
                ]}
            ]
        }


@app.route("/")
def index():
    return redirect(url_for('status'))

@app.route('/status')
def status():
    with settings.Settings() as setts:
        controls = setts.controls
        metadata = setts.metadata
        schedule = setts.schedule

        schedule["days"] = [forms.days_of_week[int(x)-1] for x in schedule["weekday"].split(";") if x]
        schedule["hours"] = [f'{int(x):02}:{int(schedule["minute"]):02}' for x in schedule["hour"].split(";") if x]
        schedule["timezone"] = tz_name()
        schedule["now"] = datetime.now().astimezone(pytz.timezone(schedule["timezone"]))

        device_mode = "(unknown)"
        try:
            device_mode = switches.mode()
        except OSError as e:
            flash(f"Mode check failed: {e}", "error")
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
        case "attracttwo":
            if testing.attracttwo_state():
                testing.attracttwo_off()
                return "Turned off."
            else:
                testing.attracttwo_on()
                return "Did the second UV light turn on? Click again to turn off."
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
                return render_template("hx/latest_photo.html", photo="test_photos/"+photo)
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
        "TakePhoto",
        "Upload"
    ]
    logs = {}
    for log in lognames:
        try:
            mtime = datetime.fromtimestamp(os.path.getmtime(log_get_path(log)))
        except (FileNotFoundError, TypeError):
            mtime = None
        logs[log] = mtime
    return render_template("view_logs.html", site=site(), logs=logs)

@app.route('/reboot', methods=["POST"])
def reboot():
    run_gitupdate("reboot")
    return 'rebooting: <a href="/">Return</a>'

@app.route('/diagnostics')
def diagnostics():
    return '<pre>' + run_gitupdate("diagnostics") + '</pre>'

@app.route('/diagnostics/reset', methods=["POST"])
def diagnostics_reset():
    return '<pre>' + run_gitupdate("reset") + '</pre>'

@app.route('/data')
def data():
    sets = datasets.get_datasets()
    return render_template("data_upload.html", site=site(), data=locals())

@app.route('/data/upload/start/<dir>')
def data_upload_start(dir):
    set = datasets.Dataset(dir)
    manifest = set.manifest()
    with settings.Settings() as setts:
        metadata = setts.metadata
        controls = setts.controls
    device_key = metadata["DeviceKey"]
    if not device_key:
        return render_template("hx/upload_button.html", d = {"dir": dir}, msg = "You need a valid device key to upload at <a href='/config/site'>device key settings</a>")
    remaining = []
    check = requests.post(current_app.config["MMM_ENDPOINT"] + "upload/check_manifest",
                          params = {"key": device_key},
                          json={
                              "deviceName": controls["name"],
                              "night": dir,
                              "files": manifest
                          })
    if check.status_code < 400:
        resp = check.json()
        for f in resp["files"]:
            if f["missing"]:
                remaining.append(f)
                set.set_upload_remaining(remaining)
        return render_template("hx/upload_start.html", dataset = set)

    return render_template("hx/upload_button.html", d = {"dir": dir},  msg = "Upload failed to start, check your <a href='/config/site'>device key settings</a>")

@app.route('/data/upload/status/<dir>')
def data_upload_status(dir):
    error = None
    set = datasets.Dataset(dir)
    remaining = set.upload_remaining
    if len(remaining) > 0:
        f = remaining.pop()
        headers = {'Content-type': f["type"]}
        up = requests.put(f["upload_url"], headers=headers, data = set.file_contents(f["filename"]))
        if up.status_code < 400:
            set.set_upload_remaining(remaining)
        else:
            error = up.text
    response = make_response(render_template("hx/upload_status.html", dataset = set, error = error))
    if len(remaining) == 0:
        set.set_uploaded(True)
        response.headers["HX-Trigger"] = "done"
    return response

@app.route('/data/upload/done/<dir>')
def data_upload_done(dir):
    set = datasets.Dataset(dir)
    return render_template("hx/upload_done.html", dataset = set)

@app.route('/data/gallery/<dir>')
def data_gallery(dir):
    set = datasets.Dataset(dir)
    return stream_template("hx/data_gallery.html", photos = ["photos/"+x for x in set.photos()], width='200')


@app.route("/setup", methods=["GET", "POST"])
def setup():
    data = MultiDict()
    data.update(config_site_data())
    data.update(config_schedule_data())

    form = forms.SetupForm(request.form or data)
    if request.method == 'POST':
        if form.validate():
            d = dict(form.data)
            config_site_save(d)
            config_operation_save(d)
            config_schedule_save(d)
        else:
            flash(f"Validation error: {','.join([f.name for f in form._fields.values() if f.errors])}", "error")
    return render_template("setup.html", site=site(), form=form,
                           mmm_endpoint = current_app.config["MMM_ENDPOINT"],
                           wifi_devices=wifi.wifi_device_macs(),
                           current_connections=wifi.current_connections()
                           )
        
    

@app.route("/config/check_device_key")
def config_check_device_key():
    check = requests.get(current_app.config["MMM_ENDPOINT"] + "upload/check_key",
                         params = {"key": request.args.get('DeviceKey')}
                         )
    if check.status_code < 400:
        return "<span class='ok' style='padding: 0.2em' title='valid key'>&#x2714;</span>"

    return "<span class='error' style='padding: 0.2em' title='invalid key'>&#10754;</span>"

@app.route("/config/site", methods=["GET", "POST"])
def config_site():

    metadata_for_form = config_site_data()
    form = forms.SiteForm(request.form or metadata_for_form)

    if request.method == 'POST':
        if form.validate():
            config_site_save(form.data)
        else:
            flash("Validation error", "error")
    return render_template("config_site.html", site=site(), form=form, mmm_endpoint = current_app.config["MMM_ENDPOINT"])

def config_site_data():
    with settings.Settings() as setts:
        return MultiDict(setts.metadata)
    

def config_site_save(d):
    d = {k: d[k] for k in forms.SiteForm()._fields.keys() if d.get(k, None) is not None}
    with settings.Settings() as setts:
        setts.update({"metadata": d})
    flash("Saved site configuration", "ok")
    


@app.route("/config/schedule", methods=["GET", "POST"])
def config_schedule():
    schedule_for_form = config_schedule_data()
    form = forms.ScheduleForm(request.form or schedule_for_form)

    if request.method == 'POST':
        if form.validate():
            d = dict(form.data)
            config_schedule_save(d)
        else:
            flash("Validation error", "error")
    return render_template("config_schedule.html", site=site(), form=form)

def config_schedule_data():
    with settings.Settings() as setts:
        schedule = setts.schedule

    schedule["timezone"] = tz_name()
    
    schedule_for_form = MultiDict(schedule)
    schedule_for_form.setlist("hour", schedule_for_form["hour"].split(";"))
    schedule_for_form.setlist("weekday", schedule_for_form["weekday"].split(";"))
    return schedule_for_form
    

def config_schedule_save(d):
    d = {k: d[k] for k in forms.ScheduleForm()._fields.keys() if d.get(k, None) is not None}
    d["hour"] = ";".join(str(x) for x in d["hour"])
    d["weekday"] = ";".join(str(x) for x in d["weekday"])

    if d["timezone"]:
        if d["timezone"] != tz_name():
            tz_set(d["timezone"])
        del d["timezone"]
    
    with settings.Settings() as setts:
        setts.update({"schedule": d})
    
    flash("Saved schedule configuration", "ok")

    
@app.route("/config/operation/wifi_networks")
def config_operation_wifi_networks():
    return render_template("hx/config_operation_wifi_networks.html", wifi_networks=wifi.wifi_networks())
    

@app.route("/config/operation", methods=["GET", "POST"])
def config_operation():
    form = forms.OperationForm(request.form or MultiDict())

    if request.method == 'POST':
        if form.validate():
            d = dict(form.data)
            config_operation_save(d)
        else:
            flash("Validation error", "error")
    return render_template("config_operation.html", site=site(), form=form,
                           wifi_devices=wifi.wifi_device_macs(),
                           current_connections=wifi.current_connections())

def config_operation_save(d):
    with settings.Settings() as setts:
        schedule = setts.schedule
        old_wifi = (schedule["ssid"], schedule["wifipass"])
        new_wifi = (d["ssid"], d["wifipass"])
        if new_wifi != old_wifi:
            attempt = wifi.connect(*new_wifi)
            if attempt == True:
                success = wifi.check_internet() and " and connected" or " but <a target='_blank' href='https://nmcheck.gnome.org/'>without internet</a> so far."
                flash(f'Added wifi for: {d["ssid"]}{success}', "ok")
            elif attempt == False:
                flash(f'Added wifi for: {d["ssid"]}. You will need to restart the device.', "ok")
                setts.update({"schedule": d})
            else:
                flash(f'Error adding wifi: {attempt}', "error")
    

@app.route("/config/camera", methods=["GET", "POST"])
def config_camera():
    with settings.Settings() as setts:
        camera = setts.camera
    
        camera_for_form = MultiDict(camera)

        form = forms.CameraForm(request.form or camera_for_form)

        if request.method == 'POST':
            if form.validate():
                d = dict(form.data)
                d["AwbEnable"] = int(d["AwbEnable"])
                d["AutoCalibration"] = int(d["AutoCalibration"])
                d["VerticalFlip"] = int(d["VerticalFlip"])
                
                setts.update({"camera": d})
                flash("Saved configuration", "ok")
            else:
                flash("Validation error", "error")
        return render_template("config_camera.html", site=site(), form=form)

@app.route("/config/device", methods=["GET", "POST"])
def config_device():
    with settings.Settings() as setts:
        form = forms.DeviceForm(request.form or MultiDict(setts.schedule))

        if request.method == 'POST':
            if form.validate():
                d = dict(form.data)
                setts.update({"schedule": d})
                if d.get("name_override"):
                    setts.update({"controls": {"name": d["name_override"]}})
                flash("Saved configuration", "ok")
            else:
                flash("Validation error", "error")
        return render_template("config_device.html", site=site(), form=form, name=setts.controls.get("name"))

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


def run_gitupdate(*cmd):
    uptodate = os.path.normpath(os.path.join(here, "../", "gitupdate.sh"))
    output = subprocess.run(["sudo", "-u", "pi", uptodate, *cmd], capture_output=True)
    return output.stdout.strip().decode("utf-8")
    
    
def check_for_updates():
    return run_gitupdate("uptodate")

def check_for_versions():
    return run_gitupdate("versions")

def log_tail(log):
    # basename to sanitize input to intended directory
    path = log_get_path(log)
    if not path:
        return ""
    output = subprocess.run(["tail", "-100", path], capture_output=True)
    return output.stdout.strip().decode("utf-8")
    
def log_get_path(log):
    n = os.path.basename(log)+"_log.txt"
    for name in [f"{n}{x}" for x in ["", ".1", ".2", ".3", ".4"]]:
        path = os.path.normpath(os.path.join(here, "../../logs/", name))
        try:
            if os.stat(path).st_size > 0:
                return path
        except FileNotFoundError:
            continue


def tz_name():
    output = subprocess.run(f"timedatectl show --property=Timezone --value".split(" "), capture_output=True)
    return output.stdout.strip().decode("utf-8")


def tz_set(timezone):
    return run_gitupdate("settz", timezone)
    

