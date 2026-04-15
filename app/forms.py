from wtforms import Form, validators
from wtforms import BooleanField, StringField, IntegerField, FloatField, SelectField, SelectMultipleField

days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

class ScheduleForm(Form):
    hour = SelectMultipleField("Hour(s)",
                               coerce=int,
                               choices = [[x, f'{x:02}:00'] for x in list(range(18,24)) + list(range(18))],
                               render_kw={"size": 7})
    weekday = SelectMultipleField("Weekday(s)",
                                  coerce=int,
                                  choices = list(zip([x for x in range(1,8)], days_of_week)),
                                  render_kw={"size": 7})

    utc_off = StringField("UTC Offset")
    minute = IntegerField("Start Minute")
    camera_interval = IntegerField("Photo interval (minutes)")
    runtime = IntegerField("Runtime (minutes)")
    onlyflash = BooleanField("Only use Flash to attract")
    attractOffPhoto = BooleanField("Turn Attract off during photo capture")
    attracttwo = BooleanField("Enable second attract strip (higher power)")

    
class OperationForm(Form):
    ssid = StringField("New Wifi SSID", render_kw={"list": "ssid_list"})
    wifipass = StringField("New Wifi Pass")

    
class CameraForm(Form):
    #LensPosition = StringField("Lens Position")
    #ExposureTime = IntegerField("Exposure Time (microseonds)")
    #AnalogueGain = StringField("Analogue Gain (1.0 to 16.0)")
    #AfMode = SelectField("AF Mode", choices = [[0, "Manual"], [1, "Auto"], [2, "Continuous"]])
    #AfSpeed = SelectField("AF Speed", choices = [[0, "Normal"], [1, "Fast"]])
    #AfRange = SelectField("AF Range", choices = [[0, "Normal"], [1, "Macro"], [2, "Full"]])
    #AwbEnable = BooleanField("AWB Enable")
    ExposureValue = StringField("Exposure Value (-8.0 to 8.0)")
    ColourGains = StringField("WB Colour Gains (two semi-colon-separated decimal values, e.g. 2.259;1.4)")
    HDR = SelectField("HDR", choices = [[1, "Off"], [3, "3 Photos"]])
    HDR_width = StringField("HDR exposure shift duration")
    AutoCalibration = BooleanField("Auto Calibration")
    AutoCalibrationPeriod = IntegerField("Auto Calibration Period (seconds til recalibrate)")
    ImageFileType = SelectField("Image File Type", choices = [[0, "JPG"], [1, "PNG"], [2, "BMP"]])
    VerticalFlip = BooleanField("Vertical Flip")
    

class SiteForm(Form):
    SiteName = StringField("Site Name")
    SiteCrew = StringField("Site Host Contact (email)")
    SiteLat = FloatField("Lat.", render_kw={"size": 7})
    SiteLon = FloatField("Lon.", render_kw={"size": 7})
    DeviceKey = StringField("Device Upload Key")
    LandingSheet = SelectField("Landing Sheet Dimensions",
                               choices = ["12x16 in", "8x12 in"])
    AttractorType = SelectField("Attractor Type",
                               choices = ["UV Strip 2.0a", "UV Strip 2.0b"])
    ScaleBarPresent = BooleanField("Scale Bar Present?")
    ColorStandardPresent = BooleanField("Color Standard Present?")

class SetupForm(ScheduleForm, OperationForm, SiteForm):
    LandingSheet = None
    AttractorType = None
    ScaleBarPresent = None
    ColorStandardPresent = None

    utc_off = None
    minute = None
    camera_interval = None
    runtime = None
    onlyflash = None
    attractOffPhoto = None
    attracttwo = None
