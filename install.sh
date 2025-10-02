#!/bin/bash

sudo apt install -y apache2 libapache2-mod-wsgi-py3 python3-virtualenv
sudo bash -c 'cat > /etc/apache2/sites-available/001-mothbox.conf <<EOF
<VirtualHost *:80>
	ServerName mothbox.local

	WSGIDaemonProcess mothbox python-path=/home/pi/Desktop/Mothbox/Web/app
	WSGIScriptAlias / /home/pi/Desktop/Mothbox/Web/app/mothbox.wsgi

	<Directory /home/pi/Desktop/Mothbox/Web>
    	Require all granted
	</Directory>
</VirtualHost>
<VirtualHost *:443>
	ServerName mothbox.local

	SSLCertificateFile /etc/ssl/certs/localssl.pem
	SSLCertificateKeyFile /etc/ssl/private/localssl.key
	WSGIDaemonProcess mothboxssl python-path=/home/pi/Desktop/Mothbox/Web/app
	WSGIScriptAlias / /home/pi/Desktop/Mothbox/Web/app/mothbox.wsgi

	<Directory /home/pi/Desktop/Mothbox/Web>
    	Require all granted
	</Directory>
</VirtualHost>

EOF'

chmod +x /home/pi
sudo a2ensite 001-mothbox
sudo a2enmod ssl

cd /home/pi/Desktop/Mothbox/Web
virtualenv .venv
. .venv/bin/activate
pip install -r requirements.txt

openssl req -x509 -out localssl.pem -keyout localssl.key   -newkey rsa:2048 -nodes -sha256  -subj '/CN=mothbox.local' -extensions EXT -config <( printf "[dn]\nCN=mothbox.local\n[req]\ndistinguished_name = dn\n[EXT]\nsubjectAltName=DNS:mothbox.local\nkeyUsage=digitalSignature\nextendedKeyUsage=serverAuth")

sudo mv localssl.pem /etc/ssl/certs/
sudo mv localssl.key /etc/ssl/private/

sudo systemctl restart apache2

# Let users turn on debug mode without requiring sudo password
sudo echo 'pi,www-data ALL=(ALL) NOPASSWD:/home/pi/Desktop/Mothbox/scripts/MothPower/stop_lowpower.sh' | sudo EDITOR='tee -a' visudo 

# Allow apache to write config files
chmod +w /home/pi/Desktop/Mothbox/controls.txt
chmod +w /home/pi/Desktop/Mothbox/schedule_settings.csv
chmod +w /home/pi/Desktop/Mothbox/camera_settings.csv
# And read GPIO
sudo usermod -a -G gpio www-data
