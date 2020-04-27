#!/usr/bin/env bash

apt-get update 
apt-get install build-essential libpcre3 libpcre3-dev libssl-dev zlib1g zlib1g-dev python3-pip -y

# stunnel setup
apt-get install stunnel4
mkdir /etc/stunnel/conf.d

# nginx setup
cp -r /vagrant/nginx /nginx
chown -R www-data:www-data /nginx
cd /nginx/nginx-1.16.1

./configure --with-http_ssl_module --add-module=../nginx-rtmp-module
make install 

# systemd unit file for nginx
#cp /vagrant/config/nginx.service /lib/systemd/system/nginx.service
#systemctl daemon-reload

# flask setup
pip3 install flask
pip3 install Flask-SocketIO
pip3 install gevent
pip3 install gevent-websocket
pip3 install gunicorn
