#!/usr/bin/env bash

# stunnel
# https://dev.to/lax/rtmps-relay-with-stunnel-12d3
cp /vagrant/stunnel/stunnel.conf /etc/stunnel/stunnel.conf
cp /vagrant/stunnel/fb.conf /etc/stunnel/conf.d/fb.conf
cp /vagrant/stunnel/stunnel4 /etc/default/stunnel4
systemctl restart stunnel4

# Flask
cd /vagrant/www/app/
# gunicorn -b 0.0.0.0:8000 -k geventwebsocket.gunicorn.workers.GeventWebSocketWorker -w 1 app:app &

# nginx
cp /vagrant/config/nginx.conf /usr/local/nginx/conf
/usr/local/nginx/sbin/nginx -t
/usr/local/nginx/sbin/nginx
# systemctl start nginx

