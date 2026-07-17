[app]

title = WalletCore

package.name = walletcore
package.domain = com.develop4world

source.dir = .

source.include_exts = py,png,jpg,jpeg,kv,json,atlas,ttf,db

version = 1.0.0

requirements = python3,kivy==2.3.1,requests

# Python for Android
p4a.branch = master
p4a.python_version = 3.11


orientation = portrait

fullscreen = 0

icon.filename = assets/icon.png


# Android
android.api = 33
android.minapi = 24

android.ndk = 25c

android.archs = arm64-v8a

android.enable_androidx = True

android.private_storage = True

android.allow_backup = True


# Permissions (dodaj po potrebi)
# android.permissions = INTERNET


[buildozer]

log_level = 2

warn_on_root = 0
