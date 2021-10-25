#!/bin/bash

echo 'this will produce unbootable system.img, trying to fix that'

echo 'run simg2img system.img system.raw'
echo 'mkdir -p /mnt/lavender/system && \
    mount mount system.raw /mnt/lavender/system && cd /mnt/lavender/system'


exit 0

rm -r ./system/priv-app/facebook-services ./system/priv-app/facebook-installer ./system/app/facebook-appmanager
for i in $( echo '
Chrome
Duo
Drive
Gmail2
GoogleTTS

YouDaoEngine
BugReport
CloudService

IdMipay
InMipay
Joyose
KSICibaEngine
TranslationService
talkback

' | tr -s '\n'
) do; 
echo $i
done

umount /mnt/lavender/system
echo 'run ext2simg system.raw system_new.img'

exit 0
unknown:
AutoRegistration (Qualcom)

ConferenceDialer
FileExplorer_old
