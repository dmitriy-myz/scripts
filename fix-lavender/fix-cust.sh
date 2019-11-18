#!/bin/bash



echo 'run simg2img cust.img cust.raw'
echo 'mkdir -p /mnt/lavender/cust && mount mount cust.raw /mnt/lavender/cust && cd /mnt/lavender/cust'


exit 0

find -iname '*app_applist' -exec bash -c 'echo -n > {}' \;
find -iname '*.sig' -delete
find -iname sign_customized_applist -exec bash -c 'echo -n > {}' \;
echo 'remove all apk files'
umount /mnt/lavender/cust
echo 'run ext2simg cust.raw cust_new.img'
