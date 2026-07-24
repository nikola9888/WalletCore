[app]

title = WalletCore

package.name = walletcore
package.domain = com.develop4world

source.dir = .

source.include_exts = py,png,jpg,jpeg,kv,json,atlas,ttf,db

version = 1.1.0

requirements = python3,kivy,requests

# Python for Android
p4a.branch = master
p4a.python_version = 3.10


orientation = portrait

fullscreen = 1

icon.filename = assets/icon.png


# Android
android.api = 33
android.minapi = 24
android.build_tools_version = 35.0.0
android.accept_sdk_license = True

android.ndk = 25c

android.archs = arm64-v8a
android.release_artifact = aab


android.enable_androidx = True

android.private_storage = True

android.allow_backup = True


# Permissions (dodaj po potrebi)
# android.permissions = INTERNET


[buildozer]

log_level = 2

warn_on_root = 0
