#!/bin/bash


echo |  openssl s_client -connect $1 > /dev/null 2>&1

if [ $? -ne 0 ]; then
    echo "$1 bad ssl"
    exit
fi

echo | \
  openssl s_client -connect $1 2> /dev/null | \
  openssl x509 -noout -checkend 864000 # -dates

if [ $? -eq 1 ]; then
   echo  "$1 ssl expired";
fi;
