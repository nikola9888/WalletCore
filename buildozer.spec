[app]

title = WalletCore

package.name = walletcore

package.domain = com.develop4world

source.dir = .

source.include_exts = py,png,jpg,jpeg,kv,atlas,json

version = 1.0.0

icon.filename = assets/icon.png

orientation = portrait

fullscreen = 0

requirements = python3,kivy

android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

android.api = 35

android.minapi = 24

android.ndk = 25b

android.archs = arm64-v8a,armeabi-v7a

android.allow_backup = True

android.private_storage = True

android.enable_androidx = True

android.copy_libs = 1


[buildozer]

log_level = 2

warn_on_root = 1

exclude_dirs = .git,.github,__pycache__,.buildozer
