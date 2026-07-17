[app]

title = WalletCore

package.name = walletcore
package.domain = com.develop4world

source.dir = .

source.include_exts = py,png,jpg,jpeg,kv,json,atlas,ttf,db

version = 1.0.0

requirements = python3==3.11.9,kivy==2.3.1,requests

orientation = portrait

fullscreen = 0

icon.filename = assets/icon.png


# Android
android.api = 34
android.build_tools_version = 34.0.0
android.minapi = 24

android.ndk = 25c

android.archs = arm64-v8a

android.enable_androidx = True

android.private_storage = True

android.allow_backup = True


# Python for Android
p4a.branch = master


[buildozer]

log_level = 2
warn_on_root = 0
