import os, glob, mimetypes, json
from pathlib import Path
from datetime import datetime, timezone

here = os.path.dirname(os.path.realpath(__file__))
TEST_ROOT = os.path.normpath(os.path.join(here, "..", "..", "..", "test_photos"))
PHOTOS_ROOT = os.path.normpath(os.path.join(here, "..", "..", "..", "photos"))
THUMBS_ROOT = os.path.normpath(os.path.join(here, "..", "..", "..", "thumbnails"))

class Dataset:
    def __init__(self, dir, root=PHOTOS_ROOT):
        self.dir = dir
        self.path = os.path.join(root, dir)

    def photos(self):
        return [os.path.join(self.dir, os.path.basename(f)) for f in sorted(glob.glob(os.path.join(self.path, "*.jpg")))]

    def manifest(self):
        return [{"filename": os.path.basename(f),
                 "size": os.stat(f).st_size,
                 "type":mimetypes.guess_type(f)[0]}
                for f in sorted(glob.glob(os.path.join(self.path, "*.jpg")) + glob.glob(os.path.join(self.path, "*.zip")) + glob.glob(os.path.join(self.path, "*.json")))]

    def file_contents(self, filename):
        with open(os.path.join(self.path, filename), 'rb') as f:
            return f.read()
    
    @property
    def _uploaded(self):
        return Path(self.path) / "uploaded.txt"
    
    def is_uploaded(self):
        return self._uploaded.exists() and datetime.fromtimestamp(self._uploaded.stat().st_mtime)

    def set_uploaded(self, val=True):
        if val:
            self._uploaded.touch()
        else:
            self._uploaded.unlink(missing_ok=True)
        try:
            os.chmod(self._uploaded, 0o666)
        except (FileNotFoundError, PermissionError):
            pass

    @property
    def upload_total(self):
        return len(self.manifest())

    @property
    def upload_total_left(self):
        if not self._upload_remaining.exists():
            return self.upload_total
        return self.upload_total - len(self.upload_remaining)
    
    @property
    def _upload_remaining(self):
        return Path(self.path) / "remaining.txt"

    @property
    def upload_remaining(self):
        with self._upload_remaining.open() as f:
            try:
                return json.load(f)
            except json.JSONDecodeError as e:
                pass
        self._upload_remaining.unlink()
        return []

    def set_upload_remaining(self, files):
        with self._upload_remaining.open("w") as f:
            json.dump(files, f)
        try:
            os.chmod(self._upload_remaining, 0o666)
        except (FileNotFoundError, PermissionError):
            pass
            
    def metadata_zip(self):
        return os.path.join(self.dir, 'metadata.zip')
        

def get_datasets(root=PHOTOS_ROOT):
    return [ Dataset(d, root=root) for d in sorted(os.listdir(root), reverse=True)]
