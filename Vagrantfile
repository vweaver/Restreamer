# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|

  config.vm.box = "hashicorp/bionic64"
  config.vm.provision :shell, path: "bootstrap.sh" 
  config.vm.provision :shell, path: "server_start.sh", run: 'always'

  # config.vm.network "public_network", :bridge => "wlan0", :ip => "10.1.10.234"
  config.vm.network "public_network", :bridge => "wlan0", :ip => "192.168.1.234"

  config.vm.synced_folder ".", "/vagrant", disabled: false

end
