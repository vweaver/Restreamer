#!/bin/bash
cp /vagrant/config/nginx.conf /usr/local/nginx/conf
p=$(pidof nginx)
kill $p
/usr/local/nginx/sbin/nginx -t
/usr/local/nginx/sbin/nginx
