#!/bin/bash

sudo apt install -y apache2 libapache2-mod-wsgi-py3 python3-virtualenv
sudo cat > /etc/apache2/sites-available/001-mothbox.conf <<EOF
<VirtualHost *:80>
	ServerName mothbox.local

	WSGIDaemonProcess mothbox python-path=/home/pi/Desktop/Mothbox/Web
	WSGIScriptAlias / /home/pi/Desktop/Mothbox/Web/mothbox.wsgi

	<Directory /home/pi/Desktop/Mothbox>
    	Require all granted
	</Directory>
</VirtualHost>
<VirtualHost *:443>
	ServerName mothbox.local

	SSLCertificateFile /etc/ssl/certs/localssl.pem
	SSLCertificateKeyFile /etc/ssl/private/localssl.key
	WSGIDaemonProcess mothboxssl python-path=/home/pi/Desktop/Mothbox/Web
	WSGIScriptAlias / /home/pi/Desktop/Mothbox/Web/mothbox.wsgi

	<Directory /home/pi/Desktop/Mothbox/Web>
    	Require all granted
	</Directory>
</VirtualHost>

EOF
chmod +x /home/pi
sudo a2ensite mothbox
sudo a2enmod ssl

cd /home/pi/Desktop/Mothbox/Web
virtualenv .venv
. .venv/activate
pip install -r requirements.txt

openssl req -x509 -out localssl.pem -keyout localssl.key \                             	 
  -newkey rsa:2048 -nodes -sha256 \
  -subj '/CN=mothbox.local' -extensions EXT -config <( \
   printf "[dn]\nCN=mothbox.local\n[req]\ndistinguished_name = dn\n[EXT]\nsubjectAltName=DNS:mothbox.local\nkeyUsage=digitalSignature\nextendedKeyUsage=serverAuth")

sudo mv localssl.pem /etc/ssl/certs/
sudo mv localssl.key /etc/ssl/private/

sudo systemctl restart apache2
