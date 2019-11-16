#!/bin/bash

vmname=$1
# vboxmanage list ostypes
ostype=Windows2016_64

vboxmanage createvm --name "${vmname}" --ostype "$ostype" --register
vboxmanage modifyvm "${vmname}" --cpus 6 --memory 16000
vboxmanage modifyvm "${vmname}" --accelerate2dvideo on
vboxmanage modifyvm "${vmname}" --vrde on --vrdeauthtype=null --vrdeaddress=127.0.0.1 --vrdeport=3391
vboxmanage storagectl "${vmname}" --name 'SATA Controller' --add sata
vboxmanage modifyvm "${vmname}" --nic1 hostonly
vboxmanage modifyvm "${vmname}" --hostonlyadapter1 vboxnet0
vboxmanage modifyvm "${vmname}" --audio none

vboxmanage createmedium disk --filename /root/VirtualBox\ VMs/"${vmname}"/"${vmname}".vdi --format vdi  --size $((1024*50))
vboxmanage list hdds
vboxmanage storageattach  "${vmname}" --storagectl 'SATA Controller' --port 0 --medium UUID  --type hdd
