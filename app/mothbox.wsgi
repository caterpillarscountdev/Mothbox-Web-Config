python_home = '/home/pi/Desktop/Mothbox/Web/app/'

activate_this = python_home + '/../.venv/bin/activate_this.py'
exec(open(activate_this).read(), dict(__file__=activate_this))

import site
site.addsitedir(python_home)

from mothbox import app as application

