#!/bin/bash
vboxmanage  extpack install Oracle_VM_VirtualBox_Extension_Pack-6.0.14.vbox-extpack
vboxmanage hostonlyif create
vboxmanage hostonlyif  ipconfig  --ip 10.40.0.1 vboxnet0
