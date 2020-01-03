#!/bin/bash



echo 'run simg2img system.img system.raw'
echo 'mkdir -p /mnt/lavender/system && \
    mount mount system.raw /mnt/lavender/system && cd /mnt/lavender/system'


exit 0

rm -r ./system/priv-app/facebook-services ./system/priv-app/facebook-installer ./system/app/facebook-appmanager

umount /mnt/lavender/system
echo 'run ext2simg system.raw system_new.img'


