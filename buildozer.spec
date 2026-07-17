[app]

title = WalletCore

package.name = walletcore
package.domain = com.develop4world

source.dir = .

source.include_exts = py,png,jpg,jpeg,kv,json,atlas,ttf,db

version = 1.0.0

requirements = python3,kivy,requests

orientation = portrait

fullscreen = 0

icon.filename = assets/icon.png

android.minapi = 24

android.archs = arm64-v8a

android.enable_androidx = True

android.private_storage = True
android.allow_backup = True


[buildozer]

log_level = 2
warn_on_root = 0
