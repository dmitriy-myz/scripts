#!/bin/bash

set +e
userdata=$1
echo 'this script will remove all apk files from userdata (used for preinstall apps after hard reset)'
echo 'ctrl+c to abort, enter to continue'

read

cd "$(dirname $userdata)"
echo 'converting userdata'
echo 'simg2img userdata.img userdata.raw'

simg2img userdata.img userdata.raw
echo 'moving original userdata'
echo "mv userdata.img userdata.img.$(date +%s)"
mv userdata.img userdata.img.$(date +%s)
echo 'creating directory'
echo 'sudo mkdir -p /mnt/lavender/userdata && \
    sudo mount userdata.raw /mnt/lavender/userdata && \
    cd /mnt/lavender/userdata'

sudo mkdir -p /mnt/lavender/userdata && \
    sudo mount userdata.raw /mnt/lavender/userdata && \
    cd /mnt/lavender/userdata

echo ' rm all apk'
echo "find -iname '*.apk' -delete"
find -iname '*.apk'
echo 'this apks will be removed. Enter to continue'
read

find -iname '*.apk' -delete

cd -

sudo umount /mnt/lavender/userdata
echo 'packing userdata back'
echo 'ext2simg userdata.raw userdata.img'
ext2simg userdata.raw userdata.img

