#!/bin/sh

. .venv/bin/activate
pip install -r requirements.txt
sudo systemctl reload apache2
