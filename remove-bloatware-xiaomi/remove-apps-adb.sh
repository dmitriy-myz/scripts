#!/bin/bash


function uninstall_app() {
    app=$1
    echo "removing $app"
    adb shell pm uninstall $app
    adb shell pm uninstall --user 0 $app
    echo "done"

}
adb devices
apps=(
    com.facebook.services
    com.facebook.system
    com.facebook.appmanager

    com.google.android.marvin.talkback
    com.google.android.apps.tachyon
    com.google.android.videos
    com.google.android.music
    com.google.android.apps.photos


    com.miui.bugreport
    com.xiaomi.joyose
    com.android.wallpaperbackup
    com.miui.cloudservice.sysbase


    com.xiaomi.miplay_client
    cn.wps.xiaomi.abroad.lite
    com.xiaomi.micloud.sdk
    com.xiaomi.xmsf
    com.xiaomi.payment
    com.xiaomi.mirecycle
    com.xiaomi.powerchecker
    com.xiaomi.glgm
    com.xiaomi.mipicks
    com.xiaomi.midrop
    com.xiaomi.providers.appindex
    com.xiaomi.discover
    com.xiaomi.mi_connect_service

    )

echo 'can be deleted:
    com.qualcomm.wfd.service wifi direct
    com.miui.securitycore second space
    com.qti.dpmserviceapp drm
    com.miui.cleanmaster


'

echo "removing ${apps[*]}"
echo "press enter"
read



for i in ${apps[*]}; do
    echo uninstall_app $i
    uninstall_app $i
done

