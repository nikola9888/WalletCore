[app]

title = WalletCore

package.name = walletcore
package.domain = com.develop4world

source.dir = .

source.include_exts = py,kv,png,jpg,jpeg,json,db,ttf,atlas

version = 1.0.0

requirements = python3,kivy,requests

orientation = portrait

fullscreen = 0

icon.filename = assets/icon.png


android.api = 34
android.minapi = 24

android.archs = arm64-v8a

android.enable_androidx = True

android.private_storage = True

android.allow_backup = True


[buildozer]

log_level = 2
warn_on_root = 0
