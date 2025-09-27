[app]
version = 1.0.0
title = JirkaKara
package.name = jirka_kara
package.domain = org.example
source.dir = .
source.include_exts = py,png,jpg,jpeg,mp3,wav,ogg,mpeg
fullscreen = 1
orientation = landscape
requirements = python3, kivy==2.3.0, pyjnius==1.6.1, cython<3
source = start_squat.png,start_bed.png,start_jail.png,stranskej.png,goal_cil.png, WhatsApp Audio 2025-09-26 at 15.13.18.mpeg, fail1.mpeg, fail2.mpeg, fail3.mpeg

[buildozer]
log_level = 2
warn_on_root = 0

[android]
# minimal
android.numeric_version = 10000   # 1*10000 + 0*100 + 0
android.api = 35
android.minapi = 24
android.archs = arm64-v8a, armeabi-v7a
android.gradle_dependencies = "com.android.support:multidex:1.0.3"
android.ndk_api = 21
android.ndk_path = /home/runner/.buildozer/android/platform/android-ndk-r25b


[logcat]
filters = *:S python:D
