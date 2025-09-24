import csv
import os

PI_PATH = '/home/pi/Desktop/Mothbox'

def relative_file(path):
    if (os.path.exists(PI_PATH)):
        return os.path.join(PI_PATH, path)

    here = os.path.dirname(os.path.realpath(__file__))
    return os.path.normpath(os.path.join(here, "../", path))

def find_file(path, filename, depth=1):
    """
    Recursively searches for a file within a directory and its subdirectories
    up to a specified depth.
    Args:
        path: The path to start searching from.
        filename: The name of the file to find.
        depth: The maximum depth of subdirectories to search (default 1).

    Returns:
        The full path to the file if found, otherwise None.
    """
    for root, dirs, files in os.walk(path):
        if (
            filename in files
            and len(root.split(os.sep)) - len(path.split(os.sep)) <= depth
        ):
            return os.path.join(root, filename)
        if depth > 1:
            # Prune directories beyond the specified depth
            dirs[:] = [
                d
                for d in dirs
                if len(os.path.join(root, d).split(os.sep)) - len(path.split(os.sep))
                <= depth
            ]
    return None


def find_settings(filename="schedule_settings.csv"):
    # first look for any updated CSV files on external media, we will prioritize those

    external_media_paths = ("/media", "/mnt")  # Common external media mount points
    default_path = relative_file(filename)
    search_depth = 2  # only want to look in the top directory of an external drive, two levels gets us there while still looking through any media
    file_path = None
    for path in external_media_paths:
        file_path = find_file(path, filename, depth=search_depth)
        print(f"Found settings on external media: {file_path}")
        break
    if file_path is None:
        file_path = default_path
        print(f"No external settings, using internal csv at: {file_path}")
    return file_path


def load_settings(file_path):
    """
    Reads schedule settings from a CSV file and converts them to appropriate data types.
    Args:
        file_path (str): Path to the CSV file containing settings.

    Returns:
        dict: Dictionary containing settings with converted data types.

    Raises:
        ValueError: If an invalid value is encountered in the CSV file.
    """

    try:
        with open(file_path) as csv_file:
            reader = csv.DictReader(csv_file)
            settings = {}
            for row in reader:
                setting, value, details = row["SETTING"].strip(), row["VALUE"].strip(), row["DETAILS"]

                # Convert data types based on setting name (adjust as needed)
                if (
                    setting == "day"
                    or setting == "weekday"
                    or setting == "hour"
                    or setting == "minute"
                    or setting == "minutes_period"
                    or setting == "second"
                ):
                    pass
                elif setting == "runtime":
                    value = int(value)
                elif setting == "utc_off":
                    value = int(value)
                elif setting == "ssid":
                    pass
                elif setting == "wifipass":
                    pass
                elif setting == "onlyflash":
                    value = int(value)
                settings[setting] = value

        return settings

    except FileNotFoundError as e:
        print(f"Error: CSV file not found: {file_path}")
        return None


def load_control_values(filename="controls.txt"):
    """
    Reads key-value pairs from the control file.
    Args:
    filename:  Name of the control file
    """
    control_values = {}
    with open(relative_file(filename), "r") as file:
        for line in file:
            key, value = line.strip().split("=")
            control_values[key] = value
    return control_values
    

def write_settings(file_path, settings):
    """
    Writes settings to specified file, assumed to already exist as we re-read
    to preserve order and details text.
    """
    with open(file_path) as csv_read:
        reader = csv.reader(csv_read)
        rows = list(reader)
    print(rows)
    with open(file_path, "w") as csv_write:
        headings = ["SETTING", "VALUE", "DETAILS"]
        writer = csv.writer(csv_write, lineterminator="\n", quoting=csv.QUOTE_MINIMAL)
        for row in rows:
            if row and row[0] in settings:
                row[1] = settings[row[0]]
            writer.writerow(row)
        


def write_control_values(control_values, filename="controls.txt"):
    """

    Writes control values to file, only changed keys and in existing order
    Args:
    control_values: dict of key value pairs from load_control_values
    filename: Name of the control file
    """

    filepath = relative_file(filename)
    with open(filepath, "r") as file:
        lines = file.readlines()
    
    with open(filepath, "w") as file:
        for line in lines:
            [control,value] = next((x for x in control_values.items() if line.startswith(x[0])), [None, None])
            if control:
                file.write(f"{control}={value}\n")
            else:
                file.write(line)  # Keep other lines unchanged
