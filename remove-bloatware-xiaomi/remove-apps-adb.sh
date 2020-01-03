#!/bin/bash


function uninstall_app() {
    app=$1
    echo "removing $app"
    adb shell pm uninstall $app
    adb shell pm uninstall --user 0 $app
    echo "done"

}
adb devices
read

for apps in "package:com.facebook.appmanager

