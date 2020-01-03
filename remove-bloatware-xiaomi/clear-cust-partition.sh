#!/bin/bash

set +e 
cust=$1
echo 'this script will remove all apk files from cust (used for preinstall apps after hard reset)'
echo 'ctrl+c to abort, enter to continue'
read

cd "$(dirname $cust)"
echo 'converting cust'
echo 'simg2img cust.img cust.raw'
simg2img cust.img cust.raw

echo 'moving original cust'
echo "mv cust.img cust.img.$(date +%s)"
mv cust.img cust.img.$(date +%s)

echo 'creating directory'
echo 'sudo mkdir -p /mnt/lavender/cust && \
    sudo mount cust.raw /mnt/lavender/cust && \
    cd /mnt/lavender/cust'

sudo mkdir -p /mnt/lavender/cust && \
    sudo mount cust.raw /mnt/lavender/cust && \
    cd /mnt/lavender/cust

echo ' rm all apk'
echo "find -iname '*.apk' -delete"
find -iname '*.apk'
echo 'this apks will be removed. Enter to continue'
read

find -iname '*.apk' -delete
echo 'truncating *app_applist'

find -iname '*app_applist'
echo 'press enter'
read
find -iname '*app_applist' -exec truncate -s 0 {} \;

echo 'remove *.sig'
find -iname '*.sig'
echo 'press enter'
read

find -iname '*.sig' -delete

echo 'truncating sign_customized_applist'
find -iname sign_customized_applist
echo 'press enter'
read
find -iname sign_customized_applist -exec truncate -s 0 {} \;

cd -

sudo umount /mnt/lavender/cust
echo 'packing cust back'
echo 'ext2simg cust.raw cust.img'
ext2simg cust.raw cust.img

