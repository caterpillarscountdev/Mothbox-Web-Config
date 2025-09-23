from flask import Flask, request, flash, render_template, url_for, redirect, abort

from werkzeug.datastructures import MultiDict


from . import settings
from . import forms

app = Flask(__name__)
app.secret_key = 'notverysecretindev'


controls = settings.load_control_values()



def site():
    with app.app_context():
        return {
            "title": "Mothbox Setup",
            "logo": "/assets/images/logos/",
            "nav_pages": [
                {"url": url_for("config_site"), "title": "Site"},
                {"url": url_for("config_schedule"), "title": "Schedule"},
                {"url": url_for("config_operation"), "title": "Operation"},
                {"url": url_for("config_camera"), "title": "Camera"}
            ],
            "computerName": controls["name"],
            "version": controls["softwareversion"],
            "status": "DEBUG"
        }


@app.route("/")
def index():
    return redirect(url_for('config_site'))

@app.route("/config/site", methods=["GET", "POST"])
def config_site():
    metadata_path = settings.find_settings('site_metadata.csv')
    metadata = settings.load_settings(metadata_path)

    metadata_for_form = MultiDict(metadata)

    form = forms.SiteForm(request.form or metadata_for_form)

    if request.method == 'POST':
        if form.validate():
            settings.write_settings(metadata_path, d)
            flash("Saved configuration", "ok")
        else:
            flash("Validation error", "error")
    return render_template("config_site.html", site=site(), form=form)


@app.route("/config/schedule", methods=["GET", "POST"])
def config_schedule():
    schedule_path = settings.find_settings()
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

    schedule_for_form = MultiDict(schedule)

    form = forms.OperationForm(request.form or schedule_for_form)

    if request.method == 'POST':
        if form.validate():
            d = dict(form.data)
            d["onlyflash"] = int(d["onlyflash"])
            settings.write_settings(schedule_path, d)
            flash("Saved configuration", "ok")
        else:
            flash("Validation error", "error")
    return render_template("config_operation.html", site=site(), form=form)

@app.route("/config/camera", methods=["GET", "POST"])
def config_camera():
    camera_path = settings.find_settings('camera_settings.csv')
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


def prepare_form(request, form, source):
    for_form = MultiDict(source)
    return form(request.form or for_form)
