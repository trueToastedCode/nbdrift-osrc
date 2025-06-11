#!/bin/bash

build_dir="build"

adb uninstall com.ninebot.segway || true
adb install-multiple $(find $build_dir/apks -maxdepth 1 -type f -name "*_signed.apk")
