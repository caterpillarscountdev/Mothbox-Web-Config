# Mothbox-Web-Config

A local web server to configure [Mothbox](https://github.com/Digital-Naturalism-Laboratories/Mothbox).

## Installation

### Local development

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

[http://localhost:5000/](http://localhost:5000/)

### On a Mothbox image

SSH or VNC terminal to pi@mothbox.local connected to wifi

Clone the repo
```
cd ~/Desktop/Mothbox
git clone https://github.com/caterpillarscountdev/Mothbox-Web-Config.git Web
cd Web
```
Run install.sh to:
 * Create venv environment
 * Install apaache
 * Create and enable apache virtualhost for mothbox.local
```
./install.sh
```

[https://mothbox.local/](https://mothbox.local/) Will warn for self-signed certificate - Advanced, Accept The Risk.
