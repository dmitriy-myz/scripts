#!/bin/bash

# login screen in gdm3
sudo cp ~/.config/monitors.xml /var/lib/gdm3/.config/
sudo chown gdm: /var/lib/gdm3/.config/monitors.xml
# new users
sudo mkdir -p /etc/skel/.config
sudo cp ~/.config/monitors.xml /etc/skel/.config/
