#!/bin/bash

url=$1
bytes=$2

if [ -z $bytes ]; then
    bytes=1024
fi
CURL="curl -ks"

$CURL -H "Range:  bytes=-$bytes" $url

old_position=$($CURL -I $url | grep 'Content-Length:' | awk '{print 0+$NF}')

while true; do
  new_position=$($CURL -I $url | grep 'Content-Length:' | awk '{print 0+$NF}')
  if [ $old_position -ne $new_position ]; then
    curl -s -H "Range:  bytes=$old_position-$new_position" $url
    old_position=$new_position
  fi
  sleep 1;
done

