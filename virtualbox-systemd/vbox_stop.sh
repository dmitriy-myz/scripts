#!/bin/bash 

UUID="$1"


nVM=$(/usr/bin/vboxmanage list runningvms | grep -c "${UUID}")

while [ ${nVM} -ne 0 ]; do
	/usr/bin/vboxmanage controlvm "${UUID}" acpipowerbutton
    nVM=$(/usr/bin/vboxmanage list runningvms | grep -c "${UUID}")
    sleep 1;
done
exit 0

