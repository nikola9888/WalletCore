[app]

title = WalletCore

package.name = walletcore
package.domain = com.develop4world

source.dir = .

source.include_exts = py,png,jpg,jpeg,kv,json,atlas,ttf

version = 1.0.0

requirements = python3,kivy

orientation = portrait
fullscreen = 0

icon.filename = assets/icon.png

android.permissions = INTERNET

android.api = 35
android.minapi = 24

android.ndk = 25b

android.archs = arm64-v8a

android.enable_androidx = True

android.private_storage = True

android.allow_backup = True

build_dir = .buildozer

p4a.branch = master


[buildozer]

log_level = 2
warn_on_root = 0
