#!/bin/sh

pip install -r requirements.txt
sudo systemctl reload apache2
