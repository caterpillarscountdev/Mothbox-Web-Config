from wtforms import Form, BooleanField, StringField, IntegerField, FloatField, SelectField, SelectMultipleField, validators

days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

class ScheduleForm(Form):
    second = IntegerField("Second")
    minute = IntegerField("Minute")
    hour = SelectMultipleField("Hour(s)",
                               coerce=int,
                               choices = [[x, f'{x:02}:00'] for x in list(range(18,24)) + list(range(18))],
                               render_kw={"size": 7})
    weekday = SelectMultipleField("Weekday(s)",
                                  coerce=int,
                                  choices = list(zip([x for x in range(1,8)], days_of_week)),
                                  render_kw={"size": 7})

    utc_off = StringField("UTC Offset")
    runtime = IntegerField("Runtime")

    
class OperationForm(Form):
    onlyflash = BooleanField("Only Flash")

    ssid = StringField("Wifi SSID")
    wifipass = StringField("Wifi Pass")

    
class CameraForm(Form):
    LensPosition = StringField("Lens Position")
    ExposureValue = StringField("Exposure Value (-8.0 to 8.0)")
    ExposureTime = IntegerField("Exposure Time (microseonds)")
    AnalogueGain = StringField("Analogue Gain (1.0 to 16.0)")
    AfMode = SelectField("AF Mode", choices = [[0, "Manual"], [1, "Auto"], [2, "Continuous"]])
    AfSpeed = SelectField("AF Speed", choices = [[0, "Normal"], [1, "Fast"]])
    AfRange = SelectField("AF Range", choices = [[0, "Normal"], [1, "Macro"], [2, "Full"]])
    AwbEnable = BooleanField("AWB Enable")
    HDR = SelectField("HDR", choices = [[1, "Off"], [3, "3 Photos"]])
    HDR_width = StringField("HDR exposure shift duration")
    AutoCalibration = BooleanField("Auto Calibration")
    AutoCalibrationPeriod = IntegerField("Auto Calibration Period (seconds til recalibrate)")
    ImageFileType = SelectField("Image File Type", choices = [[0, "JPG"], [1, "PNG"], [2, "BMP"]])
    VerticalFlip = BooleanField("Vertical Flip")
    

class SiteForm(Form):
    SiteName = StringField("Site Name")
    SiteCrew = StringField("Site Host")
    SiteLat = FloatField("Lat.", render_kw={"size": 7})
    SiteLon = FloatField("Lon.", render_kw={"size": 7})
    
