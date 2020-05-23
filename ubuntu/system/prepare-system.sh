#!/bin/bash

apt update;
# todo: use ansible
apt install -y ansible

apt install -y vim tmux screen mc build-essential terminator git
apt install -y pass
# remove snapd
apt purge -y snapd gnome-software-plugin-snap
# remove spyware
apt purge -y ubuntu-report popularity-contest apport whoopsie

apt install -y atop

systemctl stop atop atopacct
systemctl mask atop atopacct
rm /etc/cron.d/atop


cp "$(dirname $0)/etc/vim/*" "/etc/vim/"
mv "/root/.bashrc" "/root/.bashrc-$(date +%s)"
cp "$(dirname $0)/root/bashrc" "/root/.bashrc"
