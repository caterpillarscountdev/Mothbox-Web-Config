import os, glob, mimetypes
from pathlib import Path
from datetime import datetime, timezone

here = os.path.dirname(os.path.realpath(__file__))
PHOTOS_ROOT = os.path.normpath(os.path.join(here, "..", "..", "..", "photos"))
THUMBS_ROOT = os.path.normpath(os.path.join(here, "..", "..", "..", "thumbnails"))

class Dataset:
    def __init__(self, dir):
        self.dir = dir
        self.path = os.path.join(PHOTOS_ROOT, dir)

    def photos(self):
        return [os.path.join(self.dir, os.path.basename(f)) for f in sorted(glob.glob(os.path.join(self.path, "*.jpg")))]

    def manifest(self):
        return [{"filename": os.path.basename(f),
                 "size": os.stat(f).st_size,
                 "type":mimetypes.guess_file_type(f)[0]}
                for f in sorted(glob.glob(os.path.join(self.path, "*.jpg")) + glob.glob(os.path.join(self.path, "*.zip")))]    

    
    @property
    def _uploaded(self):
        return Path(self.dir) / "uploaded.txt"
    
    def is_uploaded(self):
        return self._uploaded.exists() and datetime.fromtimestamp(self.uploaded.stat().st_mtime)

    def set_uploaded(self, val=True):
        if val:
            self._uploaded.touch()
        else:
            self._uploaded.unlink(missing_ok=True)

    @property
    def upload_total(self):
        return len(self.manifest())

    @property
    def _upload_remaining(self):
        return Path(self.dir) / "remaining.txt"
    
    @property
    def upload_remaining(self):
        with self._upload_remaining.open() as f:
            return len(f.readlines())

    def set_upload_remaining(files):
        with self._upload_remaining.open() as f:
            f.writelines(files)
            
    def metadata_zip(self):
        return os.path.join(self.dir, 'metadata.zip')
        

def get_datasets():
    return [ Dataset(d) for d in sorted(os.listdir(PHOTOS_ROOT), reverse=True)]
