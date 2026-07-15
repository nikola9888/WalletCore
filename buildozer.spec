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


requirements = python3,kivy,appdirs


android.permissions = INTERNET

android.api = 35
android.minapi = 24

android.ndk = 27c

android.archs = arm64-v8a,armeabi-v7a

android.allow_backup = True

android.private_storage = True

android.enable_androidx = True


[buildozer]

log_level = 2
warn_on_root = 1
