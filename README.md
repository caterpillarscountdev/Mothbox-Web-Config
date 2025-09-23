# Mothbox-Web-Config

A local web server to configure [Mothbox](https://github.com/Digital-Naturalism-Laboratories/Mothbox).

## Installation

### Local ddevelopment

Clone the repo and run
```
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```
To run the development server
```
flask --app=app.mothbox run --debug
```

### On a Mothbox image

SSH or VNC terminal to pi@mothbox.local connected to wifi

Clone the repo
```
cd ~/Desktop/Mothbox
git clone <repo url> Web
```
Run install.sh to:
 * Create venv environment
 * Install apaache
 * Create and enable apache virtualhost for mothbox.local
```
