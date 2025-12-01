import os, glob

here = os.path.dirname(os.path.realpath(__file__))
PHOTOS_ROOT = os.path.normpath(os.path.join(here, "..", "..", "..", "photos"))
THUMBS_ROOT = os.path.normpath(os.path.join(here, "..", "..", "..", "thumbnails"))

class Dataset:
    def __init__(self, dir):
        self.dir = dir
        self.path = os.path.join(PHOTOS_ROOT, dir)

    def photos(self):
        return [os.path.join(self.dir, os.path.basename(f)) for f in sorted(glob.glob(os.path.join(self.path, "*.jpg")))]

    def metadata_zip(self):
        return os.path.join(self.dir, 'metadata.zip')
        

def get_datasets():
    return [ Dataset(d) for d in sorted(os.listdir(PHOTOS_ROOT), reverse=True)]
