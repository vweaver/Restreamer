#!/usr/bin/env bash

apt-get update 
# apt-get upgrade -y

mkdir -p /nginx/hls
chown -R www-data:www-data /nginx
cd /nginx

git clone https://github.com/sergey-dryabzhinsky/nginx-rtmp-module.git
apt-get install build-essential libpcre3 libpcre3-dev libssl-dev zlib1g zlib1g-dev -y

wget http://nginx.org/download/nginx-1.16.1.tar.gz
tar -xf nginx-1.16.1.tar.gz
rm nginx-1.16.1.tar.gz
cd nginx-1.16.1

./configure --with-http_ssl_module --add-module=../nginx-rtmp-module
make -j 8 
cp -r /nginx /vagrant

