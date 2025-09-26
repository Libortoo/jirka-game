[app]
title = JirkaKara
package.name = jirka_kara
package.domain = org.example
version = 1.0.0
source.dir = .
source.include_exts = py,png,jpg,jpeg,mp3,wav,ogg,mpeg
fullscreen = 0
orientation = landscape
requirements = python3,kivy
# if you need audio codecs, add: ffpyplayer (and set kivy options accordingly)
# requirements = python3,kivy,ffpyplayer

# Assets to include (place in same directory):
# start_squat.png,start_bed.png,start_jail.png,stranskej.png,goal_cil.png
# WhatsApp Audio 2025-09-26 at 15.13.18.mpeg, fail1.mpeg, fail2.mpeg, fail3.mpeg

[buildozer]
log_level = 2
warn_on_root = 0

[android]
# minimal
android.api = 35
android.minapi = 24
android.archs = arm64-v8a, armeabi-v7a
# if using ffpyplayer: android.gradle_dependencies = "com.android.support:multidex:1.0.3"

[logcat]
filters = *:S python:D
